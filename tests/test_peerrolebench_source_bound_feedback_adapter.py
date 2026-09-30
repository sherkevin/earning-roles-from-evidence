from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import PeerRoleLedger, PeerSelection  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402
from peerrolebench_source_bound_feedback_adapter import build_source_bound_offer  # noqa: E402
from peerrolebench_source_bound_feedback_adapter_qualification import fixture  # noqa: E402


def test_source_bound_adapter_seals_canonical_offer():
    ledger, selection, selection_record, sidecar, judgment_record, gate, schedule = fixture()
    result = build_source_bound_offer(
        selection=selection, selection_record=selection_record,
        feedback_inputs=((sidecar, judgment_record, gate, None),), ledger=ledger,
        arrival_schedule=schedule, offer_id="offer-test", context_key="PIPE3:1",
    )
    assert result.offer.public_rows[0]["candidate_key"] == "peer-b@v1"
    assert result.offer.public_rows[0]["arrival_index"] == 0
    assert result.projection_digests == (sidecar.sidecar_digest,)


def test_source_bound_adapter_requires_explicit_future_target_index():
    ledger, selection, selection_record, sidecar, judgment_record, gate, schedule = fixture()
    with pytest.raises(ValueError, match="target task index"):
        build_source_bound_offer(
            selection=selection, selection_record=selection_record,
            feedback_inputs=((sidecar, judgment_record, gate, None),), ledger=ledger,
            arrival_schedule=schedule, offer_id="offer-same-task", context_key="PIPE3:0",
            target_task_index=0,
        )


@pytest.mark.parametrize("mutated_schedule", [
    (ArrivalAssignment("feedback-0", "terminal_outcome", "judgment-0", "policy-selection-0", 0),),
    (ArrivalAssignment("feedback-0", "recipient_judgment", "judgment-0", "policy-selection-0", 1),),
])
def test_source_bound_adapter_rejects_schedule_mutation(mutated_schedule):
    ledger, selection, selection_record, sidecar, judgment_record, gate, _ = fixture()
    with pytest.raises(ValueError):
        build_source_bound_offer(
            selection=selection, selection_record=selection_record,
            feedback_inputs=((sidecar, judgment_record, gate, None),), ledger=ledger,
            arrival_schedule=mutated_schedule, offer_id="offer-test", context_key="PIPE3:1",
        )


def test_source_bound_adapter_rejects_noncanonical_record_hash():
    ledger, selection, selection_record, sidecar, judgment_record, gate, schedule = fixture()
    with pytest.raises(ValueError):
        build_source_bound_offer(
            selection=selection, selection_record=selection_record,
            feedback_inputs=((sidecar, {**judgment_record, "record_hash": "b" * 64}, gate, None),),
            ledger=ledger, arrival_schedule=schedule, offer_id="offer-test", context_key="PIPE3:1",
        )


def test_source_bound_adapter_does_not_accept_incomplete_ledger():
    _, selection, selection_record, sidecar, judgment_record, gate, schedule = fixture()
    incomplete = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    incomplete.record_selection(PeerSelection(
        "selection-0", "PIPE3_stream_processing", 0, "peer-a", "producer",
        ("peer-b", "peer-c"), "peer-b", 0.5,
    ))
    with pytest.raises(ValueError):
        build_source_bound_offer(
            selection=selection, selection_record=selection_record,
            feedback_inputs=((sidecar, judgment_record, gate, None),), ledger=incomplete,
            arrival_schedule=schedule, offer_id="offer-test", context_key="PIPE3:1",
        )
