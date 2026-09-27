from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_bridge_audit import audit_records  # noqa: E402


def test_existing_peer_role_ledger_is_refused_without_fabricated_policy_fields():
    records = [
        {"event_type": "peer_selection", "payload": {
            "selection_id": "s0", "candidate_ids": ["a", "b"],
            "chosen_peer_id": "a", "propensity": 0.5,
        }},
        {"event_type": "recipient_judgment", "payload": {"judgment_id": "j0"}},
        {"event_type": "terminal_outcome", "payload": {"outcome_id": "o0"}},
    ]
    result = audit_records(records)
    assert result["status"] == "NOT_MAPPABLE"
    assert result["policy_update_allowed"] is False
    assert result["missing"]["selection.candidate_versions"] == 1
    assert result["missing"]["feedback.arrived_at"] == 2
    assert result["missing"]["feedback.recipient_label_mapping"] == 1
    assert result["missing"]["feedback.terminal_label_mapping"] == 1


def test_complete_sidecar_enriched_records_are_mappable():
    selection = {
        "event_type": "peer_selection", "payload": {
            "selection_id": "s0", "candidate_ids": ["a", "b"],
            "candidate_versions": ["v1", "v1"], "chosen_peer_id": "a", "propensity": 0.5,
            "context_key": "ctx", "base_scores": [0.1, 0.2], "state_version": "s0",
            "encoder_version": "enc", "feature_schema": "phi", "selected_at": 1.0,
        },
    }
    feedback = {
        "event_type": "recipient_judgment", "payload": {
            "arrived_at": 2.0, "delay": 1.0, "disposition": "eligible",
            "provenance": "public", "label": 1.0,
        },
    }
    result = audit_records([selection, feedback])
    assert result["status"] == "MAPPABLE"
    assert result["policy_update_allowed"] is True
