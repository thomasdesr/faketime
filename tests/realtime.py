from contextlib import contextmanager
from time import perf_counter


@contextmanager
def must_complete_quickly():
    start = perf_counter()

    yield

    end = perf_counter()

    assert end - start < 1, (
        "Shouldn't have taken more than one second of real time to complete under faketime"
    )
