from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_structural_owner_gate_zero_call_qualification(tmp_path):
    output = tmp_path / "qualification"
    command = [sys.executable, "scripts/peerrolebench_structural_owner_gate_qualification.py",
               "--output", str(output)]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads((output / "summary.json").read_text())
    assert summary["passed"] is True
    assert summary["case_count"] == 8
    assert summary["llm_calls"] == 0
    assert summary["gpu_jobs"] == 0
    assert summary["scientific_claim_allowed"] is False


def test_structural_disagreement_is_calibration_not_censoring():
    sys.path.insert(0, str(ROOT / "scripts"))
    from peerrolebench_pipe3_material_adapter import build_materials
    from peerrolebench_pipe3_producer_scorer_v2_qualification import interfaces
    from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility
    from peerrolebench_pipe3_task_qualification import load_pipe3

    materials = build_materials(load_pipe3(0))
    assert interfaces(materials)["event_class"]
    q = {"status": "FAIL", "label": 0, "coverage_complete": True, "decision_complete": True}
    y = {"status": "PASS", "coverage_complete": True, "decision_complete": True}
    row = producer_feedback_eligibility(
        materials, q,
        {"target_role": "recipient", "target_paths": [],
         "observed_artifact_sha256": "a" * 64, "producer_defect_registered": True},
        {"changed_paths": ["producer.py"], "consumer_action": "use", "used_artifact": True}, y,
    )
    assert row["producer_feedback_status"] == "ELIGIBLE"
    assert row["structural_owner_role"] == "producer"
    assert row["judged_role_agrees"] is False
    assert "disagreement" in row["reason"]
