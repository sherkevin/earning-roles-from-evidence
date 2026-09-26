"""Consumer interface for the task queue.

This consumer uses an acknowledgment pattern — it calls get() to receive
a (message, receipt) tuple, processes the message, and then calls ack(receipt)
on success or nack(receipt) on failure to re-queue the message.
"""
import threading
import time
from typing import Any, Callable, Optional

from mqueue.queue import TaskQueue


class TaskConsumer:
    """
    Consumes tasks from a TaskQueue.

    Uses the ack/nack pattern: messages are only confirmed-delivered
    when ack(receipt) is called after successful processing.
    If the handler raises, nack(receipt) is called to re-queue the message.
    """

    def __init__(
        self,
        queue: TaskQueue,
        handler: Callable[[Any], None],
        consumer_id: int = 0,
    ):
        self._queue = queue
        self._handler = handler
        self._consumer_id = consumer_id
        self._processed: list = []
        self._lock = threading.Lock()
        self._running = False

    def run_once(self) -> bool:
        """
        Process one task from the queue.

        Returns True if a task was processed, False if the queue was empty.
        """
        result = self._queue.get()
        if result is None:
            return False
        message, receipt = result
        try:
            self._handler(message)
            self._queue.ack(receipt)
            with self._lock:
                self._processed.append(message)
            return True
        except Exception:
            self._queue.nack(receipt)
            raise

    def run_until_empty(self, max_idle_cycles: int = 10) -> None:
        """Drain the queue, stopping after max_idle_cycles consecutive empty polls."""
        idle = 0
        while idle < max_idle_cycles:
            if self.run_once():
                idle = 0
            else:
                idle += 1
                time.sleep(0.001)

    @property
    def processed_count(self) -> int:
        return len(self._processed)

    @property
    def processed_messages(self) -> list:
        with self._lock:
            return list(self._processed)
