import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_event_time_interleaving import (  # noqa: E402
    qualify_event_time_interleaving,
    run_interleaving,
)


def test_early_feedback_changes_only_future_decision():
    result = qualify_event_time_interleaving()
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["scientific_claim_allowed"] is False
    assert all(result["checks"].values())


def test_late_feedback_is_not_retroactive():
    late = run_interleaving(policy_name="contextual_trust", arrival_index=3)
    frozen = run_interleaving(policy_name="no_update", arrival_index=1)
    assert late.traces[1].probabilities == frozen.traces[1].probabilities
    assert late.traces[1].evidence_ids == ()
    assert late.traces[2].consumed is True


def test_same_public_schedule_is_given_to_comparator():
    early = run_interleaving(policy_name="contextual_trust", arrival_index=1)
    frozen = run_interleaving(policy_name="no_update", arrival_index=1)
    assert early.traces[1].evidence_ids == frozen.traces[1].evidence_ids == ("selection-0",)
    assert early.traces[1].offer_available_index == frozen.traces[1].offer_available_index == 2
    assert frozen.traces[1].consumed is False


def test_attestations_are_unique_and_state_is_versioned():
    early = run_interleaving(policy_name="contextual_trust", arrival_index=1)
    assert len({trace.attestation_digest for trace in early.traces}) == 3
    assert early.traces[0].state_digest != early.traces[1].state_digest
    assert early.manifest_root != "GENESIS"
