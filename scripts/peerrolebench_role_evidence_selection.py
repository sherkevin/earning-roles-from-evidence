"""Role-evidence overlay preview and assignment-before-selection commit.

This is an additive seam.  The existing ``AssignmentEvidenceOffer`` remains
the policy feedback/update channel; ``RoleEvidenceOffer`` is only a public
read input for a future assignment policy.  A plan previews the exact choice
under an overlay score vector without mutating the persistent policy.  Commit
records the native ``LaterAssignment`` first and then replays the previewed
choice through the existing selection boundary, so no second sample is taken.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

from peer_role_protocol_20260925 import LaterAssignment
from peerrolebench_assignment_attestation import AssignmentEvidenceOffer
from peerrolebench_baseline_policies import Selection
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, SelectionSeal, _digest
from peerrolebench_role_evidence_scorer import (
    RoleEvidenceScore,
    RoleEvidenceScoreConfig,
    score_role_evidence,
)
from peerrolebench_role_evidence_offer import RoleEvidenceOffer
from peerrolebench_selection_preview import FixedChoiceRNG, preview_selection


VERSION = "role-evidence-selection-plan-v1"


def _state_digest(policy: Any) -> str:
    return _digest(policy.snapshot())


def _base_candidate(candidate_key: str) -> str:
    return str(candidate_key).split("@", 1)[0]


@dataclass(frozen=True)
class SelectionPlan:
    """Immutable preview receipt used by the later assignment commit."""

    plan_version: str
    assignment_id: str
    native_selection_id: str
    task_id: str
    task_index: int
    role: str
    selector_id: str
    candidate_keys: tuple[str, ...]
    assigned_agent_id: str
    evidence_ids: tuple[str, ...]
    feedback_offer_id: str
    role_offer_id: str
    role_offer_digest: str
    overlay_input_digest: str
    persistent_state_digest: str
    base_scores: tuple[float, ...]
    selection: Selection
    state_version: str
    encoder_version: str
    feature_schema: str
    policy_version: str
    base_score_version: str
    rng_algorithm: str
    rng_draw: int
    selected_at: float
    read_cut: int
    decision_index: int
    captured_features: tuple[tuple[str, tuple[float, ...]], ...] = ()

    def payload(self) -> dict[str, Any]:
        return {
            "plan_version": self.plan_version,
            "assignment_id": self.assignment_id,
            "native_selection_id": self.native_selection_id,
            "task_id": self.task_id,
            "task_index": int(self.task_index),
            "role": self.role,
            "selector_id": self.selector_id,
            "candidate_keys": list(self.candidate_keys),
            "assigned_agent_id": self.assigned_agent_id,
            "evidence_ids": list(self.evidence_ids),
            "feedback_offer_id": self.feedback_offer_id,
            "role_offer_id": self.role_offer_id,
            "role_offer_digest": self.role_offer_digest,
            "overlay_input_digest": self.overlay_input_digest,
            "persistent_state_digest": self.persistent_state_digest,
            "base_scores": list(self.base_scores),
            "selection": asdict(self.selection),
            "state_version": self.state_version,
            "encoder_version": self.encoder_version,
            "feature_schema": self.feature_schema,
            "policy_version": self.policy_version,
            "base_score_version": self.base_score_version,
            "rng_algorithm": self.rng_algorithm,
            "rng_draw": int(self.rng_draw),
            "selected_at": float(self.selected_at),
            "read_cut": int(self.read_cut),
            "decision_index": int(self.decision_index),
            "captured_features": [
                [key, list(values)] for key, values in self.captured_features
            ],
        }


def _validate_offer_pair(role_offer: RoleEvidenceOffer, feedback_offer: AssignmentEvidenceOffer,
                         *, read_cut: int) -> None:
    if role_offer.task_id != feedback_offer.task_id or role_offer.task_index != feedback_offer.task_index:
        raise ValueError("role and feedback offers must identify the same target task")
    if role_offer.role != feedback_offer.role or role_offer.context_key != feedback_offer.context_key:
        raise ValueError("role and feedback offer role/context mismatch")
    if tuple(role_offer.candidate_keys) != tuple(feedback_offer.candidate_keys):
        raise ValueError("role and feedback offers must preserve the same candidate menu")
    if int(read_cut) < int(role_offer.available_index):
        raise ValueError("role evidence is unavailable at the read cut")
    if int(read_cut) < int(feedback_offer.available_index):
        raise ValueError("feedback offer is unavailable at the read cut")


def preview_role_evidence_selection(
    boundary: Pipe3SelectionBoundary,
    *,
    role_offer: RoleEvidenceOffer,
    feedback_offer: AssignmentEvidenceOffer,
    assignment_id: str,
    native_selection_id: str,
    selector_id: str,
    base_scores: Sequence[float],
    rng: Any,
    state_version: str,
    encoder_version: str,
    feature_schema: str,
    policy_version: str,
    base_score_version: str,
    rng_algorithm: str,
    rng_draw: int,
    selected_at: float,
    read_cut: int,
    decision_index: int,
    captured_features: Mapping[str, Sequence[float]] | None = None,
) -> SelectionPlan:
    """Preview a role-evidence-informed choice without persistent mutation."""
    _validate_offer_pair(role_offer, feedback_offer, read_cut=read_cut)
    if role_offer.candidate_registry_digest is not None and role_offer.candidate_registry_digest != boundary.registry_digest:
        raise ValueError("role evidence offer is bound to a different candidate registry")
    if not assignment_id or not native_selection_id:
        raise ValueError("assignment and selection identifiers are required")
    scores = tuple(float(value) for value in base_scores)
    if len(scores) != len(role_offer.candidate_keys) or not all(math.isfinite(value) for value in scores):
        raise ValueError("overlay scores must align with the role-evidence candidate menu")
    before = _state_digest(boundary.policy)
    selection = preview_selection(
        boundary, offer=feedback_offer, native_selection_id=native_selection_id,
        selector_id=selector_id, role=role_offer.role, base_scores=scores, rng=rng,
        state_version=state_version, encoder_version=encoder_version,
        feature_schema=feature_schema, policy_version=policy_version,
        base_score_version=base_score_version, rng_algorithm=rng_algorithm,
        rng_draw=rng_draw, selected_at=selected_at, read_cut=read_cut,
        decision_index=decision_index, captured_features=captured_features,
    )
    selected_key = selection.chosen.key
    selected_evidence = tuple(sorted(
        str(row["evidence_id"])
        for row in role_offer.public_evidence
        if _base_candidate(str(row["candidate_key"])) == selection.chosen.candidate_id
    ))
    if not selected_evidence:
        raise ValueError("preview selected a candidate without published role evidence")
    overlay_input_digest = _digest({
        "role_offer": role_offer.payload(),
        "overlay_scores": list(scores),
        "selected_key": selected_key,
    })
    return SelectionPlan(
        plan_version=VERSION, assignment_id=assignment_id,
        native_selection_id=native_selection_id, task_id=role_offer.task_id,
        task_index=int(role_offer.task_index), role=role_offer.role,
        selector_id=selector_id, candidate_keys=tuple(role_offer.candidate_keys),
        assigned_agent_id=selection.chosen.candidate_id,
        evidence_ids=selected_evidence, feedback_offer_id=feedback_offer.offer_id,
        role_offer_id=role_offer.offer_id, role_offer_digest=role_offer.bundle_digest,
        overlay_input_digest=overlay_input_digest, persistent_state_digest=before,
        base_scores=scores, selection=selection, state_version=state_version,
        encoder_version=encoder_version, feature_schema=feature_schema,
        policy_version=policy_version, base_score_version=base_score_version,
        rng_algorithm=rng_algorithm, rng_draw=int(rng_draw),
        selected_at=float(selected_at), read_cut=int(read_cut),
        decision_index=int(decision_index),
        captured_features=tuple(sorted(
            (str(key), tuple(float(value) for value in values))
            for key, values in (captured_features or {}).items()
        )),
    )


def preview_role_evidence_selection_with_public_judgment(
    boundary: Pipe3SelectionBoundary,
    *,
    role_offer: RoleEvidenceOffer,
    feedback_offer: AssignmentEvidenceOffer,
    base_scores: Sequence[float],
    read_cut: int,
    scorer_config: RoleEvidenceScoreConfig | None = None,
    **kwargs: Any,
) -> tuple[SelectionPlan, RoleEvidenceScore]:
    """Preview a choice using the opt-in public-judgment comparator.

    The scorer is stateless and produces the overlay before the existing
    preview transaction.  The returned score receipt must be persisted by the
    caller alongside the selection; this function does not mutate policy,
    ledger, or RNG state beyond the existing preview contract.
    """

    score = score_role_evidence(
        role_offer, base_scores=base_scores, read_cut=read_cut,
        config=scorer_config,
    )
    plan = preview_role_evidence_selection(
        boundary, role_offer=role_offer, feedback_offer=feedback_offer,
        base_scores=score.scores, read_cut=read_cut, **kwargs,
    )
    return plan, score


def commit_role_evidence_selection(
    boundary: Pipe3SelectionBoundary,
    *,
    plan: SelectionPlan,
    role_offer: RoleEvidenceOffer,
    feedback_offer: AssignmentEvidenceOffer,
) -> SelectionSeal:
    """Commit one reserved plan as assignment then exact native selection."""
    _validate_offer_pair(role_offer, feedback_offer, read_cut=plan.read_cut)
    if role_offer.candidate_registry_digest is not None and role_offer.candidate_registry_digest != boundary.registry_digest:
        raise ValueError("role evidence offer is bound to a different candidate registry")
    if role_offer.offer_id != plan.role_offer_id or role_offer.bundle_digest != plan.role_offer_digest:
        raise ValueError("role evidence offer changed after preview")
    if feedback_offer.offer_id != plan.feedback_offer_id:
        raise ValueError("feedback offer changed after preview")
    if _state_digest(boundary.policy) != plan.persistent_state_digest:
        raise ValueError("persistent policy state changed after preview")
    if tuple(feedback_offer.candidate_keys) != plan.candidate_keys:
        raise ValueError("candidate menu changed after preview")
    if plan.selection.chosen.candidate_id != plan.assigned_agent_id:
        raise ValueError("plan assigned subject differs from previewed choice")
    if not math.isclose(plan.selection.propensity, plan.selection.probabilities[plan.selection.chosen_index], abs_tol=1e-12):
        raise ValueError("plan propensity is inconsistent with preview")
    if not all(
        any(str(row["evidence_id"]) == evidence_id and
            _base_candidate(str(row["candidate_key"])) == plan.assigned_agent_id
            for row in role_offer.public_evidence)
        for evidence_id in plan.evidence_ids
    ):
        raise ValueError("plan evidence subject does not match assigned peer")

    policy_state = deepcopy(boundary.policy.__dict__)
    ledger_state = deepcopy(boundary.ledger.__dict__)
    selections_state = deepcopy(boundary.selections)
    native_rows_state = deepcopy(boundary.native_manifest_rows)
    auxiliary_rows_state = deepcopy(boundary.auxiliary_manifest_rows)
    assignment = LaterAssignment(
        plan.assignment_id, plan.task_id, plan.task_index, plan.assigned_agent_id,
        plan.role, tuple(plan.evidence_ids), plan.selection.propensity,
    )
    try:
        boundary.ledger.record_assignment(assignment)
        features = {key: values for key, values in plan.captured_features}
        seal = boundary.choose_and_seal(
            offer=feedback_offer, native_selection_id=plan.native_selection_id,
            selector_id=plan.selector_id, role=plan.role, base_scores=plan.base_scores,
            rng=FixedChoiceRNG(plan.selection), state_version=plan.state_version,
            encoder_version=plan.encoder_version, feature_schema=plan.feature_schema,
            policy_version=plan.policy_version, base_score_version=plan.base_score_version,
            rng_algorithm=plan.rng_algorithm, rng_draw=plan.rng_draw,
            selected_at=plan.selected_at, read_cut=plan.read_cut,
            decision_index=plan.decision_index, consume_evidence=False,
            captured_features=features,
        )
        if seal.native_selection.chosen_peer_id != plan.assigned_agent_id:
            raise AssertionError("commit changed the reserved candidate")
        if not math.isclose(seal.native_selection.propensity, plan.selection.propensity, abs_tol=1e-12):
            raise AssertionError("commit changed the reserved propensity")
        return seal
    except Exception:
        boundary.policy.__dict__.clear()
        boundary.policy.__dict__.update(policy_state)
        boundary.ledger.__dict__.clear()
        boundary.ledger.__dict__.update(ledger_state)
        boundary.selections.clear()
        boundary.selections.update(selections_state)
        boundary.native_manifest_rows[:] = native_rows_state
        boundary.auxiliary_manifest_rows[:] = auxiliary_rows_state
        raise


__all__ = [
    "SelectionPlan", "VERSION", "commit_role_evidence_selection",
    "preview_role_evidence_selection", "preview_role_evidence_selection_with_public_judgment",
]
