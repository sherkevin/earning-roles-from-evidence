"""
Event message queue with acknowledgment support.
"""
import threading
import uuid
from collections import deque
from typing import Any, Optional, Tuple


class QueueFull(Exception):
    """Raised when the queue has reached its capacity."""


class QueueEmpty(Exception):
    """Raised when the queue is empty."""


class EventQueue:
    """Thread-safe event queue with configurable capacity and ack support."""

    def __init__(self, capacity: int = 1000):
        self._capacity = capacity
        self._queue: deque = deque()
        self._lock = threading.Lock()
        self._in_flight: dict = {}

    def put(self, message: Any) -> None:
        """
        Enqueue an event message atomically.

        Raises QueueFull if the queue is at capacity.
        """
        with self._lock:
            if len(self._queue) >= self._capacity:
                raise QueueFull(
                    f"EventQueue at capacity ({self._capacity})"
                )
            self._queue.append(message)

    def get(self) -> Optional[Tuple[Any, str]]:
        """
        Dequeue the next event message and return (message, receipt).

        The message remains in-flight until ack(receipt) is called.
        Returns None if the queue is empty.
        """
        with self._lock:
            if not self._queue:
                return None
            message = self._queue.popleft()
            receipt = str(uuid.uuid4())
            self._in_flight[receipt] = message
            return message, receipt

    def ack(self, receipt: str) -> None:
        """
        Acknowledge successful processing of a message.

        Removes the message from the in-flight tracking.
        """
        with self._lock:
            self._in_flight.pop(receipt, None)

    def nack(self, receipt: str) -> None:
        """
        Negative-acknowledge a message, re-queuing it for redelivery.
        """
        with self._lock:
            message = self._in_flight.pop(receipt, None)
            if message is not None:
                self._queue.appendleft(message)

    def size(self) -> int:
        """Return the current number of events in the queue."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Return True if the queue has no events waiting."""
        with self._lock:
            return len(self._queue) == 0

    def is_full(self) -> bool:
        """Return True if the queue is at capacity."""
        with self._lock:
            return len(self._queue) >= self._capacity
