"""REST / HTML client handling, including lichessStream base class."""

import io
import os
import json
import gzip
import itertools
import logging
from uuid import uuid4
from datetime import datetime
from typing import (
    Any,
    Generator,
    Iterable,
    Iterator,
    Mapping,
    TypeVar,
    Optional,
    Tuple,
    List,
    Dict,
)

import chess.pgn
import wget
import zstandard

from singer_sdk.helpers._batch import (
    BaseBatchFileEncoding,
    BatchConfig,
)
from singer_sdk.streams import Stream

logger = logging.getLogger(__name__)

FactoryType = TypeVar("FactoryType", bound="Stream")
_T = TypeVar("_T")


BATCH_SIZE = 100000 # TODO: make it a config


def lazy_chunked_generator(
    iterable: Iterable[_T],
    chunk_size: int,
) -> Generator[Iterator[_T], None, None]:
    """Yield a generator for each chunk of the given iterable.

    Args:
        iterable: The iterable to chunk.
        chunk_size: The size of each chunk.

    Yields:
        A generator for each chunk of the given iterable.
    """
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, chunk_size))
        if not chunk:
            break
        yield iter(chunk)


class LichessStream(Stream):
    """lichess stream class.

    Extracting archived games from https://database.lichess.org
    """

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """

        logger.info("Downloading file ...")
        file_path = self.get_archive_pgn(self.config["api_url"])

        with open(file_path, "rb") as fh:
            dctx = zstandard.ZstdDecompressor()
            stream_reader = dctx.stream_reader(fh, read_size=8192)
            text_stream = io.TextIOWrapper(stream_reader, encoding="utf-8")
            while True:
                # parse game header
                game_header = chess.pgn.read_headers(text_stream)

                # game = chess.pgn.read_game(text_stream) # TODO: parse game

                if not game_header:
                    break
                yield dict(game_header)

    def get_batch_config(self, config: Mapping) -> BatchConfig:
        """Return the batch config for this stream.

        Args:
            config: Tap configuration dictionary.

        Returns:
            Batch config for this stream.
        """
        raw = self.config.get("batch_config")
        return BatchConfig.from_dict(raw) if raw else None

    def get_batches(
        self, batch_config: BatchConfig, context: Optional[dict] = None
    ) -> Iterable[Tuple[BaseBatchFileEncoding, List[str]]]:
        """Return a generator of batch-type dictionary objects encoded in ND-JSON.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.

        Yields:
            A tuple of (encoding, manifest) for each batch.
        """
        # TODO: cleanup batches from previous operation(s)

        param = None
        if self.config["start_date"]:
            dt = datetime.strptime(self.config["start_date"], "%Y.%m.%d")
            param = dt.strftime("%Y%m%d")

        sync_id = f"{self.tap_name}--{self.name}-{uuid4()}-{param}"
        prefix = batch_config.storage.prefix or ""

        try:
            for i, chunk in enumerate(
                lazy_chunked_generator(
                    self._sync_records(context, write_messages=False),
                    BATCH_SIZE,
                ),
                start=1,
            ):
                filename = f"{prefix}{sync_id}__{i}.json.gz"
                with batch_config.storage.fs() as fs:
                    with fs.open(filename, "wb") as f:
                        with gzip.GzipFile(fileobj=f, mode="wb") as gz:
                            gz.writelines(
                                (json.dumps(record) + "\n").encode() for record in chunk
                            )

                    file_url = fs.geturl(filename)

                yield batch_config.encoding, [file_url]
        except Exception as ex:
            logger.error(ex)
            raise
        # finally: # TODO: clean up data/

    def get_url_params(self) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if self.config["is_streaming_archived_pgn"]:
            if self.config["variant"]:
                params["variant"] = self.config["variant"]
            if self.config["start_date"]:
                dt = datetime.strptime(self.config["start_date"], "%Y.%m.%d")
                params["date"] = dt.strftime("%Y-%m")
        return params

    def get_archive_pgn(self, endpoint: str) -> str:
        """WGET remote file and return local file name."""
        url_param = self.get_url_params()
        abs_local_path = os.path.abspath(
            f"data/lichess_db_{url_param['variant']}_rated_{url_param['date']}.pgn.zst"
        )
        url = f"{endpoint}/{url_param['variant']}/lichess_db_{url_param['variant']}_rated_{url_param['date']}.pgn.zst"

        return (
            abs_local_path
            if os.path.exists(abs_local_path)
            else wget.download(url, "data/archive/")
        )
