from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_runtime_replay import replay_case  # noqa: E402


SUMMARY_PATH = ROOT / "experiments/logs/n03_pipe2_derived_root_runtime_qualification_20261003_v3/summary.json"


@pytest.fixture(scope="module")
def summary() -> dict:
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


def test_real_runtime_row_replays_to_unknown_without_fabricating_fields(summary):
    case = summary["cases"][0]
    source = {
        "seed": case["seed"],
        "producer_control": "correct_producer_control",
        "recipient_control": "correct_recipient_control",
        "fixture_status": case["fixture_status"],
        "producer": case["producer"]["correct_producer_control"],
        "recipient": case["recipient"]["correct_producer_control"]["correct_recipient_control"],
        "adoption": case["recipient"]["correct_producer_control"]["correct_recipient_control"]["artifact_adoption"],
    }
    result = replay_case(summary, source)
    assert result["gate"]["feedback_status"] == "UNKNOWN"
    assert result["label_emitted"] is None
    assert result["policy_update_allowed"] is False
    assert result["missing_fields"] == [
        "recipient_judgment", "consumer_action", "terminal_outcome",
    ]


def test_replay_rejects_root_digest_mismatch(summary):
    broken = copy.deepcopy(summary)
    broken["material_root_digest"] = "f" * 64
    case = broken["cases"][0]
    source = {
        "seed": case["seed"],
        "producer_control": "original_producer",
        "recipient_control": "original_recipient",
        "fixture_status": case["fixture_status"],
        "producer": case["producer"]["original_producer"],
        "recipient": case["recipient"]["original_producer"]["original_recipient"],
        "adoption": case["recipient"]["original_producer"]["original_recipient"]["artifact_adoption"],
    }
    with pytest.raises(ValueError, match="root digest"):
        replay_case(broken, source)
