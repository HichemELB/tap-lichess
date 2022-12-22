"""
lichess tap class.
"""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_lichess.streams import (
    lichessStream,
    GameHistoryStream,
)

STREAM_TYPES = [
    GameHistoryStream,
]


class Taplichess(Tap):
    """
    lichess tap class.
    """
    name = "tap-lichess"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "is_streaming_archived_pgn",
            th.BooleanType,
            required=False,
            default=None,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "auth_token",
            th.StringType,
            required=False,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service"
        ),
        # th.Property(
        #     "project_ids",
        #     th.ArrayType(th.StringType),
        #     required=True,
        #     description="Project IDs to replicate"
        # ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync"
        ),
        th.Property(
            "api_url",
            th.StringType,
            description="The url for the API service"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """
        Return a list of discovered streams.
        """
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    Taplichess.cli()
