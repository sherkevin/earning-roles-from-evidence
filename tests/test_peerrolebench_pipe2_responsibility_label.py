from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_derived_material_adapter import build_derived_materials, load_derived_pipe2  # noqa: E402
from peerrolebench_pipe2_responsibility_label import evaluate_pipe2_feedback  # noqa: E402


ARTIFACT = "a" * 64


def _case(seed: int = 0, *, judgment: str = "accept", action: str = "use",
          changed: tuple[str, ...] = (), score_status: str = "PASS",
          score_label: int | None = 1, complete: bool = True) -> dict:
    materials = build_derived_materials(seed)
    return {
        "materials": materials,
        "artifact_sha256": ARTIFACT,
        "producer_score": {
            "status": score_status, "label": score_label,
            "coverage_complete": complete, "decision_complete": complete,
            "artifact_sha256": ARTIFACT,
        },
        "judgment": {
            "decision": judgment, "target_role": "producer",
            "observed_artifact_sha256": ARTIFACT,
            "coverage_complete": complete, "decision_complete": complete,
        },
        "action": {
            "consumer_action": action, "changed_paths": list(changed),
            "delivery_sha256": ARTIFACT, "used_artifact": action != "independent_redo",
        },
        "outcome": {
            "status": "PASS", "artifact_sha256": ARTIFACT,
            "coverage_complete": complete, "decision_complete": complete,
        },
    }


def _evaluate(**kwargs):
    case = _case(**kwargs)
    return evaluate_pipe2_feedback(**{key: value for key, value in case.items()
                                     if key != "materials"}, materials=case["materials"])


def test_accepted_unrepaired_use_with_complete_outcome_is_eligible():
    result = _evaluate()
    assert result["feedback_status"] == "ELIGIBLE"
    assert result["label"] == 1
    assert result["policy_update_allowed"] is False


def test_recipient_repair_is_not_an_upstream_label():
    result = _evaluate(judgment="accept_with_rework", action="repair",
                       changed=("pipeline/transform.py",))
    assert result["feedback_status"] == "PENDING_ATTRIBUTION"
    assert result["label"] is None


def test_mixed_edit_is_unknown():
    result = _evaluate(judgment="accept_with_rework", action="repair",
                       changed=("pipeline/extract.py", "pipeline/transform.py"))
    assert result["feedback_status"] == "UNKNOWN"
    assert result["label"] is None


def test_rejection_without_artifact_use_is_not_eligible():
    result = _evaluate(judgment="reject_redo", action="independent_redo",
                       changed=("pipeline/transform.py",))
    assert result["feedback_status"] == "PENDING_ATTRIBUTION"
    assert result["label"] is None


def test_incomplete_score_cannot_emit_label():
    result = _evaluate(complete=False, score_label=None, score_status="UNKNOWN")
    assert result["feedback_status"] == "UNKNOWN"
    assert result["label"] is None


def test_out_of_contract_edit_is_rejected():
    case = _case(changed=("data/expected_output.csv",))
    with pytest.raises(ValueError, match="outside ownership"):
        evaluate_pipe2_feedback(**{key: value for key, value in case.items()
                                  if key != "materials"}, materials=case["materials"])
