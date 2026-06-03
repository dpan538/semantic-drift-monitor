import time
from collections.abc import Callable
from typing import TypeVar

from config import MAX_RETRIES, REQUEST_DELAY_SECONDS

T = TypeVar("T")


def polite_retry(call: Callable[[], T], retries: int = MAX_RETRIES, delay: float = REQUEST_DELAY_SECONDS) -> T:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            result = call()
            time.sleep(delay)
            return result
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    if last_error is not None:
        raise last_error
    raise RuntimeError("Retry helper failed without an exception.")

