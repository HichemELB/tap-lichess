"""REST / HTML client handling, including lichessStream base class."""

import io
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, Optional

import chess.pgn
import wget
import zstandard
from singer_sdk.streams import Stream


class LichessStream(Stream):
    """lichess stream class.

    Streaming data from API endpoints "https://lichess.org/api"
    Streaming archived games from https://database.lichess.org
    """

    # OR use a dynamic url_base:
    # @property
    # def url_base(self) -> str:
    #     """Return the API URL root, configurable via tap settings."""
    #     return self.config["api_url"]

    # records_jsonpath = "$[*]"  # Or override `parse_response`.
    # next_page_token_jsonpath = "$.next_page"  # Or override `get_next_page_token`.

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        headers["Private-Token"] = self.config.get("auth_token")
        return headers

    # def get_next_page_token(
    #     self, response: requests.Response, previous_token: Optional[Any]
    # ) -> Optional[Any]:
    #     """
    #     Return a token for identifying next page or None if no more pages.
    #     """
    #     # TODO: If pagination is required, return a token which can be used to get the
    #     #       next page. If this is the final page, return "None" to end the
    #     #       pagination loop.
    #     if self.next_page_token_jsonpath:
    #         all_matches = extract_jsonpath(
    #             self.next_page_token_jsonpath, response.json()
    #         )
    #         first_match = next(iter(all_matches), None)
    #         next_page_token = first_match
    #     else:
    #         next_page_token = response.headers.get("X-Next-Page", None)
    #
    #     return next_page_token

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        file_path = self.get_archive_pgn(self.config["api_url"])
        with open(file_path, "rb") as fh:
            dctx = zstandard.ZstdDecompressor()
            stream_reader = dctx.stream_reader(fh, read_size=10485760)  # 10MB
            text_stream = io.TextIOWrapper(stream_reader, encoding="utf-8")
            while True:
                header = chess.pgn.read_headers(text_stream)
                # TODO: parse game
                # game = chess.pgn.read_game(text_stream)
                if header is None:
                    break
                yield dict(header)

    def get_url_params(self) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if self.config["is_streaming_archived_pgn"]:
            if self.config["variant"]:
                params["variant"] = self.config["variant"]
            if self.config["start_date"]:
                dt = datetime.strptime(
                    self.config["start_date"], "%Y-%m-%d"
                ) + timedelta(days=7)
                params["date"] = dt.strftime("%Y-%m")
        # else:
        #     if next_page_token:
        #         params["page"] = next_page_token
        #     if self.replication_key:
        #         params["sort"] = "asc"
        #         params["order_by"] = self.replication_key
        return params

    def get_archive_pgn(self, endpoint: str) -> str:
        """WGET remote file and return local file name."""
        url_param = self.get_url_params()
        url = f"{endpoint}/{url_param['variant']}/lichess_db_{url_param['variant']}_rated_{url_param['date']}.pgn.zst"
        return wget.download(url, "data/")
        # TODO: clean up data/

    # def parse_api_streaming_response(self, response: requests.Response) -> Iterable[dict]:
    #     """
    #     Parse the response and return an iterator of result records when streaming from API.
    #     """
    #     # TODO: Parse response body and return a set of records when streaming from API.
    #     yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    # def post_api_streaming_response(self, row: dict, context: Optional[dict]) -> dict:
    #     """
    #     As needed, append or transform raw data to match expected structure.
    #     """
    #     return row
