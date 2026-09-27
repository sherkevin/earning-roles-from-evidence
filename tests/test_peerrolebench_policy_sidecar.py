from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_baseline_policies import TerminalOnlyPolicy  # noqa: E402
from peerrolebench_policy_sidecar import (  # noqa: E402
    DecisionSidecar,
    FeedbackSidecar,
    PolicySidecarBridge,
    bind_to_ledger_record,
)


DIGEST = "a" * 64


def decision():
    return DecisionSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="peer_selection", protocol_event_id="s0",
        task_id="task", task_index=0, role="producer", event_id="e0", selector_id="s0", context_key="ctx",
        candidates=(CandidateRef("a", "v1"), CandidateRef("b", "v1")),
        base_scores=(0.2, 0.8), chosen_index=1,
        probabilities=(0.3, 0.7), propensity=0.7,
        state_version="state-0", encoder_version="enc-0", feature_schema="phi-0",
        policy_name="no_update", policy_version="v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=10.0,
    )


def test_decision_sidecar_roundtrip_and_hash_binding():
    sidecar = decision()
    selection = sidecar.to_selection()
    assert selection.chosen.key == "b@v1"
    assert sidecar.sidecar_digest != DIGEST
    bind_to_ledger_record(sidecar.payload(), {
        "event_type": "peer_selection", "payload": {
            "selection_id": "s0", "task_id": "task", "task_index": 0,
        }, "record_hash": DIGEST,
    })
    with pytest.raises(ValueError, match="different ledger record"):
        bind_to_ledger_record(sidecar.payload(), {"record_hash": "b" * 64})


def test_sidecar_binding_rejects_wrong_event_identity():
    record = {
        "event_type": "peer_selection", "payload": {
            "selection_id": "s0", "task_id": "task", "task_index": 0,
        }, "record_hash": DIGEST,
    }
    with pytest.raises(ValueError, match="event type"):
        bind_to_ledger_record(decision().payload(), record, expected_event_type="recipient_judgment")
    with pytest.raises(ValueError, match="event id"):
        bind_to_ledger_record(decision().payload(), {
            **record, "payload": {"selection_id": "other", "task_id": "task", "task_index": 0},
        })
    with pytest.raises(ValueError, match="ledger record"):
        bind_to_ledger_record(decision().payload(), {
            **record, "event_type": "recipient_judgment",
        })


def test_feedback_sidecar_requires_mapping_for_public_label_and_hides_unknown():
    feedback = FeedbackSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="recipient_judgment", protocol_event_id="j0",
        feedback_id="f0", source_event_id="e0", selection_event_id="s0", delivery_id="d0",
        producer_id="peer-a", recipient_id="peer-b",
        source="recipient_judgment", arrived_at=12.0, delay=2.0,
        action="repair", disposition="eligible", provenance="public",
        label_mapping_version="judgment-v1", mapping_digest=DIGEST,
        responsibility_status="attributed", attribution_basis="producer-contract-v1",
        raw_value="accept_with_rework", label=0.5,
    )
    assert feedback.to_feedback().label == 0.5
    unknown = FeedbackSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="terminal_outcome", protocol_event_id="o0",
        feedback_id="f1", source_event_id="e0", selection_event_id="s0", delivery_id="d0",
        producer_id="peer-a", recipient_id="peer-b",
        source="terminal_outcome", arrived_at=13.0, delay=3.0,
        action="redo", disposition="unknown", provenance="unknown",
        label_mapping_version="", mapping_digest="", responsibility_status="unknown",
        attribution_basis="", raw_value=None, label=None,
    )
    assert unknown.to_feedback() is None
    with pytest.raises(ValueError, match="mapping version"):
        FeedbackSidecar(
            ledger_record_hash=DIGEST, protocol_event_type="recipient_judgment", protocol_event_id="j2",
            feedback_id="f2", source_event_id="e0", selection_event_id="s0", delivery_id="d0",
            producer_id="peer-a", recipient_id="peer-b",
            source="recipient_judgment", arrived_at=12.0, delay=2.0,
            action="accept", disposition="eligible", provenance="public",
            label_mapping_version="", mapping_digest="", responsibility_status="attributed",
            attribution_basis="producer-contract-v1", raw_value="accept", label=1.0,
        )


