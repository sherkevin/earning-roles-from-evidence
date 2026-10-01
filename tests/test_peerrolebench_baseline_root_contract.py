from pathlib import Path
import sys
import math

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_contract import BASELINE_ARM_SPECS, COST_FIELDS  # noqa: E402
from peerrolebench_baseline_root_contract import (  # noqa: E402
    LiveRuntimeBinding,
    RootRunnerManifest,
    feedback_denominators,
    validate_assignment_before_start,
    validate_live_root_receipt,
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


def _manifest(**overrides):
    payload = {
        "root_id": "PIPE3_stream_processing",
        "root_commit": "d" * 40,
        "source_digest": "a" * 64,
        "generator_digest": "b" * 64,
        "scorer_digest": "c" * 64,
        "schedule_digest": "d" * 64,
        "rng_schedule_digest": "f" * 64,
        "registry_digest": "e" * 64,
        "seed_split": (0, 1),
        "arm_names": ("uniform", "no_update", "raw_acceptance", "terminal_only", "contextual_trust", "pooled_controller", "RARE"),
        "rng_algorithm": "numpy-pcg64",
        "visibility_rule": "canonical_schedule_prefix_v1",
        "max_episode_attempts": 4,
        "max_api_calls": 12,
        "max_wall_seconds": 3600.0,
    }
    payload.update(overrides)
    return RootRunnerManifest(**payload)


def test_root_manifest_seals_identity_split_budget_and_digest():
    manifest = _manifest()
    payload = manifest.validate()
    assert payload["contract_version"] == "artifactrole-root-runner-v1"
    assert payload["manifest_digest"] == manifest.digest()
    with pytest.raises(ValueError, match="arm order"):
        _manifest(arm_names=("RARE",)).validate()
    with pytest.raises(ValueError, match="seed_split"):
        _manifest(seed_split=(1, 0)).validate()
    with pytest.raises(ValueError, match="budgets"):
        _manifest(max_api_calls=-1).validate()
    with pytest.raises(ValueError, match="budgets"):
        _manifest(max_wall_seconds=math.nan).validate()


def test_public_prefix_requires_complete_schedule_prefix():
    schedule = _schedule()
    assert validate_public_prefix(schedule, ["f0"], read_cut=1)["prefix_complete"]
    with pytest.raises(ValueError, match="strictly ordered"):
        validate_public_prefix((schedule[1], schedule[0]), ["f1", "f0"], read_cut=3)
    with pytest.raises(ValueError, match="omits arrived"):
        validate_public_prefix(schedule, [], read_cut=1)
    with pytest.raises(ValueError, match="future feedback"):
        validate_public_prefix(schedule, ["f0", "f1"], read_cut=1)
    with pytest.raises(ValueError, match="duplicate"):
        validate_public_prefix(schedule, ["f0", "f0"], read_cut=1)
    with pytest.raises(ValueError, match="order"):
        validate_public_prefix(schedule, ["f1", "f0"], read_cut=3)


def test_denominators_make_selected_unknown_and_unselected_explicit():
    rows = [
        {"feedback_id": "f0", "selected": True, "classification": "eligible"},
        {"feedback_id": "f1", "selected": True, "classification": "unknown"},
        {"feedback_id": "f2", "selected": True, "classification": "ignored"},
        {"feedback_id": "f3", "selected": False, "classification": "pending"},
    ]
    result = feedback_denominators(rows)
    assert result == {
        "n_feedback_rows": 4, "n_selected": 3, "n_unselected": 1,
        "n_eligible": 1, "n_unknown": 1, "n_ignored": 1,
        "n_duplicate": 0, "n_pending": 1,
        "n_selected_eligible": 1, "n_selected_unknown": 1, "n_selected_ignored": 1,
        "n_selected_duplicate": 0, "n_selected_pending": 0,
        "n_unselected_eligible": 0, "n_unselected_unknown": 0, "n_unselected_ignored": 0,
        "n_unselected_duplicate": 0, "n_unselected_pending": 1,
    }
    with pytest.raises(ValueError, match="invalid feedback"):
        feedback_denominators([{"feedback_id": "f0", "selected": True, "classification": "label_guess"}])
    with pytest.raises(ValueError, match="selected must be boolean"):
        feedback_denominators([{"feedback_id": "f0", "selected": "false", "classification": "eligible"}])


def test_assignment_must_be_sealed_before_task_start():
    assert validate_assignment_before_start(_assignment())["sealed_before_start"]
    with pytest.raises(ValueError, match="before task start"):
        validate_assignment_before_start(_assignment(decision_index=3))


def test_root_receipt_combines_gates_without_scientific_claim():
    rows = [
        {"feedback_id": "f0", "selected": True, "classification": "unknown"},
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


def test_root_receipt_binds_denominator_rows_to_prefix():
    with pytest.raises(ValueError, match="denominator rows"):
        validate_root_receipt(
            schedule=_schedule(), observed_feedback_ids=["f0"], read_cut=1,
            feedback_rows=[{"feedback_id": "other", "selected": True, "classification": "unknown"}],
            assignment=_assignment(), cost_ledger=_costs(), require_measured_cost=False,
        )


def _live_binding(**overrides):
    payload = {
        "arm_name": "contextual_trust",
        "material_manifest_digest": "1" * 64,
        "task_contract_digest": "2" * 64,
        "sandbox_runtime_digest": "3" * 64,
        "scorer_config_digest": "4" * 64,
        "worker_limits_digest": "5" * 64,
        "policy_namespace_digest": "6" * 64,
        "candidate_source_digests": (("agent-a@v1", "7" * 64), ("agent-b@v1", "8" * 64)),
    }
    payload.update(overrides)
    return LiveRuntimeBinding(**payload)


def test_live_binding_seals_material_runtime_and_candidate_snapshots():
    binding = _live_binding()
    payload = binding.validate()
    assert payload["binding_version"] == "artifactrole-live-binding-v1"
    assert payload["binding_digest"] == binding.digest()
    with pytest.raises(ValueError, match="candidate source snapshots must be sorted"):
        _live_binding(candidate_source_digests=(("agent-b@v1", "8" * 64), ("agent-a@v1", "7" * 64))).validate()
    with pytest.raises(ValueError, match="64-character sha256"):
        _live_binding(worker_limits_digest="bad").validate()


def test_live_root_receipt_requires_measured_cost_and_runtime_binding():
    rows = [{"feedback_id": "f0", "selected": True, "classification": "unknown"}]
    binding = _live_binding()
    result = validate_live_root_receipt(
        schedule=_schedule(), observed_feedback_ids=["f0"], read_cut=1,
        feedback_rows=rows, assignment=_assignment(), cost_ledger=_costs(measured=True),
        live_binding=binding,
    )
    assert result["live_parity_contract"] is True
    assert result["scientific_claim_allowed"] is False
    assert result["live_binding"]["binding_digest"] == binding.digest()
    with pytest.raises(ValueError, match="not measured"):
        validate_live_root_receipt(
            schedule=_schedule(), observed_feedback_ids=["f0"], read_cut=1,
            feedback_rows=rows, assignment=_assignment(), cost_ledger=_costs(measured=False),
            live_binding=binding,
        )
