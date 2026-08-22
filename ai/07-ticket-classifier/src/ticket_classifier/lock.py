from __future__ import annotations

import os
import time
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class BusyError(RuntimeError):
    """Raised when another classify() call holds the lock past the wait budget."""


_thread_lock = threading.Lock()
_DEFAULT_TIMEOUT = float(os.getenv("CLASSIFY_LOCK_TIMEOUT", "30"))


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
