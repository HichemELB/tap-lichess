"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_standard_tap_tests

from tap_lichess.tap import Taplichess

SAMPLE_CONFIG = {
    "start_date": "2013-01-01",
    "api_url": "https://database.lichess.org",
    "is_streaming_archived_pgn": True,
    "variant": "standard",
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(Taplichess, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# TODO: Create additional tests as appropriate.
