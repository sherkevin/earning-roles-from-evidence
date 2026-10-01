from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_two_stage_qualification import run  # noqa: E402


def test_two_stage_qualification_has_publish_then_delayed_credit(tmp_path: Path):
    result = run(tmp_path / "two-stage")
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["passed"] is True
    producer = result["cases"][0]
    assert producer["evidence_published"] is True
    assert producer["assignment_recorded"] is True
    assert producer["later_outcome_recorded"] is True
    assert producer["policy_updates"] == 1
    assert producer["duplicate_update_applied"] is False
    assert producer["replay"]["status"] == "PASS"
    recipient = result["cases"][1]
    assert recipient["evidence_published"] is False
    assert recipient["assignment_recorded"] is False
    assert recipient["policy_updates"] == 0
    assert recipient["status"] == "BLOCKED_BY_ATTRIBUTION_GATE"
