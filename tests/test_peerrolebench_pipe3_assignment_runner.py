import json
from pathlib import Path

from peerrolebench_pipe3_assignment_runner_qualification import run


def test_pipe3_runner_boundary_qualification(tmp_path: Path):
    result = run(tmp_path)
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["real_api_calls"] == 0
    assert result["gpu_jobs"] == 0
    assert result["policy_read_trace_mode"] == "recorded_public_input_digest"
    assert result["isolated_policy_trace"] is False
    assert result["trace_events"] == [
        "offer_emitted", "profile_consumed", "selection_sealed", "task_started"
    ]
    trace = [json.loads(line) for line in (tmp_path / "trace.jsonl").read_text().splitlines()]
    assert [item["event"] for item in trace] == result["trace_events"]
    assert all(item["isolated_policy_trace"] is False for item in trace)