def test_sidecar_rejects_untrusted_probability_or_hidden_label():
    with pytest.raises(ValueError, match="propensity"):
        DecisionSidecar(
            **{**decision().__dict__, "propensity": 0.6}
        )
    with pytest.raises(ValueError, match="cannot carry a label"):
        FeedbackSidecar(
            ledger_record_hash=DIGEST, protocol_event_type="terminal_outcome", protocol_event_id="o3",
            feedback_id="f3", source_event_id="e0", selection_event_id="s0", delivery_id="d0",
            producer_id="peer-a", recipient_id="peer-b",
            source="terminal_outcome", arrived_at=13.0, delay=3.0,
            action="use", disposition="unknown", provenance="unknown",
            label_mapping_version="", mapping_digest="", responsibility_status="unknown",
            attribution_basis="", raw_value="success", label=0.0,
        )


def _record(event_type, event_id):
    field = {"peer_selection": "selection_id", "recipient_judgment": "judgment_id",
             "terminal_outcome": "outcome_id"}[event_type]
    return {
        "event_type": event_type,
        "payload": {field: event_id, "task_id": "task", "task_index": 0},
        "record_hash": DIGEST,
    }


def _feedback(*, event_type, event_id, disposition, provenance, label=None, action="repair"):
    return FeedbackSidecar(
        ledger_record_hash=DIGEST, protocol_event_type=event_type, protocol_event_id=event_id,
        feedback_id=f"feedback-{event_id}", source_event_id="e0", selection_event_id="s0",
        delivery_id="d0", producer_id="peer-a", recipient_id="peer-b",
        source=event_type, arrived_at=12.0, delay=2.0, action=action,
        disposition=disposition, provenance=provenance,
        label_mapping_version="judgment-v1" if disposition == "eligible" else "",
        mapping_digest=DIGEST if disposition == "eligible" else "",
        responsibility_status="attributed" if disposition == "eligible" else "unknown",
        attribution_basis="contract-v1" if disposition == "eligible" else "",
        raw_value="accept" if label is not None else None, label=label,
    )


def test_sidecar_bridge_replays_delayed_feedback_without_resampling_or_unknown_update():
    bridge = PolicySidecarBridge(TerminalOnlyPolicy())
    bridge.ingest_selection(decision(), _record("peer_selection", "s0"))
    unknown = _feedback(event_type="recipient_judgment", event_id="j0",
                       disposition="unknown", provenance="unknown")
    assert bridge.ingest_feedback(unknown, _record("recipient_judgment", "j0")) is False
    assert bridge.policy.updates == 0
    terminal = _feedback(event_type="terminal_outcome", event_id="o0",
                         disposition="eligible", provenance="public", label=1.0, action="use")
    assert bridge.ingest_feedback(terminal, _record("terminal_outcome", "o0")) is True
    assert bridge.policy.updates == 1
    duplicate_channel = _feedback(event_type="terminal_outcome", event_id="o1",
                                  disposition="eligible", provenance="public", label=0.0, action="use")
    assert bridge.ingest_feedback(duplicate_channel, _record("terminal_outcome", "o1")) is False
    assert bridge.policy.updates == 1


def test_sidecar_bridge_rejects_feedback_before_selection():
    bridge = PolicySidecarBridge(TerminalOnlyPolicy())
    terminal = _feedback(event_type="terminal_outcome", event_id="o0",
                         disposition="eligible", provenance="public", label=1.0, action="use")
    with pytest.raises(ValueError, match="unknown protocol selection"):
        bridge.ingest_feedback(terminal, _record("terminal_outcome", "o0"))
