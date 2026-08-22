from __future__ import annotations

import os
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class BusyError(RuntimeError):
    """Raised when another classify() call holds the lock past the wait budget."""


_thread_lock = threading.Lock()
_flight_guard = threading.Lock()
_inflight: dict[str, "_Flight"] = {}
_DEFAULT_TIMEOUT = float(os.getenv("CLASSIFY_LOCK_TIMEOUT", "30"))


class _Flight:
    def __init__(self) -> None:
        self.event = threading.Event()
        self.result: dict | None = None
        self.error: BaseException | None = None


def _lock_path() -> Path:
    return Path(os.getenv("CLASSIFY_LOCK_PATH", "/tmp/ticket-classifier.lock"))


def _lock_file(handle, deadline: float) -> None:
    try:
        import fcntl
    except ImportError:
        return
    while True:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except BlockingIOError as exc:
            if time.monotonic() >= deadline:
                raise BusyError("Classifier is busy. Retry in a moment.") from exc
            time.sleep(0.05)


def _unlock_file(handle) -> None:
    try:
        import fcntl
    except ImportError:
        return
    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def classify_lock(*, timeout: float | None = None) -> Iterator[None]:
    """Serialize LLM calls across threads and local processes."""
    seconds = _DEFAULT_TIMEOUT if timeout is None else timeout
    deadline = time.monotonic() + max(0.0, seconds)
    remaining = deadline - time.monotonic()
    if not _thread_lock.acquire(timeout=max(0.0, remaining)):
        raise BusyError("Classifier is busy. Retry in a moment.")
    handle = None
    try:
        path = _lock_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = path.open("a+")
        _lock_file(handle, deadline)
        yield
    finally:
        if handle is not None:
            try:
                _unlock_file(handle)
            finally:
                handle.close()
        _thread_lock.release()


def single_flight(key: str, timeout: float | None = None) -> tuple[_Flight, bool]:
    """Join an in-flight classify for the same text, or become the owner.

    Results are not cached after the flight ends.
    """
    with _flight_guard:
        existing = _inflight.get(key)
        if existing is not None:
            return existing, False
        flight = _Flight()
        _inflight[key] = flight
        return flight, True


def wait_flight(flight: _Flight, timeout: float | None = None) -> dict:
    seconds = _DEFAULT_TIMEOUT if timeout is None else timeout
    if not flight.event.wait(timeout=max(0.0, seconds)):
        raise BusyError("Classifier is busy. Retry in a moment.")
    if flight.error is not None:
        raise flight.error
    if flight.result is None:
        raise BusyError("Classifier is busy. Retry in a moment.")
    return dict(flight.result)


def finish_flight(key: str, flight: _Flight, *, result: dict | None = None, error: BaseException | None = None) -> None:
    flight.result = result
    flight.error = error
    flight.event.set()
    with _flight_guard:
        if _inflight.get(key) is flight:
            del _inflight[key]
