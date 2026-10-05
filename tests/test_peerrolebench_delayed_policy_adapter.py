from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import CandidateRef, FeatureContextualTrustPolicy, Feedback
from peerrolebench_delayed_policy_adapter import DelayedPolicyAdapter, LaterChannelPayload
from peerrolebench_delayed_policy_adapter import ValidatedLaterCredit
from peerrolebench_peer_history import HistoryEntryV1
from peerrolebench_role_evidence_offer import PublicRoleEvidence, make_role_evidence_offer
from peerrolebench_two_stage_gate import SourceGate, LaterCredit
from peer_role_protocol_20260925 import RoleEvidenceUpdate

from test_peerrolebench_peer_history_binding import _ledger_and_offer


def gate() -> SourceGate:
    return SourceGate(
        gate_version="two-stage-role-evidence-v2",
        producer_paths_changed=("producer.py",), recipient_paths_changed=(),
        q_complete=True, y_complete=True, target_role="producer",
        artifact_binding_present=True, later_use_valid=False,
        attribution_eligible=True, evidence_publish_allowed=True,
        policy_update_allowed=False, status="ELIGIBLE", reason="test",
    )


def offer():
    evidence = PublicRoleEvidence(
        evidence_id="e-source", candidate_key="peer-b@v1", role="producer",
        source_task_index=0, delivery_id="d0", judgment_id="j0", action_id="a0",
        outcome_id="o0", artifact_sha256="a" * 64, judgment="accept",
        action="use", outcome_status="PASS", quality_score=1.0, available_index=2,
    )
    return make_role_evidence_offer(
        offer_id="offer-1", task_id="task", task_index=1, role="producer",
        context_key="ctx", candidate_keys=("peer-b@v1", "peer-c@v1"),
        evidence=(evidence,), evidence_version="role-evidence-v1", available_index=2,
    )


def policy() -> FeatureContextualTrustPolicy:
    return FeatureContextualTrustPolicy(
        dimension=2, ridge=1.0, trust_scale=1.0,
        encoder_version="hash64-v1", feature_schema="matrix-features-v1",
    )


def choose(adapter: DelayedPolicyAdapter):
    return adapter.policy.choose(
        event_id="target-selection", context_key="ctx", selector_id="selector",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        # Make the selected candidate deterministic without using a hand-coded
        # choice: the shared base-score contract strongly favors peer-b.
        base_scores=(100.0, 0.0), rng=__import__("numpy").random.default_rng(0),
        state_version="initial", encoder_version="hash64-v1",
        feature_schema="matrix-features-v1", captured_features={
            "peer-b@v1": (1.0, 0.0), "peer-c@v1": (0.0, 1.0),
        },
    )


def credit() -> LaterCredit:
    return LaterCredit.build(
        assignment_id="assignment-1", source_evidence_id="e-source",
        later_outcome_id="o-later", later_quality=1.0,
    )


def channel(selection, *, outcome="o-later", feedback_id="fb-1") -> LaterChannelPayload:
    return LaterChannelPayload(
        credit=credit(),
        feedback=Feedback(
            feedback_id=feedback_id, source_event_id=selection.event_id,
            source="recipient_judgment", label=1.0, arrived_at=3.0, delay=1.0,
            action="accept", disposition="eligible", provenance="public", arrival_index=3,
        ),
        target_outcome_id=outcome, assignment_candidate_key="peer-b@v1",
        namespace="ns-1",
    )


def test_publish_does_not_update_policy_and_valid_later_channel_updates_once():
    adapter = DelayedPolicyAdapter(policy(), namespace="ns-1")
    before = adapter._state_digest()
    receipt = adapter.publish(offer(), source_gate=gate())
    assert receipt.state_digest_before == before == receipt.state_digest_after
    assert receipt.policy_updates_before == receipt.policy_updates_after == 0
    selection = choose(adapter)
    assert adapter.apply_later_credit(channel(selection)) == "UPDATED_ONCE"
    assert adapter.policy.updates == 1
    assert adapter.apply_later_credit(channel(selection)) == "NOOP_DUPLICATE"


def test_same_assignment_cannot_use_an_alternate_outcome():
    adapter = DelayedPolicyAdapter(policy(), namespace="ns-1")
    adapter.publish(offer(), source_gate=gate())
    selection = choose(adapter)
    adapter.apply_later_credit(channel(selection))
    alternate = LaterChannelPayload(
        credit=LaterCredit.build(assignment_id="assignment-1", source_evidence_id="e-source", later_outcome_id="o-other", later_quality=0.0),
        feedback=Feedback("fb-2", selection.event_id, "recipient_judgment", 0.0, 4.0, delay=2.0, action="reject"),
        target_outcome_id="o-other", assignment_candidate_key="peer-b@v1", namespace="ns-1",
    )
    try:
        adapter.apply_later_credit(alternate)
    except ValueError as exc:
        assert "already has a different" in str(exc)
    else:
        raise AssertionError("alternate outcome must be rejected")
    assert adapter.policy.updates == 1


def test_same_credit_with_mutated_feedback_is_not_a_duplicate():
    adapter = DelayedPolicyAdapter(policy(), namespace="ns-1")
    adapter.publish(offer(), source_gate=gate())
    selection = choose(adapter)
    adapter.apply_later_credit(channel(selection))
    mutated = LaterChannelPayload(
        credit=credit(),
        feedback=Feedback("fb-1", selection.event_id, "recipient_judgment", 0.0, 4.0, action="reject"),
        target_outcome_id="o-later", assignment_candidate_key="peer-b@v1", namespace="ns-1",
    )
    try:
        adapter.apply_later_credit(mutated)
    except ValueError as exc:
        assert "already has a different" in str(exc)
    else:
        raise AssertionError("mutated duplicate feedback must be rejected")
    assert adapter.policy.updates == 1


