"""Stream type classes for tap-lichess."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_lichess.client import lichessStream

# TODO: Delete this is if not using json files for schema definition
# SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class GameHistoryStream(lichessStream):
    """Define custom stream."""
    name = "gamehistory"
    path = "/gamehistory"
    primary_keys = ["Site"]
    replication_key = "UTCDate"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("event", th.StringType),
        th.Property(
            "Site",
            th.StringType,
            description="The game's system ID"
        ),
        th.Property(
            "white",
            th.IntegerType,
            description="The white player ID"
        ),
        th.Property(
            "black",
            th.StringType,
            description="The black player ID"
        ),
        th.Property("result",
                    th.StringType,
                    description="The game result"),
        th.Property("UTCDate",
                    th.StringType,
                    description="The date when the game took place"),
        th.Property("UTCTime",
                    th.StringType,
                    description="The time when the game took place"),
        th.Property(
            "state",
            th.StringType,
            description="State name in ISO 3166-2 format"
        ),
        th.Property("zip", th.StringType),
    ).to_dict()


