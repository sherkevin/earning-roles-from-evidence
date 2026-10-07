"""Native-valid neutral anchors must not become legacy attribution or credit."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'references/aamas'))

from peerrolebench_ledger_replay import replay_ledger_events
from peerrolebench_peer_history import PeerHistoryV1
from peerrolebench_peer_history_adapter import append_history_after_credit
from peerrolebench_role_evidence_offer import build_role_evidence_from_ledger
from peerrolebench_two_stage_gate import (
    DelayedCreditLedger, LaterCredit, derive_later_credit_from_ledger,
    evaluate_source_gate,
)
from test_peerrolebench_peer_history_binding import _ledger_and_offer


@pytest.mark.parametrize('version', ['noisy-observation-completion-v1',
                                     'noisy-observation-completion-v999'])
def test_native_valid_observation_cannot_enter_legacy_channels(version):
    ledger, offer, assignment, selection, _, registry = _ledger_and_offer(
        source_update_version=version)
    # Completeness of native lineage must not be confused with semantic type.
    assert replay_ledger_events(ledger.events, allow_incomplete=True).ledger.evidence['e0'].update_version == version
    with pytest.raises(ValueError, match='noisy observation completion'):
        build_role_evidence_from_ledger(
            ledger=ledger, evidence_id='e0', candidate_key='peer-a@v1', role='producer',
            target_task_index=1, evidence_version='role-evidence-v1', available_index=5)

    # A permissive historical gate is deliberately supplied: the native type
    # boundary must reject even when a caller claims source eligibility.
    complete = {'status': 'PASS', 'coverage_complete': True, 'decision_complete': True}
    gate = evaluate_source_gate(
        {'agent_payloads': {'producer': {'writable_paths': ['producer.py']},
                           'recipient': {'writable_paths': ['processor.py']}}},
        complete, {'target_role': 'producer', 'observed_artifact_sha256': 'a' * 64},
        {'changed_paths': ['producer.py']}, complete)
    assert gate.evidence_publish_allowed
    assert derive_later_credit_from_ledger(
        ledger=ledger, source_gate=gate, assignment_id='as1', source_evidence_id='e0',
        evidence_candidate_id='peer-a@v1', later_outcome_id='o1') is None

    # Bypass the factory to model an erroneous caller. History still rejects
    # before publishing a seal/entry; this is not a real policy update.
    credit = LaterCredit.build(assignment_id='as1', source_evidence_id='e0',
                               later_outcome_id='o1', later_quality=1.0)
    delayed = DelayedCreditLedger()
    delayed.apply_once(credit, lambda _: None)
    history = PeerHistoryV1.empty('peer-a')
    before = history.state_digest()
    with pytest.raises(ValueError, match='noisy observation completion'):
        append_history_after_credit(
            history=history, ledger=ledger, offer=offer,
            target_assignment=assignment, target_selection=selection, credit=credit,
            delayed_ledger=delayed, assignment_read_cut=5, target_decision_index=6,
            target_arrival_index=12, candidate_key='peer-a@v1',
            candidate_registry_digest=registry)
    assert history.state_digest() == before
