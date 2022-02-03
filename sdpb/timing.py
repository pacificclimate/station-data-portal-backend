"""
Context manager for timing a block of code (in with statement).
Calls a logging function with timing messages.

Usage:

```
logger = logging.getLogger(__name__)
with timing("description/label", log=logger.debug):
    # Timing start message logged here
    # ... Code to be timed ...
# Timing end message logged here
```
"""
from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timing(
    description,
    log=None,
    multiplier=1000,
    start_message="{description}: start",
    end_message="{description}: elapsed time {elapsed} ms",
):
    start = perf_counter() * multiplier
    if log is not None and start_message is not None:
        log(start_message.format(description=description, start=start))
    yield
    end = perf_counter() * multiplier
    elapsed = end - start
    if log is not None:
        log(
            end_message.format(
                description=description, start=start, end=end, elapsed=elapsed
            )
        )
