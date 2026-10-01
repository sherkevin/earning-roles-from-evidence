"""Zero-call root-runner checks shared by every baseline arm.

The policy matrix runner validates one hand-authored offer at a time.  A live
root runner additionally has to prove that an offer contains the complete
public prefix at its read cut, that denominators are not inferred later, and
that assignment is sealed before task execution.  These helpers are pure
validators so they can be used by both the ArtifactRole runner and offline
replay without introducing model calls.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from peerrolebench_baseline_contract import COST_FIELDS, validate_cost_ledger
from peerrolebench_event_time_schedule import ArrivalAssignment


ROOT_CONTRACT_VERSION = "artifactrole-root-runner-v1"
FEEDBACK_CLASSES = ("eligible", "unknown", "ignored", "duplicate", "pending")


def validate_public_prefix(
    schedule: Sequence[ArrivalAssignment],
    observed_feedback_ids: Sequence[str],
    *,
    read_cut: int,
) -> dict[str, Any]:
    """Require exactly the schedule prefix visible at ``read_cut``.

    A caller may intentionally filter a row only after it has been classified
    by the denominator contract; it may not silently omit a row from the
    public prefix before classification.
    """

    if read_cut < 0:
        raise ValueError("read_cut must be non-negative")
    schedule_ids = [str(row.feedback_id) for row in schedule]
    if len(schedule_ids) != len(set(schedule_ids)):
        raise ValueError("schedule contains duplicate feedback ids")
    expected = [str(row.feedback_id) for row in schedule if int(row.arrival_index) <= read_cut]
    observed = [str(item) for item in observed_feedback_ids]
    if len(observed) != len(set(observed)):
        raise ValueError("observed public prefix contains duplicate feedback ids")
    future = sorted(set(observed) - set(expected))
    missing = sorted(set(expected) - set(observed))
    unknown = sorted(set(observed) - set(schedule_ids))
    if unknown:
        raise ValueError(f"observed feedback is outside frozen schedule: {unknown}")
    if future:
        raise ValueError(f"future feedback visible before read cut: {future}")
    if missing:
        raise ValueError(f"public prefix omits arrived feedback: {missing}")
    return {
        "contract_version": ROOT_CONTRACT_VERSION,
        "read_cut": int(read_cut),
        "expected_feedback_ids": expected,
        "observed_feedback_ids": observed,
        "prefix_complete": True,
    }


def feedback_denominators(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    """Compute explicit total/selected/eligible/UNKNOWN denominators."""

    counts = Counter({
        "n_feedback_rows": 0, "n_selected": 0, "n_unselected": 0,
        "n_eligible": 0, "n_unknown": 0, "n_ignored": 0,
        "n_duplicate": 0, "n_pending": 0,
    })
    for row in rows:
        counts["n_feedback_rows"] += 1
        selected = bool(row.get("selected", False))
        counts["n_selected" if selected else "n_unselected"] += 1
        classification = str(row.get("classification", ""))
        if classification not in FEEDBACK_CLASSES:
            raise ValueError(f"invalid feedback classification={classification!r}")
        counts[f"n_{classification}"] += 1
    if counts["n_feedback_rows"] != counts["n_selected"] + counts["n_unselected"]:
        raise AssertionError("selected/unselected denominator does not sum to total")
    if counts["n_feedback_rows"] != sum(counts[f"n_{name}"] for name in FEEDBACK_CLASSES):
        raise AssertionError("feedback classification denominator does not sum to total")
    return dict(counts)


def validate_assignment_before_start(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the execution-before-selection boundary for later assignment."""

    required = {
        "assignment_id", "evidence_offer_id", "candidate_key", "selection_event_id",
        "decision_index", "task_start_index", "menu_digest", "assignment_digest",
    }
    missing = sorted(required - set(receipt))
    if missing:
        raise ValueError(f"assignment receipt missing fields={missing}")
    if int(receipt["decision_index"]) >= int(receipt["task_start_index"]):
        raise ValueError("assignment must be sealed before task start")
    if not str(receipt["assignment_digest"]):
        raise ValueError("assignment digest is required")
    if not str(receipt["menu_digest"]):
        raise ValueError("menu digest is required")
    return {
        "contract_version": ROOT_CONTRACT_VERSION,
        "assignment_id": str(receipt["assignment_id"]),
        "evidence_offer_id": str(receipt["evidence_offer_id"]),
        "candidate_key": str(receipt["candidate_key"]),
        "selection_event_id": str(receipt["selection_event_id"]),
        "decision_index": int(receipt["decision_index"]),
        "task_start_index": int(receipt["task_start_index"]),
        "menu_digest": str(receipt["menu_digest"]),
        "assignment_digest": str(receipt["assignment_digest"]),
        "sealed_before_start": True,
    }


def validate_root_receipt(
    *,
    schedule: Sequence[ArrivalAssignment],
    observed_feedback_ids: Sequence[str],
    read_cut: int,
    feedback_rows: Sequence[Mapping[str, Any]],
    assignment: Mapping[str, Any],
    cost_ledger: Mapping[str, Mapping[str, Mapping[str, Any]]],
    require_measured_cost: bool,
) -> dict[str, Any]:
    prefix = validate_public_prefix(schedule, observed_feedback_ids, read_cut=read_cut)
    denominators = feedback_denominators(feedback_rows)
    assignment_receipt = validate_assignment_before_start(assignment)
    normalized_cost = validate_cost_ledger(cost_ledger, require_measured=require_measured_cost)
    return {
        "contract_version": ROOT_CONTRACT_VERSION,
        "prefix": prefix,
        "denominators": denominators,
        "assignment": assignment_receipt,
        "cost_ledger": normalized_cost,
        "cost_fields": list(COST_FIELDS),
        "scientific_claim_allowed": False,
    }


__all__ = [
    "FEEDBACK_CLASSES", "ROOT_CONTRACT_VERSION", "feedback_denominators",
    "validate_assignment_before_start", "validate_public_prefix", "validate_root_receipt",
]
