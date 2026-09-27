from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import peerrolebench_producer_scorer as scorer  # noqa: E402


def _sources():
    return {
        "mqueue/__init__.py": "",
        "mqueue/config.py": "",
        "mqueue/queue.py": "class TaskQueue: pass\n",
        "mqueue/priority.py": "class PriorityTask: pass\n",
    }


@pytest.mark.parametrize("exc", [TimeoutError("rpc"), PermissionError("denied")])
def test_transport_failures_are_unknown(monkeypatch, tmp_path, exc):
    class FailingWorker:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            raise exc

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(scorer, "SandboxedWorker", FailingWorker)
    events = []
    result = scorer.run_producer_scorer(
        _sources(), {"queue": "TaskQueue", "priority": "PriorityTask"},
        "DIST1_queue_race", 0, tmp_path / "scorer", lambda kind, payload: events.append((kind, payload)),
    )
    assert result["status"] == "UNKNOWN"
    assert result["label"] is None
    assert result["transport"]["status"] in {"timeout", "error"}
    assert (tmp_path / "scorer/response.json").is_file()


def test_transport_response_is_recorded_without_secret(monkeypatch, tmp_path):
    class MalformedWorker:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def request(self, request):
            return {"ok": True, "value": {"status": "PASS"}}

    monkeypatch.setattr(scorer, "SandboxedWorker", MalformedWorker)
    result = scorer.run_producer_scorer(
        _sources(), {"queue": "TaskQueue", "priority": "PriorityTask"},
        "DIST1_queue_race", 0, tmp_path / "scorer", lambda *_: None,
    )
    assert result["status"] == "UNKNOWN"
    response = json.loads((tmp_path / "scorer/response.json").read_text())
    assert response["result"]["label"] is None
