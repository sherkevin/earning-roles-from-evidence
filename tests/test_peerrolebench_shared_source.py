import json
import subprocess
import sys

from scripts.peerrolebench_shared_source import (
    ARM_NAMES,
    project_source_to_arms,
    validate_arm_projections,
)


def _source(gate_status="ELIGIBLE", inclusion="ITT_AND_ELIGIBLE"):
    return {
        "source_event_id": "e0", "task_id": "PIPE3", "root": "PIPE3", "seed": 0,
        "delivery_digest": "a" * 64,
        "judgment": {"decision": "accept"}, "action": {"changed_paths": []},
        "producer_score": {"status": "FAIL", "label": 0},
        "outcome": {"status": "PASS"}, "gate": {"status": gate_status},
        "cost": {"api_attempts": 2},
        "episode_status": "SOURCE_COMPLETE" if gate_status == "ELIGIBLE" else "STOPPED_PRE_TARGET",
        "gate_status": gate_status,
        "estimand_inclusion": inclusion if gate_status == "ELIGIBLE" else "ITT_ONLY",
    }


def test_projection_preserves_source_and_isolates_arm_namespace():
    rows = project_source_to_arms(_source(), ARM_NAMES)
    report = validate_arm_projections(rows)
    assert report["valid"] is True
    assert {row["policy_arm"] for row in rows} == set(ARM_NAMES)
    assert len({row["policy_namespace"] for row in rows}) == len(ARM_NAMES)


def test_projection_rejects_source_mutation():
    rows = project_source_to_arms(_source(), ARM_NAMES)
    rows[1]["outcome"]["status"] = "FAIL"
    try:
        validate_arm_projections(rows)
    except ValueError as exc:
        assert "outcome" in str(exc)
    else:
        raise AssertionError("mutated source was accepted")


def test_qualification_is_zero_call_and_passes(tmp_path):
    out = tmp_path / "qualification"
    proc = subprocess.run(
        [sys.executable, "scripts/peerrolebench_shared_source_qualification.py", "--output", str(out)],
        check=True, capture_output=True, text=True,
    )
    assert json.loads(proc.stdout)["passed"] is True
    summary = json.loads((out / "summary.json").read_text())
    assert summary["case_count"] == 6
    assert summary["llm_calls"] == 0
    assert summary["scientific_claim_allowed"] is False
