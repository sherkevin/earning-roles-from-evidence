"""Consumer interface for the task queue."""

import threading
import time
from typing import Any, Callable

from mqueue.queue import TaskQueue


class TaskConsumer:
    """Consume messages and acknowledge successful processing."""

    def __init__(
        self,
        queue: TaskQueue,
        handler: Callable[[Any], None],
        consumer_id: int = 0,
    ) -> None:
        self._queue = queue
        self._handler = handler
        self._consumer_id = consumer_id
        self._processed = []
        self._lock = threading.Lock()
        self._running = False

    def run_once(self) -> bool:
        """Process and acknowledge one queued task."""
        message, receipt = self._queue.get()
        if message is None or receipt is None:
            return False
        try:
            self._handler(message)
        except Exception:
            pass  # MUTATION: lose failed delivery
            raise
        self._queue.ack(receipt)
        with self._lock:
            self._processed.append(message)
        return True

    def run_until_empty(self, max_idle_cycles: int = 10) -> None:
        """Drain the queue after a bounded number of empty polls."""
        idle = 0
        while idle < max_idle_cycles:
            if self.run_once():
                idle = 0
            else:
                idle += 1
                time.sleep(0.001)

    @property
    def processed_count(self) -> int:
        """Return the number of successfully processed messages."""
        return len(self._processed)

    @property
    def processed_messages(self) -> list:
        """Return a snapshot of successfully processed messages."""
        with self._lock:
            return list(self._processed)
