from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_live_runner_v2_qualification import run  # noqa: E402
import peerrolebench_pipe3_live_runner_v2_qualification as runner  # noqa: E402


def test_pipe3_live_runner_v2_preserves_responsibility_gate_block(tmp_path: Path):
    result = run(tmp_path / "promotion")

    assert result["status"] == "BLOCKED_BY_RESPONSIBILITY_GATE"
    assert result["passed"] is False
    assert result["real_api_calls"] == result["gpu_jobs"] == 0
    assert result["scientific_claim_allowed"] is False
    assert result["blocked_count"] == 2
    assert result["failure_count"] == 0

    for control in ("producer_owned", "recipient_owned"):
        case = next(row for row in result["cases"] if row["control"] == control)
        assert case["status"] == "BLOCKED_BY_RESPONSIBILITY_GATE"
        assert case["policy_updates"] == 0
        assert case["next_task_started"] is False
        assert case["next_outcome_recorded"] is False
        assert case["unknown_denominator"] == {
            "feedback_rows": 1, "eligible_rows": 0, "unknown_rows": 1,
        }
        assert [event["event"] for event in case["trace"]] == [
            "actor_output", "scorer_before", "action", "outcome",
            "source_offer", "policy_read", "next_selection", "promotion_blocked",
        ]
        assert (tmp_path / "promotion" / control / "config.json").exists()
        assert (tmp_path / "promotion" / control / "raw.jsonl").exists()
        assert (tmp_path / "promotion" / control / "summary.json").exists()


def test_pipe3_live_runner_v2_preserves_control_failure_receipt(tmp_path: Path, monkeypatch):
    original = runner._run_control

    def fail_recipient(control: str, **kwargs):
        if control == "recipient_owned":
            raise RuntimeError("synthetic control failure")
        return original(control, **kwargs)

    monkeypatch.setattr(runner, "_run_control", fail_recipient)
    result = runner.run(tmp_path / "failure-preservation")

    assert result["status"] == "FAILED_OFFLINE"
    assert result["passed"] is False
    assert result["failure_count"] == 1
    failure = tmp_path / "failure-preservation" / "recipient_owned" / "failure.json"
    assert failure.exists()
    assert "synthetic control failure" in failure.read_text()
    producer = next(row for row in result["cases"] if row["control"] == "producer_owned")
    assert producer["status"] == "BLOCKED_BY_RESPONSIBILITY_GATE"
