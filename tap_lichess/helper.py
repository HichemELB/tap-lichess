import os

from collections import OrderedDict
import json


USER_AGENT = "Mozilla/5.0 (Macintosh; scitylana.singer.io)"


def get_abs_path(path: str) -> str:
    """
    Returns the absolute path
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def get_game_header(header: OrderedDict) -> dict:
    """
    Read an OrderedDict game header and retrun it as Dict
    """
    return dict(header)

