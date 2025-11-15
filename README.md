# faketime

Helpful wrapper around
[time-machine](https://github.com/adamchainz/time-machine) that extends its
capabilities to also fake out `time.sleep`, `asyncio.sleep`, and
`time.monotonic`. When you advance time via any of the sleep functions, time
will shift forward without waiting for that time to actually pass.

## _This library may cause you bugs_

Both [time-machine](https://github.com/adamchainz/time-machine) and [freezegun](https://github.com/spulec/freezegun) have deliberately avoided mocking sleep functions and monotonic clocks after encountering significant issues (see below).

That said, it is sometimes _really_ handy to be able to mock out dumb sleeps. So user beware :D

**Why doesn't upstream do this?**

* `time-machine` added monotonic mocking in v2.13.0 and immediately broke asyncio tests, pytest durations, and database drivers ([#387](https://github.com/adamchainz/time-machine/issues/387), [#505](https://github.com/adamchainz/time-machine/issues/505), [#509](https://github.com/adamchainz/time-machine/issues/509)). The maintainer now plans to remove it entirely, stating it was "too brittle and broke many things, like asyncio" ([#560](https://github.com/adamchainz/time-machine/pull/560)).

* `freezegun` mocking `time.monotonic()` causes `asyncio.sleep()` to hang indefinitely ([#290](https://github.com/spulec/freezegun/issues/290), [#437](https://github.com/spulec/freezegun/issues/437), [#383](https://github.com/spulec/freezegun/issues/383)) and can make monotonic time move backwards, violating its core guarantee ([#556](https://github.com/spulec/freezegun/issues/556)).

## Install

```bash
uv pip install faketime
```

## Example

faketime has two modes: `fake` & `frozen`:
* In `fake` mode, "time" still advances naturally in the background.
* In `frozen` it does not and instead advances only when explicitly moved
  forward via an explicit action, such as a `{time,asyncio}.sleep`.

```python
import time
from faketime import faketime, frozentime

with faketime():
    start = time.time()
    time.sleep(10)  # Instantly advance time by t+10 seconds
    elapsed = time.time() - start
    assert elapsed >= 10  # Note: Will be >= because some actual time has also naturally happened


with frozentime():
    start = time.time()
    time.sleep(10)  # Instantly advance time by exactly 10 seconds
    elapsed = time.time() - start
    assert elapsed == 10  # Exactly 10 seconds passed

```


## Pytest

There's also a lightweight set of pytest fixtures you can use to wrap your whole
test suite in fake or frozen time.

```python
from faketime.pytest import *

def test_something(faketime):
    time.sleep(10)  # Instant

def test_frozen(frozentime):
    time.sleep(10)  # Instant, and also frozen
```
