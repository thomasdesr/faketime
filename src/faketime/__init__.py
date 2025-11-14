from asyncio import sleep as _original_async_sleep
from contextlib import contextmanager
from dataclasses import dataclass
from unittest import mock

import time_machine


@dataclass
class _ExpandedTimeMachine:
    tt: time_machine.Coordinates

    _highest_monotonic_ns: int = 0
    _previous_monotonic_ns: int = 0

    def sync_sleep(self, seconds) -> None:
        self.tt.shift(seconds)

    async def async_sleep(self, seconds) -> None:
        self.tt.shift(seconds)
        await _original_async_sleep(0)  # Yield control to the event loop

    def monotonic_ns(self) -> int:
        current_time = self.tt.time_ns()

        current_delta = current_time - self._previous_monotonic_ns
        if current_delta > 0:
            self._highest_monotonic_ns = max(
                current_time, self._highest_monotonic_ns + current_delta
            )

        self._previous_monotonic_ns = current_time
        return self._highest_monotonic_ns

    def monotonic(self) -> float:
        return self.monotonic_ns() / time_machine.NANOSECONDS_PER_SECOND


def _faketime(destination: time_machine.DestinationType = 0, *, tick: bool = True):
    with time_machine.travel(destination, tick=tick) as tt:
        et = _ExpandedTimeMachine(tt)

        with (
            mock.patch.multiple(
                "time",
                sleep=et.sync_sleep,
                monotonic=et.monotonic,
                monotonic_ns=et.monotonic_ns,
            ),
            mock.patch("asyncio.sleep", new=et.async_sleep),
            mock.patch(
                "asyncio.BaseEventLoop.time",
                new=et.monotonic,
            ),
        ):
            yield tt


@contextmanager
def faketime(destination: time_machine.DestinationType = 0):
    yield from _faketime(destination)


@contextmanager
def frozentime(destination: time_machine.DestinationType = 0):
    yield from _faketime(destination, tick=False)
