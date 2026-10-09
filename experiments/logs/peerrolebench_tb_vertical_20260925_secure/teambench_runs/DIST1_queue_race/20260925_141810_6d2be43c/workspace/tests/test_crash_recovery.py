"""
Consumer crash recovery tests.

Verifies Bug 2 is fixed: if a consumer gets a event but calls nack()
(simulating a crash), the event must be re-queued and eventually delivered.
"""
import pytest

from mqueue.queue import EventQueue


def test_nack_requeues_message():
    """
    A nack()'d event must be re-delivered to the next consumer.
    """
    q = EventQueue(capacity=10)
    if not hasattr(q, 'ack') or not hasattr(q, 'nack'):
        pytest.skip("Queue does not support ack/nack — fix Bug 2 first")

    q.put("event_important")

    # First get — simulated crash
    msg1, receipt1 = q.get()
    assert msg1 == "event_important"
    q.nack(receipt1)  # Consumer crashed — put it back

    # Second get — must re-deliver the same message
    msg2, receipt2 = q.get()
    assert msg2 == "event_important", (
        f"Message not re-delivered after nack: got {msg2!r}"
    )
    q.ack(receipt2)  # Successful processing


def test_acked_message_not_redelivered():
    """
    An ack()'d event must NOT be re-delivered.
    """
    q = EventQueue(capacity=10)
    if not hasattr(q, 'ack'):
        pytest.skip("Queue does not support ack — fix Bug 2 first")

    q.put("event_done")
    msg, receipt = q.get()
    assert msg == "event_done"
    q.ack(receipt)

    # Queue must now be empty — no re-delivery
    result = q.get()
    if isinstance(result, tuple):
        assert result[0] is None, "Acked message was re-delivered"
    else:
        assert result is None, "Acked message was re-delivered"


def test_multiple_in_flight_nack_all():
    """
    Multiple in-flight events that all get nack()'d must all be re-queued.
    """
    q = EventQueue(capacity=10)
    if not hasattr(q, 'ack') or not hasattr(q, 'nack'):
        pytest.skip("Queue does not support ack/nack — fix Bug 2 first")

    msgs = [f"event_{i}" for i in range(3)]
    for m in msgs:
        q.put(m)

    receipts = []
    for _ in range(3):
        msg, receipt = q.get()
        receipts.append((msg, receipt))

    # Nack all of them (simulate 3 simultaneous crashes)
    for _, receipt in receipts:
        q.nack(receipt)

    # All 3 must be retrievable again
    recovered = []
    for _ in range(3):
        result = q.get()
        if isinstance(result, tuple):
            msg, receipt = result
            if msg is not None:
                q.ack(receipt)
                recovered.append(msg)

    assert len(recovered) == 3, (
        f"Expected 3 recovered events after nack, got {len(recovered)}"
    )
