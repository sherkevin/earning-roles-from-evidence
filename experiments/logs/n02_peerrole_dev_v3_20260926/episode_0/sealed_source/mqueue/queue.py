"""
Task message queue with acknowledgment support.
"""
import threading
import uuid
from collections import deque
from typing import Any, Optional, Tuple


class QueueFull(Exception):
    """Raised when the queue has reached its capacity."""


class QueueEmpty(Exception):
    """Raised when the queue is empty."""


class TaskQueue:
    """Thread-safe task queue with configurable capacity and ack/nack support."""

    def __init__(self, capacity: int = 500):
        self._capacity = capacity
        self._queue: deque = deque()
        self._in_flight: dict = {}
        self._lock = threading.Lock()

    def put(self, message: Any) -> None:
        """
        Enqueue a task message.

        Raises QueueFull if the queue is at capacity.
        The capacity check and append are performed atomically under the lock.
        """
        with self._lock:
            if len(self._queue) + len(self._in_flight) >= self._capacity:
                raise QueueFull(
                    f"TaskQueue at capacity ({self._capacity})"
                )
            self._queue.append(message)

    def get(self) -> Optional[Tuple[Any, str]]:
        """
        Dequeue and return the next task message along with a receipt token,
        or None if empty.

        The message is moved to an in-flight dictionary and is only permanently
        removed when ack(receipt) is called. If the consumer crashes, nack(receipt)
        can be used to re-queue the message.
        """
        with self._lock:
            if not self._queue:
                return None
            message = self._queue.popleft()
            receipt = str(uuid.uuid4())
            self._in_flight[receipt] = message
            return (message, receipt)

    def ack(self, receipt: str) -> None:
        """
        Acknowledge successful processing of a message.
        Removes the message from the in-flight dictionary permanently.
        """
        with self._lock:
            self._in_flight.pop(receipt, None)

    def nack(self, receipt: str) -> None:
        """
        Negative-acknowledge a message (processing failed).
        Returns the message to the front of the queue for redelivery.
        """
        with self._lock:
            message = self._in_flight.pop(receipt, None)
            if message is not None:
                self._queue.appendleft(message)

    def size(self) -> int:
        """Return the current number of tasks in the queue (not including in-flight)."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Return True if the queue has no tasks waiting."""
        with self._lock:
            return len(self._queue) == 0

    def is_full(self) -> bool:
        """Return True if the queue is at capacity."""
        with self._lock:
            return len(self._queue) + len(self._in_flight) >= self._capacity
