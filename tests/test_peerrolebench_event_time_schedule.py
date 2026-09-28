from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_event_time_schedule import (  # noqa: E402
    ArrivalAssignment,
    schedule_digest,
    validate_schedule,
)


ROWS = [
    ArrivalAssignment("feedback-b", "terminal_outcome", "outcome-b", "selection-b", 2),
    ArrivalAssignment("feedback-a", "recipient_judgment", "judgment-a", "selection-a", 1),
]


def test_schedule_is_sorted_only_by_frozen_global_index():
    ordered = validate_schedule(ROWS, expected_feedback_ids=("feedback-a", "feedback-b"))
    assert [row.feedback_id for row in ordered] == ["feedback-a", "feedback-b"]
    assert schedule_digest(ROWS) == schedule_digest(list(reversed(ROWS)))


def test_schedule_rejects_duplicate_time_or_event_identity():
    with pytest.raises(ValueError, match="arrival_index"):
        validate_schedule([ROWS[0], ArrivalAssignment("feedback-a", "recipient_judgment", "judgment-a", "selection-a", 2)])
    with pytest.raises(ValueError, match="protocol event"):
        validate_schedule([ROWS[0], ArrivalAssignment("feedback-a", "terminal_outcome", "outcome-b", "selection-a", 1)])


def test_schedule_rejects_missing_expected_feedback():
    with pytest.raises(ValueError, match="expected feedback"):
        validate_schedule(ROWS, expected_feedback_ids=("feedback-a", "feedback-c"))
