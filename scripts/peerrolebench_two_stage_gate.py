"""Two-stage responsibility/evidence/update contract.

This module is deliberately small and policy-agnostic.  It separates a
source episode that may be published as public role evidence from the later
assignment outcome that is allowed to change persistent policy state.  The
functions consume already validated scorer/action material; they do not call
an LLM or infer hidden truth.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import math
from typing import Any, Callable, Mapping

from peerrolebench_pipe3_responsibility_label import derive_structural_owner_role


# v2 closes a reachability hole found by the PIPE2 derived-root audit: an
# explicitly registered producer defect still requires direct, unrepaired
# acceptance.  The v1 receipts remain historical and are never rewritten.
VERSION = "two-stage-role-evidence-v3-structural-owner"


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _complete_score(score: Mapping[str, Any]) -> bool:
    return (
        score.get("status") in {"PASS", "FAIL"}
        and score.get("coverage_complete") is True
        and score.get("decision_complete") is True
    )


@dataclass(frozen=True)
class SourceGate:
    """The three source-side dispositions, with no later outcome leakage."""

    gate_version: str
    producer_paths_changed: tuple[str, ...]
    recipient_paths_changed: tuple[str, ...]
    q_complete: bool
    y_complete: bool
    target_role: str | None
    artifact_binding_present: bool
    later_use_valid: bool
    attribution_eligible: bool
    evidence_publish_allowed: bool
    policy_update_allowed: bool
    status: str
    reason: str
    structural_owner_role: str = "unknown"
    judged_role_agrees: bool | None = None
    judged_target_paths: tuple[str, ...] = ()

    def payload(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_source_gate(
    materials: Mapping[str, Any],
    producer_score: Mapping[str, Any],
    judgment: Mapping[str, Any],
    action: Mapping[str, Any],
    outcome: Mapping[str, Any],
    later_use: Mapping[str, Any] | None = None,
) -> SourceGate:
    """Evaluate source attribution and publication.

    ``later_use`` is recorded for audit only.  It can never make a source
    episode attributable when no producer-owned contract change exists.
    """

    producer_paths = set(materials["agent_payloads"]["producer"]["writable_paths"])
    recipient_paths = set(materials["agent_payloads"]["recipient"]["writable_paths"])
    if producer_paths & recipient_paths:
        raise ValueError("producer and recipient ownership must be disjoint")
    changed = set(action.get("changed_paths", []))
    outside = changed - producer_paths - recipient_paths
    if outside:
        raise ValueError(f"changed paths outside ownership contract: {sorted(outside)}")
    producer_changed = tuple(sorted(changed & producer_paths))
    recipient_changed = tuple(sorted(changed & recipient_paths))
    q_complete = _complete_score(producer_score)
    y_complete = (
        outcome.get("status") in {"PASS", "FAIL"}
        and outcome.get("coverage_complete") is True
        and outcome.get("decision_complete") is True
    )
    target_role = judgment.get("target_role")
    binding = bool(judgment.get("observed_artifact_sha256"))
    # A producer defect may be pre-registered by an independent objective
    # scorer.  This is distinct from a recipient rewrite: the delivered
    # producer snapshot remains the attribution subject, and any recipient
    # integration edit is accounted for separately.
    strict_attribution = "producer_defect_registered" in judgment
    producer_defect_registered = bool(judgment.get("producer_defect_registered") is True)
    producer_defect_observed = producer_score.get("status") == "FAIL" and producer_score.get("label") == 0
    # Historical qualification receipts predate the explicit defect field and
    # retain the old producer-owned change contract. Current runners always
    # send the field, so this compatibility branch cannot weaken new runs.
    if not strict_attribution:
        producer_defect_registered = bool(producer_changed and target_role == "producer" and binding)
        producer_defect_observed = True
    later_valid = bool(later_use and later_use.get("valid") is True)
    # A later outcome validates a future assignment.  It is intentionally not
    # an alternative source of producer attribution.
    direct_unrepaired_use = bool(
        judgment.get("decision") == "accept"
        and action.get("consumer_action") == "use"
        and action.get("used_artifact") is True
        and not changed
    )
    structural_owner_role = derive_structural_owner_role(
        materials, producer_score, action,
        producer_defect_registered=producer_defect_registered,
        later_use_valid=later_valid or direct_unrepaired_use,
    )
    if (not strict_attribution and producer_changed and target_role == "producer"
            and binding and not recipient_changed):
        # Historical qualification fixtures predate explicit operator-side
        # defect registration.  New live events always carry the field.
        structural_owner_role = "producer"
    judged_role_agrees = (
        target_role == structural_owner_role
        if target_role in {"producer", "recipient", "sink", "mixed"}
        and structural_owner_role != "unknown"
        else None
    )
    attribution = bool(
        q_complete and y_complete and structural_owner_role == "producer" and binding
        and producer_defect_registered and producer_defect_observed
        and (producer_changed if not strict_attribution else not producer_changed)
        and not (producer_changed and recipient_changed)
        and (direct_unrepaired_use if strict_attribution else True)
    )
    if attribution:
        status = "ELIGIBLE"
        if judged_role_agrees is False:
            reason = "structural producer ownership; judged target role disagreement retained for calibration"
        else:
            reason = "complete source Qp/Y with independently registered producer defect"
    elif producer_changed and recipient_changed:
        status = "UNKNOWN"
        reason = "mixed ownership change requires a registered counterfactual"
    elif recipient_changed and not producer_changed:
        status = "PENDING_ATTRIBUTION"
        reason = "recipient-owned integration change cannot label producer"
    elif not q_complete or not y_complete or not binding:
        status = "UNKNOWN"
        reason = "incomplete source scorer/outcome, target binding, or artifact binding"
    else:
        status = "PENDING_ATTRIBUTION"
        reason = "no producer-owned contract change; later outcome cannot create source evidence"
    return SourceGate(
        gate_version=VERSION,
        producer_paths_changed=producer_changed,
        recipient_paths_changed=recipient_changed,
        q_complete=q_complete,
        y_complete=y_complete,
        target_role=target_role,
        artifact_binding_present=binding,
        later_use_valid=later_valid,
        attribution_eligible=attribution,
        evidence_publish_allowed=attribution,
        policy_update_allowed=False,
        status=status,
        reason=reason,
        structural_owner_role=structural_owner_role,
        judged_role_agrees=judged_role_agrees,
        judged_target_paths=tuple(judgment.get("target_paths", ())),
    )


@dataclass(frozen=True)
class LaterCredit:
    assignment_id: str
    source_evidence_id: str
    later_outcome_id: str
    later_quality: float | None
    credit_digest: str

    @classmethod
    def build(
        cls,
        *,
        assignment_id: str,
        source_evidence_id: str,
        later_outcome_id: str,
        later_quality: float | None,
    ) -> "LaterCredit":
        payload = {
            "assignment_id": assignment_id,
            "source_evidence_id": source_evidence_id,
            "later_outcome_id": later_outcome_id,
            "later_quality": later_quality,
        }
        return cls(assignment_id, source_evidence_id, later_outcome_id, later_quality, _digest(payload))


def validate_later_credit(
    *,
    source_gate: SourceGate,
    assignment_id: str,
    source_evidence_id: str,
    later_outcome: Mapping[str, Any],
    assignment_consumed: bool,
    selection_matches_assignment: bool,
    assignment_agent_id: str | None = None,
    evidence_candidate_id: str | None = None,
) -> LaterCredit | None:
    """Return one delayed credit only after a later assignment/use is valid."""

    complete = (
        later_outcome.get("status") in {"PASS", "FAIL"}
        and later_outcome.get("coverage_complete") is True
        and later_outcome.get("decision_complete") is True
        and bool(later_outcome.get("outcome_id"))
    )
    if not (
        source_gate.evidence_publish_allowed
        and assignment_id
        and source_evidence_id
        and assignment_consumed
        and selection_matches_assignment
        and assignment_agent_id
        and evidence_candidate_id
        and assignment_agent_id == evidence_candidate_id
        and complete
    ):
        return None
    return LaterCredit.build(
        assignment_id=assignment_id,
        source_evidence_id=source_evidence_id,
        later_outcome_id=str(later_outcome["outcome_id"]),
        later_quality=None if later_outcome.get("quality_score") is None else float(later_outcome["quality_score"]),
    )


def derive_later_credit_from_ledger(
    *, ledger: Any, source_gate: SourceGate, assignment_id: str,
    source_evidence_id: str, evidence_candidate_id: str,
    later_outcome_id: str,
) -> LaterCredit | None:
    """Derive delayed credit from canonical ledger lineage.

    Caller booleans are intentionally not accepted here.  The assignment,
    target selection, delivery, action and outcome must all be present in the
    same append-only ledger, and the assignment subject must match the public
    evidence subject.
    """
    if not source_gate.evidence_publish_allowed:
        return None
    assignment = getattr(ledger, "assignments", {}).get(assignment_id)
    evidence = getattr(ledger, "evidence", {}).get(source_evidence_id)
    if assignment is None or evidence is None or source_evidence_id not in assignment.evidence_ids:
        return None
    expected_candidate = str(evidence_candidate_id).split("@", 1)[0]
    if assignment.agent_id != expected_candidate:
        return None
    selections = [
        selection for selection in getattr(ledger, "selections", {}).values()
        if (selection.task_id, selection.task_index) == (assignment.task_id, assignment.task_index)
    ]
    if len(selections) != 1:
        return None
    selection = selections[0]
    if selection.chosen_peer_id != assignment.agent_id:
        return None
    if not math.isclose(float(selection.propensity), float(assignment.decision_propensity), abs_tol=1e-12):
        return None
    deliveries = [
        delivery for delivery in getattr(ledger, "deliveries", {}).values()
        if (delivery.task_id, delivery.task_index) == (assignment.task_id, assignment.task_index)
        and delivery.producer_id == assignment.agent_id
        and delivery.selection_id == selection.selection_id
    ]
    if len(deliveries) != 1:
        return None
    delivery = deliveries[0]
    outcome = getattr(ledger, "outcomes", {}).get(later_outcome_id)
    if outcome is None or outcome.delivery_id != delivery.delivery_id:
        return None
    if not any(action.delivery_id == delivery.delivery_id for action in getattr(ledger, "actions", {}).values()):
        return None
    if not any(judgment.delivery_id == delivery.delivery_id for judgment in getattr(ledger, "judgments", {}).values()):
        return None
    return LaterCredit.build(
        assignment_id=assignment_id,
        source_evidence_id=source_evidence_id,
        later_outcome_id=later_outcome_id,
        later_quality=outcome.partial_score,
    )


class DelayedCreditLedger:
    """Idempotent selected-only application point for a policy updater."""

    def __init__(self) -> None:
        self.credits: dict[str, LaterCredit] = {}

    def apply_once(
        self,
        credit: LaterCredit,
        updater: Callable[[LaterCredit], None],
        *,
        snapshot: Callable[[], Any] | None = None,
        restore: Callable[[Any], None] | None = None,
    ) -> bool:
        """Apply one credit exactly once.

        ``updater`` is expected to be atomic.  When an updater touches more
        than one mutable object, callers can provide a cheap ``snapshot`` /
        ``restore`` pair so an exception cannot leave a partially applied
        policy update while the credit key remains available for retry.
        Without a rollback pair the exception is still propagated and the
        credit key is not recorded; this makes the failure explicit instead
        of silently converting it into a successful update.
        """
        key = f"{credit.assignment_id}\x1f{credit.later_outcome_id}"
        if key in self.credits:
            return False
        before = snapshot() if snapshot is not None else None
        try:
            updater(credit)
        except Exception:
            if snapshot is not None and restore is not None:
                restore(before)
            raise
        self.credits[key] = credit
        return True

    def snapshot(self) -> dict[str, Any]:
        return {
            "version": VERSION,
            "credit_count": len(self.credits),
            "credits": {key: asdict(value) for key, value in sorted(self.credits.items())},
        }


__all__ = [
    "DelayedCreditLedger",
    "LaterCredit",
    "SourceGate",
    "VERSION",
    "evaluate_source_gate",
    "derive_later_credit_from_ledger",
    "validate_later_credit",
]
