"""Producer helper for the event queue."""
import threading
import time
from typing import Any

from mqueue.queue import EventQueue, QueueFull


class EventProducer:
    """Sends events to a EventQueue."""

    def __init__(self, queue: EventQueue, producer_id: int):
        self._queue = queue
        self._producer_id = producer_id
        self._sent: list = []
        self._lock = threading.Lock()

    def send(self, payload: Any, retries: int = 3) -> bool:
        """
        Send a event to the queue.

        Returns True on success, False if the queue remained full after retries.
        """
        for attempt in range(retries):
            try:
                self._queue.put(payload)
                with self._lock:
                    self._sent.append(payload)
                return True
            except QueueFull:
                if attempt < retries - 1:
                    time.sleep(0.001 * (attempt + 1))
        return False

    @property
    def sent_count(self) -> int:
        return len(self._sent)

    @property
    def sent_messages(self) -> list:
        with self._lock:
            return list(self._sent)
