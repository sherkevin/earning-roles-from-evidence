from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_assignment_attestation import (  # noqa: E402
    AssignmentEvidenceOffer,
    DecisionConsumptionAttestation,
    _digest,
    build_consumption_attestation,
    verify_consumption_attestation,
)
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_policy_sidecar import DecisionSidecar  # noqa: E402


DIGEST = "a" * 64


def decision(**overrides):
    values = {
        "ledger_record_hash": DIGEST,
        "protocol_event_type": "peer_selection",
        "protocol_event_id": "s0",
        "task_id": "task",
        "task_index": 0,
        "role": "producer",
        "event_id": "e0",
        "selector_id": "selector",
        "context_key": "ctx",
        "candidates": (CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        "base_scores": (0.2, 0.8),
        "chosen_index": 1,
        "probabilities": (0.5, 0.5),
        "propensity": 0.5,
        "state_version": "state-1",
        "encoder_version": "enc-1",
        "feature_schema": "phi-1",
        "policy_name": "contextual_trust",
        "policy_version": "v1",
        "base_score_version": "base-1",
        "rng_algorithm": "rng",
        "rng_draw": 0,
        "selected_at": 10.0,
        "state_digest": "b" * 64,
    }
    values.update(overrides)
    return DecisionSidecar(**values)


def offer(**overrides):
    values = {
        "offer_id": "offer-0",
        "offer_record_hash": DIGEST,
        "task_id": "task",
        "task_index": 0,
        "role": "producer",
        "context_key": "ctx",
        "candidate_keys": ("peer-a@v1", "peer-b@v1"),
        "evidence_ids": ("e0",),
        "evidence_version": "ev-v1",
        "public_rows": ({
            "feedback_id": "f0", "source_event_id": "e0", "source": "recipient_judgment",
            "candidate_key": "peer-b@v1", "evidence_version": "ev-v1", "source_index": 0,
            "arrival_index": 2,
            "arrived_at": 4.0, "delay": 1.0, "action": "repair", "disposition": "eligible",
            "provenance": "public", "label": 1.0,
        },),
        "available_index": 2,
    }
    values.update(overrides)
    payload = {
        "offer_id": values["offer_id"],
        "task_id": values["task_id"], "task_index": values["task_index"], "role": values["role"],
        "context_key": values["context_key"], "candidate_keys": list(values["candidate_keys"]),
        "evidence_ids": list(values["evidence_ids"]), "evidence_version": values["evidence_version"],
        "public_rows": [dict(row) for row in values["public_rows"]],
        "available_index": values["available_index"],
        "watermark_schema": "global-event-index-v1",
    }
    values["bundle_digest"] = _digest(payload)
    return AssignmentEvidenceOffer(**values)


def test_consumed_offer_binds_preselection_context_and_state():
    ev, dec = offer(), decision()
    att = build_consumption_attestation(ev, dec, consumed=True, read_cut=2, decision_index=3)
    assert verify_consumption_attestation(att, ev, dec) is True
    assert "selected_candidate_key" not in ev.payload()
    assert "propensity" not in ev.payload()
    assert att.policy_state_digest_before == dec.state_digest


def test_unconsumed_offer_is_explicit_control_and_ignores_bundle_contents():
    ev, dec = offer(), decision()
    changed = offer(public_rows=({**ev.public_rows[0], "label": 0.0},))
    att0 = build_consumption_attestation(ev, dec, consumed=False, read_cut=2, decision_index=3)
    att1 = build_consumption_attestation(changed, dec, consumed=False, read_cut=2, decision_index=3)
    assert verify_consumption_attestation(att0, ev, dec) is False
    assert verify_consumption_attestation(att1, changed, dec) is False
    assert att0.policy_input_digest == att1.policy_input_digest


def test_consumed_public_mutation_changes_policy_input_digest():
    ev, dec = offer(), decision()
    changed = offer(public_rows=({**ev.public_rows[0], "label": 0.0},))
    att0 = build_consumption_attestation(ev, dec, consumed=True, read_cut=2, decision_index=3)
    att1 = build_consumption_attestation(changed, dec, consumed=True, read_cut=2, decision_index=3)
    assert att0.policy_input_digest != att1.policy_input_digest


def test_operator_ledger_hash_does_not_change_public_bundle_digest():
    assert offer(offer_record_hash="d" * 64).bundle_digest == offer().bundle_digest


def test_offer_can_carry_a_late_correction_without_collapsing_source_lineage():
    first = offer().public_rows[0]
    correction = {
        **first,
        "feedback_id": "f0-correction",
        "arrival_index": 3,
        "arrived_at": 5.0,
        "delay": 2.0,
        "label": 0.0,
        "supersedes": "f0",
    }
    ev = offer(
        available_index=3,
        public_rows=(first, correction),
    )
    assert ev.evidence_ids == ("e0",)
    assert ev.payload()["public_rows"][1]["supersedes"] == "f0"


@pytest.mark.parametrize("bad_row", [
    {"raw_value": "secret"}, {"unknown": "field"},
])
def test_offer_rejects_private_or_unknown_public_fields(bad_row):
    with pytest.raises(ValueError, match="private or unknown"):
        offer(public_rows=({**offer().public_rows[0], **bad_row},))


def test_offer_rejects_non_scalar_or_non_numeric_timing():
    with pytest.raises(ValueError, match="numeric"):
        offer(public_rows=({**offer().public_rows[0], "source_index": [0]},))


def test_offer_rejects_unsorted_or_duplicate_evidence_ids():
    with pytest.raises(ValueError, match="sorted"):
        offer(evidence_ids=("e1", "e0"))


def test_attestation_rejects_future_offer_and_menu_or_context_mismatch():
    with pytest.raises(ValueError, match="unavailable"):
        build_consumption_attestation(offer(available_index=4), decision(), consumed=True, read_cut=2, decision_index=3)
    with pytest.raises(ValueError, match="candidate menu"):
        build_consumption_attestation(offer(candidate_keys=("peer-b@v1", "peer-a@v1")), decision(), consumed=True, read_cut=2, decision_index=3)
    with pytest.raises(ValueError, match="context"):
        build_consumption_attestation(offer(context_key="other"), decision(), consumed=True, read_cut=2, decision_index=3)


def test_attestation_requires_state_digest_and_verification_rejects_other_decision():
    with pytest.raises(ValueError, match="state digest"):
        build_consumption_attestation(offer(), decision(state_digest=None), consumed=True, read_cut=2, decision_index=3)
    ev, dec = offer(), decision()
    att = build_consumption_attestation(ev, dec, consumed=True, read_cut=2, decision_index=3)
    with pytest.raises(ValueError, match="decision mismatch"):
        verify_consumption_attestation(att, ev, decision(event_id="other"))


def test_attestation_rejects_tampered_canonical_digest():
    ev, dec = offer(), decision()
    att = build_consumption_attestation(ev, dec, consumed=True, read_cut=2, decision_index=3)
    with pytest.raises(ValueError, match="attestation_digest"):
        DecisionConsumptionAttestation(**{**att.__dict__, "policy_input_digest": "d" * 64})
