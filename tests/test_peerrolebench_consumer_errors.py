"""Resource errors must not become selected-only capability labels."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from peerrolebench_consumer_checks import run_checks, require_behavior_response


@pytest.mark.parametrize("error_type", ["MemoryError", "PermissionError", "BlockingIOError", "OSError"])
def test_worker_resource_error_is_unknown(error_type):
    result = run_checks(lambda _: {"ok": False, "error_type": error_type, "errno": 13})
    assert result["status"] == "UNKNOWN"
    assert not result["coverage_complete"]
    assert not result["observed_behavioral_failure"]
    assert result["checks"][0]["status"] == "UNKNOWN"
    assert all(c["status"] == "NOT_RUN" for c in result["checks"][1:])


def test_behavior_error_stays_failure():
    result = run_checks(lambda _: {"ok": False, "error_type": "ValueError", "message": "bad value"})
    assert result["status"] == "FAIL"
    assert result["observed_behavioral_failure"]


def test_known_handler_failure_remains_behavioral_response():
    response = {"ok": False, "error_type": "HandlerRetry"}
    assert require_behavior_response(response) is response


def test_resource_error_preserves_previous_behavioral_failure():
    count = 0
    def request(_):
        nonlocal count
        count += 1
        return {"ok": False, "error_type": "ValueError" if count == 1 else "MemoryError"}
    result = run_checks(request)
    assert result["status"] == "UNKNOWN"
    assert result["observed_behavioral_failure"]
    assert [c["status"] for c in result["checks"]] == ["FAIL", "UNKNOWN", "NOT_RUN", "NOT_RUN"]
