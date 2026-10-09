"""Thread-safe task queue with explicit acknowledgement."""

import threading
import uuid
from collections import deque
from typing import Any, Dict, Optional, Tuple


class QueueFull(Exception):
    """Raised when the queue has reached its capacity."""


class QueueEmpty(Exception):
    """Raised when the queue is empty."""


class TaskQueue:
    """Thread-safe FIFO queue with ack/nack receipts."""

    def __init__(self, capacity: int = 500) -> None:
        self._capacity = capacity
        self._queue: deque[Any] = deque()
        self._in_flight: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def put(self, message: Any) -> None:
        """Atomically enqueue a message if capacity is available."""
        with self._lock:
            if len(self._queue) >= self._capacity:
                raise QueueFull(f"TaskQueue at capacity ({self._capacity})")
            self._queue.append(message)

    def get(self) -> Tuple[Optional[Any], Optional[str]]:
        """Return the next message and receipt, or ``(None, None)``."""
        with self._lock:
            if not self._queue:
                return None, None
            message = self._queue.popleft()
            receipt = uuid.uuid4().hex
            self._in_flight[receipt] = message
            return message, receipt

    def ack(self, receipt: str) -> None:
        """Commit a receipt and remove it from the in-flight set."""
        with self._lock:
            self._in_flight.pop(receipt, None)

    def nack(self, receipt: str) -> None:
        """Return an unacknowledged message to the front of the queue."""
        with self._lock:
            if receipt in self._in_flight:
                self._queue.appendleft(self._in_flight.pop(receipt))

    def size(self) -> int:
        """Return the number of queued messages."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Return whether no queued messages remain."""
        with self._lock:
            return not self._queue

    def is_full(self) -> bool:
        """Return whether the queue has reached capacity."""
        with self._lock:
            return len(self._queue) >= self._capacity
