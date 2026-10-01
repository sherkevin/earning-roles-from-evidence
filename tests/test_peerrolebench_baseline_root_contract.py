from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_contract import BASELINE_ARM_SPECS, COST_FIELDS  # noqa: E402
from peerrolebench_baseline_root_contract import (  # noqa: E402
    feedback_denominators,
    validate_assignment_before_start,
    validate_public_prefix,
    validate_root_receipt,
)
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402


def _schedule():
    return (
        ArrivalAssignment("f0", "recipient_judgment", "j0", "selection-0", 1),
        ArrivalAssignment("f1", "terminal_outcome", "o1", "selection-0", 3),
    )


def _assignment(**overrides):
    result = {
        "assignment_id": "a0", "evidence_offer_id": "offer-0", "candidate_key": "agent-a@v1",
        "selection_event_id": "selection-1", "decision_index": 2, "task_start_index": 3,
        "menu_digest": "m" * 64, "assignment_digest": "a" * 64,
    }
    result.update(overrides)
    return result


def _costs(measured=False):
    units = {
        "producer": "seconds", "recipient": "seconds", "judge": "seconds",
        "scorer": "seconds", "selection": "seconds", "policy_update": "seconds",
        "retry": "count", "communication": "records", "repair": "count",
        "replay": "records", "state": "bytes", "api_calls": "count",
        "input_tokens": "tokens", "output_tokens": "tokens",
        "gpu_seconds": "seconds", "wall_seconds": "seconds",
    }
    return {
        spec.name: {
            field: {"value": 0.0, "measured": measured, "source": "fixture", "unit": units[field]}
            for field in COST_FIELDS
        }
        for spec in BASELINE_ARM_SPECS
    }


def test_public_prefix_requires_complete_schedule_prefix():
    schedule = _schedule()
    assert validate_public_prefix(schedule, ["f0"], read_cut=1)["prefix_complete"]
    with pytest.raises(ValueError, match="omits arrived"):
        validate_public_prefix(schedule, [], read_cut=1)
    with pytest.raises(ValueError, match="future feedback"):
        validate_public_prefix(schedule, ["f0", "f1"], read_cut=1)
    with pytest.raises(ValueError, match="duplicate"):
        validate_public_prefix(schedule, ["f0", "f0"], read_cut=1)


def test_denominators_make_selected_unknown_and_unselected_explicit():
    rows = [
        {"selected": True, "classification": "eligible"},
        {"selected": True, "classification": "unknown"},
        {"selected": True, "classification": "ignored"},
        {"selected": False, "classification": "pending"},
    ]
    result = feedback_denominators(rows)
    assert result == {
        "n_feedback_rows": 4, "n_selected": 3, "n_unselected": 1,
        "n_eligible": 1, "n_unknown": 1, "n_ignored": 1,
        "n_duplicate": 0, "n_pending": 1,
    }
    with pytest.raises(ValueError, match="invalid feedback"):
        feedback_denominators([{"selected": True, "classification": "label_guess"}])


def test_assignment_must_be_sealed_before_task_start():
    assert validate_assignment_before_start(_assignment())["sealed_before_start"]
    with pytest.raises(ValueError, match="before task start"):
        validate_assignment_before_start(_assignment(decision_index=3))


def test_root_receipt_combines_gates_without_scientific_claim():
    rows = [
        {"selected": True, "classification": "eligible"},
        {"selected": False, "classification": "unknown"},
    ]
    result = validate_root_receipt(
        schedule=_schedule(), observed_feedback_ids=["f0"], read_cut=1,
        feedback_rows=rows, assignment=_assignment(), cost_ledger=_costs(),
        require_measured_cost=False,
    )
    assert result["contract_version"] == "artifactrole-root-runner-v1"
    assert result["denominators"]["n_unknown"] == 1
    assert result["scientific_claim_allowed"] is False
    with pytest.raises(ValueError, match="not measured"):
        validate_root_receipt(
            schedule=_schedule(), observed_feedback_ids=["f0"], read_cut=1,
            feedback_rows=rows, assignment=_assignment(), cost_ledger=_costs(),
            require_measured_cost=True,
        )
