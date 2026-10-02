from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_chain_composition import compose_pipe2_chain  # noqa: E402


def test_eligible_chain_reaches_later_assignment_and_next_task_start():
    result = compose_pipe2_chain(0, variant="eligible")
    assert result["gate"]["feedback_status"] == "ELIGIBLE"
    assert result["evidence_recorded"] is True
    assert result["assignment_recorded"] is True
    assert result["next_selection_recorded"] is True
    assert result["ledger_snapshot"] == {
        "event_count": 11, "last_hash": result["ledger_snapshot"]["last_hash"],
        "delivery_count": 1, "producer_score_count": 1, "judgment_count": 1,
        "action_count": 1, "outcome_count": 1, "evidence_count": 1,
        "assignment_count": 1,
    }
    assert result["scientific_claim_allowed"] is False


@pytest.mark.parametrize("variant, status", [
    ("repair", "PENDING_ATTRIBUTION"),
    ("mixed", "UNKNOWN"),
])
def test_non_eligible_controls_stop_before_evidence_and_assignment(variant: str, status: str):
    result = compose_pipe2_chain(1, variant=variant)
    assert result["gate"]["feedback_status"] == status
    assert result["evidence_recorded"] is False
    assert result["assignment_recorded"] is False
    assert result["next_selection_recorded"] is False
