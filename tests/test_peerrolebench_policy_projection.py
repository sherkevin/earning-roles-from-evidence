from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_policy_projection import (  # noqa: E402
    AttributionGate,
    RAW_ACCEPTANCE_MAPPING_VERSION,
    RawAcceptanceSidecar,
    _digest,
    project_feedback,
    project_raw_acceptance,
)
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar  # noqa: E402
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402


DIGEST = "a" * 64
GATE_DIGEST = "b" * 64


def sidecar(**overrides):
    values = {
        "ledger_record_hash": DIGEST,
        "protocol_event_type": "recipient_judgment",
        "protocol_event_id": "j0",
        "feedback_id": "f0",
        "source_event_id": "e0",
        "selection_event_id": "s0",
        "delivery_id": "d0",
        "producer_id": "peer-b",
        "producer_version": "v1",
        "recipient_id": "peer-a",
        "source": "recipient_judgment",
        "arrived_at": 12.0,
        "delay": 2.0,
        "action": "repair",
        "disposition": "eligible",
        "provenance": "public",
        "label_mapping_version": "judgment-v1",
        "mapping_digest": DIGEST,
        "responsibility_status": "attributed",
        "attribution_basis": "producer-contract-v1",
        "raw_value": "accept_with_rework",
        "label": 0.5,
        "sidecar_version": "peerrole-policy-sidecar-v2",
    }
    values.update(overrides)
    return FeedbackSidecar(**values)


def gate(*, sidecar_obj=None, **overrides):
    bound_sidecar = sidecar_obj or sidecar()
    values = {
        "gate_version": "gate-v1",
        "ledger_record_hash": DIGEST,
        "sidecar_digest": bound_sidecar.sidecar_digest,
        "protocol_event_type": "recipient_judgment",
        "protocol_event_id": "j0",
        "source_event_id": "e0",
        "delivery_id": "d0",
        "producer_id": "peer-b",
        "producer_version": "v1",
        "recipient_id": "peer-a",
        "selection_event_id": "s0",
        "eligible": True,
        "weight": 1.0,
        "label": bound_sidecar.label,
        "label_mapping_version": "judgment-v1",
        "evidence_version": "evidence-v1",
        "source_index": 5,
    }
    values.update(overrides)
    digest_payload = {key: values[key] for key in (
        "gate_version", "ledger_record_hash", "sidecar_digest", "protocol_event_type",
        "protocol_event_id", "source_event_id", "delivery_id", "producer_id",
        "producer_version", "recipient_id", "selection_event_id", "eligible", "weight",
        "label", "label_mapping_version", "evidence_version", "source_index",
    )}
    values["gate_digest"] = _digest(digest_payload)
    return AttributionGate(**values)


def selection():
    return DecisionSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="peer_selection", protocol_event_id="s0",
        task_id="task", task_index=0, role="producer", event_id="e0", selector_id="selector",
        context_key="ctx", candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(0.2, 0.8), chosen_index=1,
        probabilities=(0.5, 0.5), propensity=0.5, state_version="state", encoder_version="enc",
        feature_schema="phi", policy_name="no_update", policy_version="v1", base_score_version="base",
        rng_algorithm="rng", rng_draw=0, selected_at=1.0,
    )


def raw_sidecar(**overrides):
    values = {
        "ledger_record_hash": DIGEST,
        "protocol_event_type": "recipient_judgment",
        "protocol_event_id": "j0",
        "feedback_id": "raw-f0",
        "source_event_id": "e0",
        "selection_event_id": "s0",
        "delivery_id": "d0",
        "producer_id": "peer-b",
        "producer_version": "v1",
        "recipient_id": "peer-a",
        "decision": "accept",
        "label_mapping_version": RAW_ACCEPTANCE_MAPPING_VERSION,
        "mapping_digest": DIGEST,
        "source_index": 5,
        "arrived_at": 12.0,
        "delay": 2.0,
    }
    values.update(overrides)
    return RawAcceptanceSidecar(**values)


def raw_judgment_record(decision="accept"):
    return {
        "record_hash": DIGEST,
        "event_type": "recipient_judgment",
        "payload": {
            "judgment_id": "j0",
            "delivery_id": "d0",
            "consumer_id": "peer-a",
            "decision": decision,
        },
    }


def test_projection_exposes_only_typed_minimal_feedback():
    projection = project_feedback(sidecar(), gate(), selection=selection())
    feedback = projection.to_feedback()
    assert feedback is not None
    assert feedback.label == 0.5
    assert projection.candidate_key == "peer-b@v1"
    payload = projection.public_payload()
    assert payload["evidence_version"] == "evidence-v1"
    assert payload["source_index"] == 5
    for private_name in {
        "raw_value", "responsibility_status", "attribution_basis",
        "mapping_digest", "gate_digest", "producer_score_status",
    }:
        assert private_name not in payload