def test_public_and_lineage_errors_fail_closed_without_update():
    adapter = DelayedPolicyAdapter(policy(), namespace="ns-1")
    try:
        adapter.publish(offer(), source_gate=SourceGate(**{**gate().payload(), "evidence_publish_allowed": False}))
    except ValueError as exc:
        assert "does not permit" in str(exc)
    else:
        raise AssertionError("closed source gate must reject publication")
    adapter.publish(offer(), source_gate=gate())
    selection = choose(adapter)
    bad = LaterChannelPayload(
        credit=credit(),
        feedback=Feedback("fb-bad", "e-source", "recipient_judgment", 1.0, 3.0),
        target_outcome_id="o-later", assignment_candidate_key="peer-b@v1", namespace="ns-1",
    )
    try:
        adapter.apply_later_credit(bad)
    except ValueError as exc:
        assert "target policy selection" in str(exc)
    else:
        raise AssertionError("source evidence id must not be accepted as target selection")
    assert adapter.policy.updates == 0


def test_snapshot_restore_preserves_public_store_and_idempotency():
    adapter = DelayedPolicyAdapter(policy(), namespace="ns-1")
    adapter.publish(offer(), source_gate=gate())
    selection = choose(adapter)
    assert adapter.apply_later_credit(channel(selection)) == "UPDATED_ONCE"
    restored = DelayedPolicyAdapter.restore(adapter.snapshot())
    assert restored._state_digest() == adapter._state_digest()
    assert restored.apply_later_credit(channel(selection)) == "NOOP_DUPLICATE"


def test_canonical_replay_validation_binds_real_ledger_lineage_before_update():
    ledger, role_offer, assignment, target_selection, entry, registry = _ledger_and_offer()
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "c1", "o1", "role-evidence-v1", 13.0))
    adapter = DelayedPolicyAdapter(
        FeatureContextualTrustPolicy(
            dimension=2, ridge=1.0, trust_scale=1.0,
            encoder_version="hash64-v1", feature_schema="matrix-features-v1",
        ), namespace="ns-1",
    )
    adapter.publish_from_ledger(role_offer, ledger=ledger, source_gate=gate())
    adapter.policy.choose(
        event_id="policy-s1", context_key="ctx", selector_id="selector",
        candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(100.0, 0.0), rng=__import__("numpy").random.default_rng(0),
        state_version="target", encoder_version="hash64-v1", feature_schema="matrix-features-v1",
        captured_features={"peer-a@v1": (1.0, 0.0), "peer-b@v1": (0.0, 1.0)},
    )
    validated = adapter.validate_later(
        ledger=ledger, source_gate=gate(), role_offer=role_offer,
        target_assignment=assignment, target_selection=target_selection,
        evidence_candidate_id="peer-a@v1", later_outcome_id="o1",
        history_entry=entry, assignment_read_cut=5, target_decision_index=6,
        target_arrival_index=12, candidate_registry_digest=registry,
        target_policy_event_id="policy-s1",
        feedback=Feedback("target-feedback", "policy-s1", "recipient_judgment", 1.0, 12.0,
                          delay=6.0, action="accept", disposition="eligible", provenance="public"),
    )
    assert isinstance(validated, ValidatedLaterCredit)
    assert validated.replay_status == "PASS"
    assert adapter.apply_validated_later_credit(validated) == "UPDATED_ONCE"
    assert adapter.policy.updates == 1


def test_canonical_validation_rejects_label_mutation_before_policy_update():
    ledger, role_offer, assignment, target_selection, entry, registry = _ledger_and_offer()
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "c1", "o1", "role-evidence-v1", 13.0))
    adapter = DelayedPolicyAdapter(
        FeatureContextualTrustPolicy(
            dimension=2, ridge=1.0, trust_scale=1.0,
            encoder_version="hash64-v1", feature_schema="matrix-features-v1",
        ), namespace="ns-1",
    )
    adapter.publish_from_ledger(role_offer, ledger=ledger, source_gate=gate())
    adapter.policy.choose(
        event_id="policy-s1", context_key="ctx", selector_id="selector",
        candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(100.0, 0.0), rng=__import__("numpy").random.default_rng(0),
        state_version="target", encoder_version="hash64-v1", feature_schema="matrix-features-v1",
        captured_features={"peer-a@v1": (1.0, 0.0), "peer-b@v1": (0.0, 1.0)},
    )
    try:
        adapter.validate_later(
            ledger=ledger, source_gate=gate(), role_offer=role_offer,
            target_assignment=assignment, target_selection=target_selection,
            evidence_candidate_id="peer-a@v1", later_outcome_id="o1",
            history_entry=entry, assignment_read_cut=5, target_decision_index=6,
            target_arrival_index=12, candidate_registry_digest=registry,
            target_policy_event_id="policy-s1",
            feedback=Feedback("target-feedback", "policy-s1", "recipient_judgment", 0.0, 12.0,
                              delay=6.0, action="reject", disposition="eligible", provenance="public"),
        )
    except ValueError as exc:
        assert "does not match target recipient judgment" in str(exc)
    else:
        raise AssertionError("mutated target label must be rejected")
    assert adapter.policy.updates == 0


def test_snapshot_mutation_is_rejected_before_restore():
    adapter = DelayedPolicyAdapter(policy(), namespace="ns-1")
    adapter.publish(offer(), source_gate=gate())
    snapshot = adapter.snapshot()
    snapshot["evidence_subjects"]["e-source"] = "peer-c@v1"
    try:
        DelayedPolicyAdapter.restore(snapshot)
    except ValueError as exc:
        assert "snapshot digest" in str(exc)
    else:
        raise AssertionError("mutated snapshot must not restore")
