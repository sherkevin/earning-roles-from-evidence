"""Pure ownership gate for producer role evidence.

The function is intentionally independent of any LLM scorer.  It consumes
operator-validated sidecars and returns eligibility only; callers provide the
actual label after this gate passes.

The active gate uses contract-derived structural ownership for eligibility.  A
recipient model's ``target_role`` remains an observed calibration field and
cannot censor the same registered producer event merely because wording
differs across policy arms.
"""
from __future__ import annotations


VERSION = "pipe3-responsibility-label-v2-structural-owner"
OWNER_ROLES = {"producer", "recipient", "sink", "mixed", "unknown"}


def derive_structural_owner_role(materials, producer_score, action,
                                 *, producer_defect_registered=False,
                                 later_use_valid=False):
    """Derive the auditable owner from contract paths and an independent score.

    ``target_role`` is deliberately absent from this function.  It is a model
    observation, not an ownership oracle.  A producer owner requires either a
    registered producer defect with an independent Qp FAIL/0 or a valid later
    use bound to the producer contract.  Recipient-only and mixed edits remain
    non-producer evidence.
    """
    producer_paths = set(materials["agent_payloads"]["producer"]["writable_paths"])
    recipient_paths = set(materials["agent_payloads"]["recipient"]["writable_paths"])
    if producer_paths & recipient_paths:
        raise ValueError("producer and recipient ownership must be disjoint")
    changed = set(action.get("changed_paths", []))
    outside = changed - producer_paths - recipient_paths
    if outside:
        raise ValueError(f"changed paths outside ownership contract: {sorted(outside)}")
    producer_changed = changed & producer_paths
    recipient_changed = changed & recipient_paths
    if producer_changed and recipient_changed:
        return "mixed"
    if recipient_changed:
        return "recipient"
    q_fail = (producer_score.get("status") == "FAIL"
              and producer_score.get("label") == 0)
    if (producer_changed and producer_defect_registered and q_fail) or (
            not changed and producer_defect_registered and q_fail):
        return "producer"
    return "unknown"


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
    explicit_registration = "producer_defect_registered" in judgment
    producer_defect_registered = bool(judgment.get("producer_defect_registered") is True)
    # Compatibility for historical zero-call fixtures.  New live runners pass
    # the operator-side registration explicitly and therefore cannot use model
    # wording to manufacture ownership.
    if not explicit_registration:
        producer_defect_registered = bool(producer_changed and target_role == "producer" and binding)
    structural_owner_role = derive_structural_owner_role(
        materials, producer_score, action,
        producer_defect_registered=producer_defect_registered,
        later_use_valid=later_valid,
    )
    if (not explicit_registration and producer_changed and target_role == "producer"
            and binding and not recipient_changed):
        # Historical fixtures predate the operator-side defect registration
        # field.  Keep their qualification semantics isolated from new live
        # events, which always carry explicit registration.
        structural_owner_role = "producer"
    judged_role_agrees = (
        target_role == structural_owner_role
        if target_role in {"producer", "recipient", "sink", "mixed"}
        and structural_owner_role in OWNER_ROLES
        else None
    )
    direct_unrepaired_use = bool(
        action.get("consumer_action") == "use"
        and action.get("used_artifact") is True
        and not changed
    )
    eligible = bool(q_complete and y_complete and structural_owner_role == "producer" and binding
                    and (producer_changed or later_valid or
                         (explicit_registration and producer_defect_registered and direct_unrepaired_use))
                    and not recipient_changed)
    if eligible:
        status = "ELIGIBLE"
        if judged_role_agrees is False:
            reason = "structural producer ownership; judged target role disagreement retained for calibration"
        else:
            reason = "complete Qp/Y with structural producer ownership"
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
        "gate_version": VERSION,
        "producer_owned_paths_changed": producer_changed,
        "recipient_owned_paths_changed": recipient_changed,
        "q_complete": q_complete,
        "outcome_complete": y_complete,
        "judgment_target_role": target_role,
        "structural_owner_role": structural_owner_role,
        "judged_role_agrees": judged_role_agrees,
        "judged_target_paths": list(judgment.get("target_paths", [])),
        "artifact_binding_present": binding,
        "later_use_valid": later_valid,
        "producer_feedback_status": status,
        "producer_feedback_eligible": eligible,
        "reason": reason,
        "policy_update_allowed": False,
        "scientific_claim_allowed": False,
    }


__all__ = ["VERSION", "derive_structural_owner_role", "producer_feedback_eligibility"]
