import pytest
from ._faketime import _faketime


@pytest.fixture()
def faketime():
    yield from _faketime()


@pytest.fixture()
def frozentime():
    yield from _faketime(tick=False)
