
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
        self._queue: list = []
        self._unacked: dict = {}
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)
        self._counter = 0

    def put(self, message: Any, timeout: Optional[float] = None) -> str:
        receipt = str(uuid.uuid4())
        with self._not_full:
            if len(self._queue) + len(self._unacked) >= self._capacity:
                if not self._not_full.wait_for(
                    lambda: len(self._queue) + len(self._unacked) < self._capacity,
                    timeout=timeout
                ):
                    raise QueueFull(
                        f"TaskQueue at capacity ({self._capacity})"
                    )
            self._counter += 1
            entry = (self._counter, receipt, message)
            # Insert maintaining sorted order by counter for deterministic FIFO
            lo, hi = 0, len(self._queue)
            while lo < hi:
                mid = (lo + hi) // 2
                if self._queue[mid][0] < entry[0]:
                    lo = mid + 1
                else:
                    hi = mid
            self._queue.insert(lo, entry)
            self._not_empty.notify()
        return receipt

    def get(self, timeout: Optional[float] = None) -> Optional[Tuple[str, Any]]:
        with self._not_empty:
            if not self._queue:
                if not self._not_empty.wait_for(lambda: bool(self._queue), timeout=timeout):
                    return None
            entry = self._queue.pop(0)
            _, receipt, message = entry
            self._unacked[receipt] = entry
            self._not_full.notify()
            return (receipt, message)

    def acknowledge(self, receipt: str) -> None:
        with self._lock:
            if receipt in self._unacked:
                del self._unacked[receipt]

    def nack(self, receipt: str) -> None:
        with self._not_empty:
            if receipt in self._unacked:
                entry = self._unacked.pop(receipt)
                lo, hi = 0, len(self._queue)
                while lo < hi:
                    mid = (lo + hi) // 2
                    if self._queue[mid][0] < entry[0]:
                        lo = mid + 1
                    else:
                        hi = mid
                self._queue.insert(lo, entry)
                self._not_empty.notify()

    def size(self) -> int:
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        with self._lock:
            return len(self._queue) == 0

    def is_full(self) -> bool:
        with self._lock:
            return len(self._queue) + len(self._unacked) >= self._capacity
