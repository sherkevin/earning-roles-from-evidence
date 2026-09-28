"""Pure ownership gate for producer role evidence.

The function is intentionally independent of any LLM scorer.  It consumes
operator-validated sidecars and returns eligibility only; callers provide the
actual label after this gate passes.
"""
from __future__ import annotations


def producer_feedback_eligibility(materials, producer_score, judgment, action,
                                  outcome, later_use=None):
    producer_paths = set(materials["agent_payloads"]["producer"]["writable_paths"])
    recipient_paths = set(materials["agent_payloads"]["recipient"]["writable_paths"])
    if producer_paths & recipient_paths:
        raise ValueError("producer and recipient ownership must be disjoint")
    changed = set(action.get("changed_paths", []))
    outside = changed - producer_paths - recipient_paths
    if outside:
        raise ValueError(f"changed paths outside ownership contract: {sorted(outside)}")
    producer_changed = sorted(changed & producer_paths)
    recipient_changed = sorted(changed & recipient_paths)
    q_complete = (producer_score.get("status") in {"PASS", "FAIL"}
                  and producer_score.get("coverage_complete") is True
                  and producer_score.get("decision_complete") is True)
    y_complete = (outcome.get("status") in {"PASS", "FAIL"}
                  and outcome.get("coverage_complete") is True
                  and outcome.get("decision_complete") is True)
    binding = bool(judgment.get("observed_artifact_sha256"))
    target_role = judgment.get("target_role")
    later_valid = bool(later_use and later_use.get("valid") is True)
    eligible = bool(q_complete and y_complete and target_role == "producer" and binding
                    and (producer_changed or later_valid) and not recipient_changed)
    if eligible:
        status = "ELIGIBLE"
        reason = "complete Qp/Y with producer-owned change or valid later-use evidence"
    elif recipient_changed and not producer_changed:
        status = "PENDING_ATTRIBUTION"
        reason = "recipient-owned integration change cannot label producer"
    elif producer_changed and recipient_changed:
        status = "UNKNOWN"
        reason = "mixed ownership change requires a registered counterfactual"
    elif not q_complete or not y_complete:
        status = "UNKNOWN"
        reason = "incomplete scorer or outcome coverage"
    else:
        status = "PENDING_ATTRIBUTION"
        reason = "no producer-owned change or valid later-use evidence"
    return {
        "gate_version": "pipe3-responsibility-label-v1",
        "producer_owned_paths_changed": producer_changed,
        "recipient_owned_paths_changed": recipient_changed,
        "q_complete": q_complete,
        "outcome_complete": y_complete,
        "judgment_target_role": target_role,
        "artifact_binding_present": binding,
        "later_use_valid": later_valid,
        "producer_feedback_status": status,
        "producer_feedback_eligible": eligible,
        "reason": reason,
        "policy_update_allowed": False,
        "scientific_claim_allowed": False,
    }