def test_raw_acceptance_projection_is_public_but_not_attributed():
    projection = project_raw_acceptance(
        raw_sidecar(), selection=selection(), ledger_record=raw_judgment_record(),
    )
    feedback = projection.to_feedback()
    assert feedback is not None
    assert feedback.source == "raw_acceptance"
    assert feedback.label == 1.0
    assert projection.public_payload()["action"] == "accept"
    assert all(name not in projection.public_payload() for name in (
        "responsibility_status", "attribution_basis", "gate_digest", "weight",
    ))

    rejected = project_raw_acceptance(
        raw_sidecar(decision="reject"), selection=selection(),
        ledger_record=raw_judgment_record(decision="reject"),
    )
    assert rejected.to_feedback().label == 0.0


def test_raw_acceptance_projection_rejects_rework_and_canonical_mutation():
    with pytest.raises(ValueError, match="accept or reject"):
        raw_sidecar(decision="rework")
    with pytest.raises(ValueError, match="canonical judgment"):
        project_raw_acceptance(
            raw_sidecar(), selection=selection(),
            ledger_record=raw_judgment_record(decision="reject"),
        )
    with pytest.raises(ValueError, match="selected candidate"):
        project_raw_acceptance(
            raw_sidecar(producer_id="peer-a"), selection=selection(),
            ledger_record=raw_judgment_record(),
        )


def test_ineligible_gate_projects_unknown_and_cannot_update_policy():
    unknown_sidecar = sidecar(disposition="unknown", provenance="unknown", raw_value=None, label=None)
    projection = project_feedback(
        unknown_sidecar,
        gate(sidecar_obj=unknown_sidecar, eligible=False, weight=None, label=None),
        selection=selection(),
    )
    assert projection.disposition == "unknown"
    assert projection.to_feedback() is None
    payload = projection.public_payload()
    assert "label" not in payload and "weight" not in payload


def test_projection_rejects_eligible_gate_for_non_public_sidecar():
    unknown_sidecar = sidecar(disposition="unknown", provenance="unknown", raw_value=None, label=None)
    with pytest.raises(ValueError, match="non-public sidecar"):
        project_feedback(unknown_sidecar, gate(sidecar_obj=unknown_sidecar, label=0.5), selection=selection())


def test_projection_rejects_label_substitution():
    with pytest.raises(ValueError, match="label mismatch"):
        project_feedback(sidecar(), gate(label=1.0), selection=selection())


@pytest.mark.parametrize("field", [
    "protocol_event_type", "protocol_event_id", "source_event_id", "recipient_id",
    "ledger_record_hash", "selection_event_id",
])
def test_projection_rejects_cross_event_identity_mutation(field):
    mutation = {"protocol_event_type": "terminal_outcome", "ledger_record_hash": "c" * 64}.get(field, "other")
    mutated = sidecar(**{field: mutation})
    with pytest.raises(ValueError):
        project_feedback(mutated, gate(), selection=selection())


def test_projection_rejects_feedback_for_unchosen_candidate():
    unchosen = sidecar(producer_id="peer-a")
    with pytest.raises(ValueError, match="selected candidate"):
        project_feedback(unchosen, gate(sidecar_obj=unchosen, producer_id="peer-a"), selection=selection())


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"delivery_id": "other"}, "delivery mismatch"),
        ({"producer_id": "peer-c"}, "producer mismatch"),
        ({"producer_version": "v2"}, "producer mismatch"),
    ],
)
def test_projection_rejects_lineage_mismatch(changes, message):
    with pytest.raises(ValueError, match=message):
        project_feedback(sidecar(), gate(**changes), selection=selection())


def test_projection_rejects_label_mapping_mismatch():
    with pytest.raises(ValueError, match="label mapping mismatch"):
        project_feedback(sidecar(), gate(label_mapping_version="judgment-v2"), selection=selection())


def test_gate_rejects_private_label_on_ineligible_event():
    with pytest.raises(ValueError, match="cannot carry policy label"):
        gate(eligible=False, weight=1.0, label=None)
    with pytest.raises(ValueError, match="eligible gate requires label"):
        gate(label=None)


def test_projection_rejects_non_finite_sidecar_time():
    with pytest.raises(ValueError, match="finite"):
        project_feedback(sidecar(arrived_at=float("nan")), gate(), selection=selection())
