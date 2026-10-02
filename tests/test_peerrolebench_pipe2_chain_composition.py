from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_chain_composition import compose_pipe2_chain  # noqa: E402


def test_unregistered_accept_chain_stops_before_role_evidence():
    result = compose_pipe2_chain(0, variant="eligible")
    assert result["gate"]["feedback_status"] == "PENDING_ATTRIBUTION"
    assert result["evidence_recorded"] is False
    assert result["assignment_recorded"] is False
    assert result["next_selection_recorded"] is False
    assert result["ledger_event_types"] == [
        "peer_selection", "task_start", "producer_delivery", "producer_score",
        "recipient_judgment", "consumer_action", "terminal_outcome",
    ]
    assert len(result["ledger_event_hashes"]) == 7
    assert result["ledger_snapshot"] == {
        "event_count": 7, "last_hash": result["ledger_snapshot"]["last_hash"],
        "delivery_count": 1, "producer_score_count": 1, "judgment_count": 1,
        "action_count": 1, "outcome_count": 1, "evidence_count": 0,
        "assignment_count": 0,
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
    assert result["ledger_event_types"] == [
        "peer_selection", "task_start", "producer_delivery", "producer_score",
        "recipient_judgment", "consumer_action", "terminal_outcome",
    ]
