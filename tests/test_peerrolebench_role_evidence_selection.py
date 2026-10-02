from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import ContextualTrustPolicy  # noqa: E402
from peerrolebench_pipe3_full_chain_qualification import registry  # noqa: E402
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, make_offer  # noqa: E402
from peerrolebench_role_evidence_offer import (  # noqa: E402
    PublicRoleEvidence, build_role_evidence_from_ledger, make_role_evidence_offer,
)
from peerrolebench_role_evidence_selection import (  # noqa: E402
    commit_role_evidence_selection, preview_role_evidence_selection,
)
from peerrolebench_role_evidence_scorer import score_role_evidence  # noqa: E402


DIGEST = "a" * 64
OUTPUT = "b" * 64


def _common(**overrides):
    values = dict(
        selector_id="peer-a", base_scores=(100.0, -100.0), rng=np.random.default_rng(7),
        state_version="state", encoder_version="encoder", feature_schema="pipe3",
        policy_version="contextual-v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=1.0,
        read_cut=1, decision_index=1, captured_features=None,
    )
    values.update(overrides)
    return values


def _source(boundary):
    first_offer = make_offer(
        offer_id="source-offer", task_id="task", task_index=0, role="producer",
        context_key="PIPE3:0", candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(), evidence_version="role-v1", available_index=0,
    )
    first = boundary.choose_and_seal(
        offer=first_offer, native_selection_id="s0", role="producer",
        base_scores=(100.0, -100.0), rng=np.random.default_rng(3), selector_id="peer-a",
        state_version="state0", encoder_version="encoder", feature_schema="pipe3",
        policy_version="contextual-v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=0.0,
        read_cut=0, decision_index=0, consume_evidence=False,
    )
    boundary.ledger.record_task_start("task", 0)
    boundary.ledger.record_delivery(Delivery("d0", "task", first.native_selection.chosen_peer_id,
                                             "peer-a", DIGEST, "src", 0, "s0"))
    boundary.ledger.record_producer_score(ProducerScore("q0", "d0", DIGEST, "score-v1", "PASS", 1,
                                                        1.0, OUTPUT, True, True))
    boundary.ledger.record_judgment(RecipientJudgment("j0", "d0", "peer-a", "accept_with_rework", DIGEST))
    boundary.ledger.record_action(ConsumerAction("a0", "d0", "peer-a", True, DIGEST, OUTPUT, action="repair"))
    boundary.ledger.record_outcome(TerminalOutcome("o0", "d0", True, "outcome-v1", 1.0, OUTPUT))
    boundary.ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "o0", "role-v1", 1.0))
    role_offer = make_role_evidence_offer(
        offer_id="role-offer", task_id="task", task_index=1, role="producer", context_key="PIPE3:1",
        candidate_keys=("peer-b@v1", "peer-c@v1"),
        evidence=(build_role_evidence_from_ledger(
            ledger=boundary.ledger, evidence_id="e0", candidate_key="peer-b@v1", role="producer",
            target_task_index=1, evidence_version="role-v1", available_index=1,
        ),),
        evidence_version="role-v1", available_index=1,
    )
    feedback_offer = make_offer(
        offer_id="feedback-offer", task_id="task", task_index=1, role="producer",
        context_key="PIPE3:1", candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=(),
        evidence_version="role-v1", available_index=1,
    )
    return role_offer, feedback_offer


def test_role_evidence_preview_commit_is_nonupdating_and_assignment_first():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    role_offer, feedback_offer = _source(boundary)
    before = boundary.policy.snapshot()
    plan = preview_role_evidence_selection(
        boundary, role_offer=role_offer, feedback_offer=feedback_offer,
        assignment_id="as1", native_selection_id="s1", **_common(),
    )
    assert boundary.policy.snapshot() == before
    assert plan.assigned_agent_id == "peer-b"
    seal = commit_role_evidence_selection(
        boundary, plan=plan, role_offer=role_offer, feedback_offer=feedback_offer,
    )
    assert boundary.policy.snapshot()["updates"] == 0
    assert seal.native_selection.chosen_peer_id == plan.assigned_agent_id
    assert seal.native_selection.propensity == plan.selection.propensity
    event_types = [row["event_type"] for row in boundary.ledger.events]
    assert event_types[-2:] == ["later_assignment", "peer_selection"]
    boundary.ledger.record_task_start("task", 1)


