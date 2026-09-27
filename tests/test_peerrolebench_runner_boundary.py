from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_runner_boundary_qualification import (  # noqa: E402
    classify_scorer_response,
    ledger_cases,
    replay_case,
)

FIXTURE = ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json"


@pytest.fixture()
def records():
    return json.loads(FIXTURE.read_text())


def test_complete_fixture_is_update_eligible(records):
    result = replay_case(records, strict=True)
    assert result["status"] == "PASS"
    assert result["complete"] is True


@pytest.mark.parametrize("event_type", ["peer_selection", "producer_delivery", "recipient_judgment"])
def test_stage_exception_prefix_is_unknown_and_never_an_update(records, event_type):
    result = replay_case(ledger_cases(records)[{
        "peer_selection": "exception_after_selection",
        "producer_delivery": "exception_after_delivery",
        "recipient_judgment": "exception_after_judgment",
    }[event_type]], strict=False)
    assert result["status"] == "UNKNOWN"
    assert result["complete"] is False


def test_retry_record_is_invalid_not_a_second_sample(records):
    result = replay_case(ledger_cases(records)["transport_retry_record"], strict=True)
    assert result["status"] == "INVALID"
    assert result["code"] == "unsupported_retry"


@pytest.mark.parametrize("kind", ["timeout", "permission", "invalid_json", "missing", "exception"])
def test_scorer_transport_failures_are_unknown_without_evidence(kind):
    kwargs = {"timed_out": kind == "timeout", "permission_denied": kind == "permission",
              "transport_error": "connection_reset" if kind == "exception" else None}
    response = "not-json" if kind == "invalid_json" else None
    result = classify_scorer_response(response, **kwargs)
    assert result["status"] == "UNKNOWN"
    assert result["label"] is None


def test_complete_scorer_response_is_the_only_update_eligible_case():
    assert classify_scorer_response({"status": "PASS", "scorer_version": "v1",
                                     "coverage_complete": True})["label"] == 1


def test_unknown_scorer_case_is_rejected():
    result = classify_scorer_response({"status": "MAYBE", "scorer_version": "v1",
                                       "coverage_complete": True})
    assert result["status"] == "UNKNOWN"
