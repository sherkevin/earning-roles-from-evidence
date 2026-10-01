from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_isolated_policy_read import read_role_evidence_offer_isolated  # noqa: E402
from peerrolebench_role_evidence_offer import (  # noqa: E402
    PublicRoleEvidence, build_role_evidence_from_ledger, make_role_evidence_offer,
)
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, RecipientJudgment,
    RoleEvidenceUpdate, TerminalOutcome,
)


def evidence(*, candidate="peer-b@v1", evidence_id="e0", source_task=0, available=1):
    return PublicRoleEvidence(
        evidence_id=evidence_id, candidate_key=candidate, role="producer",
        source_task_index=source_task, judgment="accept_with_rework", action="repair",
        delivery_id="d0", judgment_id="j0", action_id="a0", outcome_id="o0",
        artifact_sha256="a" * 64,
        outcome_status="PASS", quality_score=1.0, available_index=available,
    )


def offer(**overrides):
    values = {
        "offer_id": "role-offer-1", "task_id": "task", "task_index": 1,
        "role": "producer", "context_key": "PIPE3:1",
        "candidate_keys": ("peer-b@v1", "peer-c@v1"),
        "evidence": (evidence(),), "evidence_version": "role-evidence-v1",
        "available_index": 1,
    }
    values.update(overrides)
    return make_role_evidence_offer(**values)


def test_role_evidence_offer_uses_native_evidence_id_not_selection_id():
    value = offer()
    assert value.evidence_ids == ("e0",)
    assert value.public_evidence[0]["evidence_id"] == "e0"
    assert value.public_evidence[0]["candidate_key"] == "peer-b@v1"


def test_isolated_reader_consumes_role_evidence_and_binds_digest():
    value = offer()
    trace = read_role_evidence_offer_isolated(value, read_cut=1, previous_aux_hash="GENESIS")
    assert trace.evidence_ids == ("e0",)
    assert trace.candidate_keys == value.candidate_keys
    assert trace.read_cut == 1


def test_role_evidence_cannot_be_future_or_private():
    with pytest.raises(ValueError, match="precede"):
        offer(evidence=(evidence(source_task=1),))
    with pytest.raises(ValueError, match="typed PublicRoleEvidence"):
        bad = dict(evidence().payload())
        bad["private_score"] = 1
        # The offer constructor must reject a row that did not come from the
        # typed public record, before any worker is launched.
        make_role_evidence_offer(
            offer_id="bad", task_id="task", task_index=1, role="producer", context_key="PIPE3:1",
            candidate_keys=("peer-b@v1", "peer-c@v1"), evidence=(bad,),
            evidence_version="role-evidence-v1", available_index=1,
        )


def test_role_evidence_requires_candidate_menu_binding():
    with pytest.raises(ValueError, match="outside"):
        offer(evidence=(evidence(candidate="peer-x@v1"),))


def test_native_ledger_builder_rejects_evidence_subject_mismatch():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", "task", 0, "peer-a", "producer", ("peer-b", "peer-c"), "peer-b", 0.5))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery("d0", "task", "peer-b", "peer-a", "a" * 64, "source", 0, "s0"))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "peer-a", "accept_with_rework", "a" * 64))
    ledger.record_action(ConsumerAction("a0", "d0", "peer-a", True, "a" * 64, "b" * 64, action="repair"))
    ledger.record_outcome(TerminalOutcome("o0", "d0", True, "score-v1", 1.0, "c" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "o0", "ev-v1", 1.0))
    row = build_role_evidence_from_ledger(
        ledger=ledger, evidence_id="e0", candidate_key="peer-b@v1", role="producer",
        target_task_index=1, evidence_version="role-evidence-v1", available_index=1,
    )
    assert row.delivery_id == "d0"
    with pytest.raises(ValueError, match="candidate"):
        build_role_evidence_from_ledger(
            ledger=ledger, evidence_id="e0", candidate_key="peer-c@v1", role="producer",
            target_task_index=1, evidence_version="role-evidence-v1", available_index=1,
        )
