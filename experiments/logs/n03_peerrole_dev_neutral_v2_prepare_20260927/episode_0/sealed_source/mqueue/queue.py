
import threading
import uuid
from collections import deque
from typing import Any, Optional, Tuple


class QueueFull(Exception):
    pass


class QueueEmpty(Exception):
    pass


class TaskQueue:

    def __init__(self, capacity: int = 500):
        self._capacity = capacity
        self._queue: deque = deque()
        self._in_flight: dict = {}
        self._lock = threading.Lock()

    def put(self, message: Any) -> None:
        with self._lock:
            if len(self._queue) + len(self._in_flight) >= self._capacity:
                raise QueueFull(
                    f"TaskQueue at capacity ({self._capacity})"
                )
            self._queue.append(message)

    def get(self) -> Optional[Any]:
        with self._lock:
            if not self._queue:
                return None
            message = self._queue.popleft()
            receipt = str(uuid.uuid4())
            self._in_flight[receipt] = message
            return (message, receipt)

    def ack(self, receipt: Any) -> None:
        with self._lock:
            if receipt in self._in_flight:
                del self._in_flight[receipt]

    def nack(self, receipt: Any) -> None:
        with self._lock:
            if receipt in self._in_flight:
                message = self._in_flight.pop(receipt)
                self._queue.append(message)

    def size(self) -> int:
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        with self._lock:
            return len(self._queue) == 0

    def is_full(self) -> bool:
        with self._lock:
            return len(self._queue) + len(self._in_flight) >= self._capacity
