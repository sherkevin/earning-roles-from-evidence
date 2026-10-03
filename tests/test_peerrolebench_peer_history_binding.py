from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    ProducerScore,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)
from peerrolebench_peer_history import HistoryCostV1, HistoryEntryV1  # noqa: E402
from peerrolebench_peer_history_binding import build_history_binding_receipt  # noqa: E402
from peerrolebench_role_evidence_offer import (  # noqa: E402
    PublicRoleEvidence,
    make_role_evidence_offer,
)


def _digest(value) -> str:
    if isinstance(value, str):
        value = value.encode()
    else:
        value = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(value).hexdigest()


def _ledger_and_offer():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", "task", 0, "peer-r", "producer",
                                         ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery("d0", "task", "peer-a", "peer-r", "a" * 64,
                                    "source0", 0, "s0"))
    ledger.record_producer_score(ProducerScore(
        "q0", "d0", "a" * 64, "producer-score-v2", "PASS", 1, 1.0, "b" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "peer-r", "accept", "a" * 64))
    ledger.record_action(ConsumerAction("c0", "d0", "peer-r", True, "a" * 64, "c" * 64, action="use"))
    ledger.record_outcome(TerminalOutcome("o0", "d0", True, "target-score-v1", 1.0, "d" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "c0", "o0", "role-evidence-v1", 5.0))
    assignment = LaterAssignment("as1", "task", 1, "peer-a", "producer", ("e0",), 0.5)
    ledger.record_assignment(assignment)
    ledger.record_selection(PeerSelection("s1", "task", 1, "peer-r2", "producer",
                                         ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start("task", 1)
    ledger.record_delivery(Delivery("d1", "task", "peer-a", "peer-r2", "e" * 64,
                                    "source1", 1, "s1"))
    ledger.record_judgment(RecipientJudgment("j1", "d1", "peer-r2", "accept", "e" * 64))
    ledger.record_action(ConsumerAction("c1", "d1", "peer-r2", True, "e" * 64, "f" * 64, action="use"))
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "target-score-v1", 1.0, "1" * 64))
    registry = _digest("registry")
    source_row = PublicRoleEvidence(
        evidence_id="e0", candidate_key="peer-a@v1", role="producer", source_task_index=0,
        delivery_id="d0", judgment_id="j0", action_id="c0", outcome_id="o0",
        artifact_sha256="a" * 64, judgment="accept", action="use", outcome_status="PASS",
        quality_score=1.0, available_index=5,
    )
    offer = make_role_evidence_offer(
        offer_id="offer-1", task_id="task", task_index=1, role="producer", context_key="ctx",
        candidate_keys=("peer-a@v1", "peer-b@v1"), evidence=(source_row,),
        evidence_version="role-evidence-v1", available_index=5,
        candidate_registry_digest=registry,
    )
    entry = HistoryEntryV1(
        "h1", "peer-a", "peer-a", _digest("role"), _digest("state"), "a" * 64,
        "j0", 1.0, "o1", 1.0, _digest("metric"), HistoryCostV1(wall_ms=12.0),
        13, "as1", "PASS",
    )
    return ledger, offer, assignment, ledger.selections["s1"], entry, registry


def test_source_target_binding_is_canonical_and_version_bound():
    ledger, offer, assignment, selection, entry, registry = _ledger_and_offer()
    receipt = build_history_binding_receipt(
        entry=entry, ledger=ledger, offer=offer, target_assignment=assignment,
        target_selection=selection, target_outcome_id="o1", assignment_read_cut=5,
        target_decision_index=6, target_arrival_index=12,
        candidate_key="peer-a@v1", candidate_registry_digest=registry,
        later_credit_digest=_digest("credit"),
    )
    assert receipt.source_evidence_id == "e0"
    assert receipt.source_delivery_id == "d0"
    assert receipt.target_delivery_id == "d1"
    assert receipt.target_outcome_id == "o1"
    assert receipt.binding_digest == _digest(receipt.payload(include_digest=False))


@pytest.mark.parametrize("mutation, message", [
    ("read_cut", "read cut"),
    ("candidate", "candidate"),
    ("arrival", "history entry arrived"),
])
def test_source_target_binding_rejects_temporal_or_identity_mutation(mutation, message):
    ledger, offer, assignment, selection, entry, registry = _ledger_and_offer()
    kwargs = {
        "entry": entry, "ledger": ledger, "offer": offer, "target_assignment": assignment,
        "target_selection": selection, "target_outcome_id": "o1", "assignment_read_cut": 5,
        "target_decision_index": 6, "target_arrival_index": 12,
        "candidate_key": "peer-a@v1", "candidate_registry_digest": registry,
        "later_credit_digest": _digest("credit"),
    }
    if mutation == "read_cut":
        kwargs["assignment_read_cut"] = 4
    elif mutation == "candidate":
        kwargs["candidate_key"] = "peer-b@v1"
    else:
        kwargs["target_arrival_index"] = 13
        kwargs["entry"] = replace(entry, arrival_index=12)
    with pytest.raises(ValueError, match=message):
        build_history_binding_receipt(**kwargs)
