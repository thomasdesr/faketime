import time

import pytest

from ..realtime import must_complete_quickly


def test_fixture_works(faketime):
    with must_complete_quickly():
        time.sleep(10)
        assert time.monotonic() == pytest.approx(10, rel=0.1), "Fixture didn't work"


def test_frozentime_fixture_works(frozentime):
    with must_complete_quickly():
        time.sleep(10)
        assert time.monotonic() == 10, "Fixture didn't work"
