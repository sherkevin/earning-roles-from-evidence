"""Responsibility-safe feedback gate for the PIPE2 candidate root.

This is a zero-call contract, not a learner.  It prevents the common mistake
of turning a recipient's repair of its own integration files into a producer
label.  A producer label is admitted only when an independent producer score,
the recipient's sealed judgment, actual artifact use, and a complete terminal
outcome all bind to the same delivery digest.  Rework, rejection, mixed edits,
or incomplete coverage remain pending/unknown and cannot update a policy.
"""

from __future__ import annotations

from typing import Any, Mapping


JUDGMENTS = {"accept", "accept_with_rework", "reject_redo", "reject_reroute"}
ACTIONS = {"use", "repair", "independent_redo"}


def _complete_score(score: Mapping[str, Any], artifact_sha256: str) -> bool:
    return bool(
        score.get("status") in {"PASS", "FAIL"}
        and score.get("coverage_complete") is True
        and score.get("decision_complete") is True
        and score.get("artifact_sha256") == artifact_sha256
        and score.get("label") in {0, 1}
    )


def _complete_outcome(outcome: Mapping[str, Any], artifact_sha256: str) -> bool:
    return bool(
        outcome.get("status") in {"PASS", "FAIL"}
        and outcome.get("coverage_complete") is True
        and outcome.get("decision_complete") is True
        and outcome.get("artifact_sha256") == artifact_sha256
    )


def evaluate_pipe2_feedback(
    materials: Mapping[str, Any],
    *,
    artifact_sha256: str,
    producer_score: Mapping[str, Any],
    judgment: Mapping[str, Any],
    action: Mapping[str, Any],
    outcome: Mapping[str, Any],
) -> dict[str, Any]:
    """Return an auditable eligibility decision without mutating state.

    ``label`` is copied from the independent producer score only after the
    strict gate passes.  Terminal outcome is a completeness/use witness; it is
    never silently converted into an upstream label.
    """
    producer_paths = set(materials["agent_payloads"]["producer"]["writable_paths"])
    recipient_paths = set(materials["agent_payloads"]["recipient"]["writable_paths"])
    if producer_paths & recipient_paths:
        raise ValueError("producer and recipient ownership must be disjoint")

    changed = set(action.get("changed_paths", ()))
    outside = changed - producer_paths - recipient_paths
    if outside:
        raise ValueError(f"changed paths outside ownership contract: {sorted(outside)}")
    producer_changed = sorted(changed & producer_paths)
    recipient_changed = sorted(changed & recipient_paths)

    score_complete = _complete_score(producer_score, artifact_sha256)
    outcome_complete = _complete_outcome(outcome, artifact_sha256)
    judgment_complete = bool(
        judgment.get("decision") in JUDGMENTS
        and judgment.get("target_role") == "producer"
        and judgment.get("observed_artifact_sha256") == artifact_sha256
        and judgment.get("coverage_complete") is True
        and judgment.get("decision_complete") is True
    )
    action_complete = bool(
        action.get("consumer_action") in ACTIONS
        and action.get("delivery_sha256") == artifact_sha256
        and action.get("used_artifact") is True
    )
    direct_use = bool(
        judgment.get("decision") == "accept"
        and action.get("consumer_action") == "use"
        and not changed
    )
    eligible = bool(score_complete and judgment_complete and action_complete
                    and outcome_complete and direct_use)

    if eligible:
        status = "ELIGIBLE"
        reason = "independent producer score is bound to accepted, used, unrepaired delivery and complete outcome"
        label = int(producer_score["label"])
    elif producer_changed and recipient_changed:
        status = "UNKNOWN"
        reason = "mixed ownership edits require a registered counterfactual"
        label = None
    elif recipient_changed or judgment.get("decision") in {"accept_with_rework", "reject_redo", "reject_reroute"}:
        status = "PENDING_ATTRIBUTION"
        reason = "recipient integration/rework or rejection cannot directly label the producer"
        label = None
    elif not score_complete or not judgment_complete or not action_complete or not outcome_complete:
        status = "UNKNOWN"
        reason = "incomplete score, judgment, action, or terminal coverage"
        label = None
    else:
        status = "PENDING_ATTRIBUTION"
        reason = "strict accepted-and-used delivery gate did not pass"
        label = None

    return {
        "gate_version": "pipe2-responsibility-label-v1",
        "artifact_sha256": artifact_sha256,
        "producer_owned_paths_changed": producer_changed,
        "recipient_owned_paths_changed": recipient_changed,
        "producer_score_complete": score_complete,
        "judgment_complete": judgment_complete,
        "action_complete": action_complete,
        "outcome_complete": outcome_complete,
        "direct_unrepaired_use": direct_use,
        "feedback_status": status,
        "feedback_eligible": eligible,
        "label": label,
        "label_mapping_version": "independent-producer-score-v1" if eligible else None,
        "reason": reason,
        "policy_update_allowed": False,
        "scientific_claim_allowed": False,
    }


__all__ = ["evaluate_pipe2_feedback"]
