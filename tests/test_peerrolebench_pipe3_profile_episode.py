from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from peerrolebench_pipe3_profile_episode_qualification import run


def test_pipe3_profile_episode_two_authored_controls(tmp_path: Path):
    result = run(tmp_path)
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["real_api_calls"] == result["gpu_jobs"] == 0
    assert len(result["cases"]) == 2
    producer_case, recipient_case = result["cases"]
    assert producer_case["case"] == "producer_fix"
    assert producer_case["eligibility"]["producer_feedback_status"] == "ELIGIBLE"
    assert producer_case["action"]["changed_paths"] == ["producer.py"]
    assert producer_case["profile"] is not None
    assert producer_case["assignment_trace"][-1]["event"] == "task_started"
    assert recipient_case["case"] == "recipient_fix"
    assert recipient_case["eligibility"]["producer_feedback_status"] == "PENDING_ATTRIBUTION"
    assert recipient_case["action"]["changed_paths"] == ["processor.py"]
    assert recipient_case["profile"] is None
    assert recipient_case["assignment_trace"] is None
