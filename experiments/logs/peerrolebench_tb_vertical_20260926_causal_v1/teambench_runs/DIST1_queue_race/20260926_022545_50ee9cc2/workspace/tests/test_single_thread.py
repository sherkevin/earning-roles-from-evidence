"""
Single-threaded tests for the event queue.

These tests pass even with the race condition bugs because they never
exercise concurrent access paths.
"""
import pytest
from mqueue.queue import EventQueue, QueueFull


def test_put_and_get_basic():
    """Basic enqueue/dequeue round-trip."""
    q = EventQueue(capacity=10)
    q.put("event_1")
    q.put("event_2")
    result = q.get()
    # After fix, get() returns (msg, receipt) — handle both
    msg = result[0] if isinstance(result, tuple) else result
    assert msg == "event_1"


def test_queue_empty_returns_none():
    """get() on empty queue returns None (or (None, None) after fix)."""
    q = EventQueue(capacity=10)
    result = q.get()
    if isinstance(result, tuple):
        assert result[0] is None
    else:
        assert result is None


def test_queue_full_raises():
    """put() on a full queue raises QueueFull."""
    q = EventQueue(capacity=3)
    q.put("a")
    q.put("b")
    q.put("c")
    with pytest.raises(QueueFull):
        q.put("d")


def test_size_tracking():
    """size() reflects current queue depth."""
    q = EventQueue(capacity=10)
    assert q.size() == 0
    q.put("x")
    assert q.size() == 1
    q.put("y")
    assert q.size() == 2


def test_is_empty_and_is_full():
    """is_empty() and is_full() return correct values."""
    q = EventQueue(capacity=2)
    assert q.is_empty()
    assert not q.is_full()
    q.put("a")
    assert not q.is_empty()
    assert not q.is_full()
    q.put("b")
    assert q.is_full()


def test_fifo_order():
    """Messages are retrieved in FIFO order (single thread)."""
    q = EventQueue(capacity=10)
    for i in range(5):
        q.put(f"event_{i}")
    for i in range(5):
        result = q.get()
        msg = result[0] if isinstance(result, tuple) else result
        assert msg == f"event_{i}"
