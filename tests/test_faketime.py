import asyncio
import time
from typing import List

from hypothesis import given
from hypothesis.strategies import integers, lists
from time_machine import NANOSECONDS_PER_SECOND

from faketime import faketime, frozentime

from .realtime import must_complete_quickly


def test_time_sleep():
    with must_complete_quickly(), faketime():
        time.sleep(10)


def test_time_sleeps_the_right_amount():
    with must_complete_quickly(), frozentime():
        start = time.time()
        time.sleep(10)
        end = time.time()

        assert end - start == 10, "Time didn't advance while sleeping"


def test_asyncio_sleep():
    async def _test():
        with must_complete_quickly(), faketime():
            await asyncio.sleep(10)

    asyncio.run(_test())


def test_asyncio_call_later():
    async def _test():
        loop = asyncio.get_event_loop()

        has_been_called = False

        def _has_called():
            nonlocal has_been_called
            print("Was called at", loop.time(), "seconds")
            has_been_called = True

        with must_complete_quickly(), faketime():
            loop.call_later(10, _has_called)

            # Wait for up to "100 [simulated] seconds" for the callback to run
            for i in range(100):
                print(i, loop.time())
                await asyncio.sleep(1)

                if has_been_called:
                    # And if it has, break out and finish
                    break
            else:
                raise AssertionError("Call later never called")

    asyncio.run(_test())


def test_asyncio_create_sleepy_task():
    async def _test():
        async def _sleepy_task():
            await asyncio.sleep(10)

        loop = asyncio.get_event_loop()

        with must_complete_quickly(), faketime():
            f = loop.create_task(_sleepy_task())

            for _ in range(100):
                await asyncio.sleep(1)
                if f.done():
                    break
            else:
                raise AssertionError("Task never finished")

    asyncio.run(_test())


@given(lists(integers()))
def test_monotonic_only_goes_forward(intervals):
    monotonic_values = []

    with must_complete_quickly(), faketime() as ft:
        for i in intervals:
            monotonic_values.append(time.monotonic())

            ft.shift(i)

    assert sorted(monotonic_values) == monotonic_values, (
        "Monotonic returned values that went down"
    )


@given(lists(integers()))
def test_monotonic_goes_up_by_the_right_amounts(intervals: List[int]):
    with must_complete_quickly(), frozentime() as ft:
        for shift in intervals:
            before = time.monotonic_ns()
            ft.shift(shift)
            after = time.monotonic_ns()

            if shift < 0:
                assert after == before, (
                    "If shifting back in time, monotonic can't go backwards"
                )
            else:
                assert after - before == shift * NANOSECONDS_PER_SECOND, (
                    f"Time didn't advance by the right amount: {time.time()}"
                )
