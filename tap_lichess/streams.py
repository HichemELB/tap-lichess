"""Stream type classes for tap-lichess."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_lichess.client import lichessStream

# SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class GameHistoryStream(lichessStream):
    """
    Define custom stream.
    """
    name = "GameHistoryStream"
    path = "/lichess/history"
    primary_keys = None #["Site"]
    replication_key = None #"UTCDate"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "gamehistory.json"
    schema = th.PropertiesList(
        th.Property(
            "Event",
            th.StringType,
            description="The event when the game took place"),
        th.Property(
            "Site",
            th.StringType,
            description="The game's system ID"
        ),
        th.Property(
            "Date",
            th.IntegerType,
            description="Date when the game was played"
        ),
        th.Property(
            "Round",
            th.IntegerType,
            description="If the game is part of a tournament, it is the number of the game in that tournament"
                        "(e.g. game 3 out of 7)"
        ),
        th.Property(
            "White",
            th.IntegerType,
            description="The white player ID"
        ),
        th.Property(
            "Black",
            th.StringType,
            description="The black player ID"
        ),
        th.Property(
            "Result",
            th.StringType,
            description="The game result"),
        th.Property(
            "UTCDate",
            th.StringType,
            description="The date when the game was played, in UTC time zone"),
        th.Property(
            "UTCTime",
            th.StringType,
            description="The time when the game was played, in UTC time zone"),
        th.Property(
            "WhiteElo",
            th.StringType,
            description="Rating of the player with White color."
                        "(Elo is a type of rating used in Chess)"
        ),
        th.Property(
            "BlackElo",
            th.StringType,
            description="Rating of the player with White color"
        ),
        th.Property(
            "WhiteRatingDiff",
            th.StringType,
            description="The difference in rating for the player of the White color after having finished the game "
                        "(positive in case of win, negative in case of loss)"
        ),
        th.Property(
            "BlackRatingDiff",
            th.StringType,
            description="The difference in rating for the player of the Black color after having finished the game "
                        "(positive in case of win, negative in case of loss)"
        ),
        th.Property(
            "WhiteTitle",
            th.StringType,
            description="Optional header, in case the player with White color has a Title "
                        "(like International Master for ex)"
        ),
        th.Property(
            "BlackTitle",
            th.StringType,
            description="Optional header, in case the player with Black color has a Title "
                        "(like International Master for ex)"
        ),
        th.Property(
            "ECO",
            th.StringType,
            description="Code of the opening "
        ),
        th.Property(
            "Opening",
            th.StringType,
            description="The opening that was used for the game (example “Sicilian”)"
        ),
        th.Property(
            "TimeControl",
            th.StringType,
            description="The TimeControl used. There are different possible TimeControl."
                        "For example : '300+0' means : each player has 300 seconds (5 mins) and there is no additional"
                        "time after a move '180+2' means : each player has 180 seconds (3 mins) and there is 2 seconds "
                        "increment after each move"
        ),
        th.Property(
            "Termination",
            th.StringType,
            description="How the game was terminated. Examples: Checkmate, Stalemate, "
                        "Three Fold Repetition, TimeForfeit, …"
        ),
    ).to_dict()