def test_role_evidence_commit_rolls_back_if_plan_is_stale():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    role_offer, feedback_offer = _source(boundary)
    plan = preview_role_evidence_selection(
        boundary, role_offer=role_offer, feedback_offer=feedback_offer,
        assignment_id="as1", native_selection_id="s1", **_common(),
    )
    boundary.policy.temperature = 2.0
    try:
        commit_role_evidence_selection(boundary, plan=plan, role_offer=role_offer, feedback_offer=feedback_offer)
    except ValueError as exc:
        assert "persistent policy state" in str(exc)
    else:
        raise AssertionError("stale preview must be rejected")
    assert not boundary.ledger.assignments
    assert not boundary.ledger.selections or list(boundary.ledger.selections) == ["s0"]


def test_evidence_content_mutation_does_not_change_hand_authored_overlay_choice():
    """The current seam must expose this gap instead of claiming evidence use."""
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    role_offer, feedback_offer = _source(boundary)
    common = _common(rng=np.random.default_rng(7))
    first = preview_role_evidence_selection(
        boundary, role_offer=role_offer, feedback_offer=feedback_offer,
        assignment_id="as-evidence-0", native_selection_id="s-evidence-0", **common,
    )
    row = PublicRoleEvidence(**dict(role_offer.public_evidence[0]))
    mutated_row = replace(row, quality_score=0.0)
    mutated_offer = make_role_evidence_offer(
        offer_id=role_offer.offer_id, task_id=role_offer.task_id,
        task_index=role_offer.task_index, role=role_offer.role,
        context_key=role_offer.context_key, candidate_keys=role_offer.candidate_keys,
        evidence=(mutated_row,), evidence_version=role_offer.evidence_version,
        available_index=role_offer.available_index,
        candidate_registry_digest=role_offer.candidate_registry_digest,
    )
    second = preview_role_evidence_selection(
        boundary, role_offer=mutated_offer, feedback_offer=feedback_offer,
        assignment_id="as-evidence-0", native_selection_id="s-evidence-0",
        **_common(rng=np.random.default_rng(7)),
    )
    assert first.assigned_agent_id == second.assigned_agent_id == "peer-b"
    assert first.selection.chosen_index == second.selection.chosen_index
    assert first.selection.probabilities == second.selection.probabilities
    assert first.role_offer_digest != second.role_offer_digest
    assert first.overlay_input_digest != second.overlay_input_digest


def test_judgment_score_changes_but_quality_score_is_not_read():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    role_offer, _ = _source(boundary)
    base = (0.0, 0.0)
    original = score_role_evidence(role_offer, base_scores=base, read_cut=1)
    original_row = PublicRoleEvidence(**dict(role_offer.public_evidence[0]))
    judgment_changed = make_role_evidence_offer(
        offer_id=role_offer.offer_id, task_id=role_offer.task_id,
        task_index=role_offer.task_index, role=role_offer.role,
        context_key=role_offer.context_key, candidate_keys=role_offer.candidate_keys,
        evidence=(replace(original_row, judgment="reject_redo"),),
        evidence_version=role_offer.evidence_version,
        available_index=role_offer.available_index,
        candidate_registry_digest=role_offer.candidate_registry_digest,
    )
    quality_changed = make_role_evidence_offer(
        offer_id=role_offer.offer_id, task_id=role_offer.task_id,
        task_index=role_offer.task_index, role=role_offer.role,
        context_key=role_offer.context_key, candidate_keys=role_offer.candidate_keys,
        evidence=(replace(original_row, quality_score=0.0),),
        evidence_version=role_offer.evidence_version,
        available_index=role_offer.available_index,
        candidate_registry_digest=role_offer.candidate_registry_digest,
    )
    changed = score_role_evidence(judgment_changed, base_scores=base, read_cut=1)
    unchanged = score_role_evidence(quality_changed, base_scores=base, read_cut=1)
    assert original.posterior_means == (0.5, 0.5)
    assert changed.posterior_means[0] == 1.0 / 3.0
    assert changed.scores != original.scores
    assert changed.input_digest != original.input_digest
    assert unchanged.scores == original.scores
    assert unchanged.input_digest == original.input_digest
