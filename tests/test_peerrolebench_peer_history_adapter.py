from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_peer_history import PeerHistoryV1  # noqa: E402
from peerrolebench_peer_history_adapter import append_history_after_credit  # noqa: E402
from peerrolebench_two_stage_gate import DelayedCreditLedger, LaterCredit  # noqa: E402

from test_peerrolebench_peer_history_binding import _ledger_and_offer  # noqa: E402


def test_adapter_appends_only_after_exact_later_credit():
    ledger, offer, assignment, selection, _entry, registry = _ledger_and_offer()
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    assert delayed.apply_once(credit, lambda _: None) is True
    history = PeerHistoryV1.empty("peer-a")
    result = append_history_after_credit(
        history=history, ledger=ledger, offer=offer,
        target_assignment=assignment, target_selection=selection, credit=credit,
        delayed_ledger=delayed,
        assignment_read_cut=5, target_decision_index=6, target_arrival_index=12,
        candidate_key="peer-a@v1", candidate_registry_digest=registry,
    )
    assert len(history.entries) == 1
    assert history.entries[0].recipient_judgment_label == 1.0
    assert history.entries[0].later_outcome_label == 1.0
    assert result["receipt"]["later_credit_digest"] == credit.credit_digest
    assert result["history_projection"]["entry_count"] == 1


def test_adapter_duplicate_credit_is_exactly_once_noop():
    ledger, offer, assignment, selection, _entry, registry = _ledger_and_offer()
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    assert delayed.apply_once(credit, lambda _: None) is True
    history = PeerHistoryV1.empty("peer-a")
    kwargs = {
        "history": history, "ledger": ledger, "offer": offer,
        "target_assignment": assignment, "target_selection": selection,
        "credit": credit, "delayed_ledger": delayed,
        "assignment_read_cut": 5, "target_decision_index": 6,
        "target_arrival_index": 12, "candidate_key": "peer-a@v1",
        "candidate_registry_digest": registry,
    }
    first = append_history_after_credit(**kwargs)
    second = append_history_after_credit(**kwargs)
    assert first["status"] == "APPENDED"
    assert second["status"] == "NOOP"
    assert second["receipt"] is None
    assert len(history.entries) == 1
    assert len(history.seals) == 1


def test_adapter_rejects_unrelated_credit_without_mutating_history():
    ledger, offer, assignment, selection, _entry, registry = _ledger_and_offer()
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="other-evidence",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    assert delayed.apply_once(credit, lambda _: None) is True
    history = PeerHistoryV1.empty("peer-a")
    with pytest.raises(ValueError, match="outside the role offer"):
        append_history_after_credit(
            history=history, ledger=ledger, offer=offer,
            target_assignment=assignment, target_selection=selection, credit=credit,
            delayed_ledger=delayed,
            assignment_read_cut=5, target_decision_index=6, target_arrival_index=12,
            candidate_key="peer-a@v1", candidate_registry_digest=registry,
        )
    assert history.entries == ()
    assert history.seals == ()


def test_adapter_rejects_valid_but_uncommitted_credit():
    ledger, offer, assignment, selection, _entry, registry = _ledger_and_offer()
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    history = PeerHistoryV1.empty("peer-a")
    with pytest.raises(ValueError, match="exact delayed credit to be committed"):
        append_history_after_credit(
            history=history, ledger=ledger, offer=offer,
            target_assignment=assignment, target_selection=selection, credit=credit,
            delayed_ledger=DelayedCreditLedger(),
            assignment_read_cut=5, target_decision_index=6, target_arrival_index=12,
            candidate_key="peer-a@v1", candidate_registry_digest=registry,
        )
    assert history.entries == ()
    assert history.seals == ()


def test_adapter_restores_history_when_append_fails_after_seal():
    ledger, offer, assignment, selection, _entry, registry = _ledger_and_offer()
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    assert delayed.apply_once(credit, lambda _: None) is True

    class FailOnceHistory(PeerHistoryV1):
        failed = False

        def append(self, entry):
            super().append(entry)
            if not type(self).failed:
                type(self).failed = True
                raise RuntimeError("injected append failure after seal")

    history = FailOnceHistory("peer-a")
    with pytest.raises(RuntimeError, match="injected append failure"):
        append_history_after_credit(
            history=history, ledger=ledger, offer=offer,
            target_assignment=assignment, target_selection=selection, credit=credit,
            delayed_ledger=delayed,
            assignment_read_cut=5, target_decision_index=6, target_arrival_index=12,
            candidate_key="peer-a@v1", candidate_registry_digest=registry,
        )
    assert history.entries == ()
    assert history.seals == ()
    retry = append_history_after_credit(
        history=history, ledger=ledger, offer=offer,
        target_assignment=assignment, target_selection=selection, credit=credit,
        delayed_ledger=delayed,
        assignment_read_cut=5, target_decision_index=6, target_arrival_index=12,
        candidate_key="peer-a@v1", candidate_registry_digest=registry,
    )
    assert retry["history_projection"]["entry_count"] == 1


def test_adapter_rejects_missing_target_judgment_before_append():
    ledger, offer, assignment, selection, _entry, registry = _ledger_and_offer()
    ledger.judgments.pop("j1")
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    assert delayed.apply_once(credit, lambda _: None) is True
    history = PeerHistoryV1.empty("peer-a")
    with pytest.raises(ValueError, match="target delivery lacks judgment/action"):
        append_history_after_credit(
            history=history, ledger=ledger, offer=offer,
            target_assignment=assignment, target_selection=selection, credit=credit,
            delayed_ledger=delayed,
            assignment_read_cut=5, target_decision_index=6, target_arrival_index=12,
            candidate_key="peer-a@v1", candidate_registry_digest=registry,
        )
    assert history.entries == ()
    assert history.seals == ()
