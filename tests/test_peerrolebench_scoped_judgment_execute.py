"""Offline software fixtures only; no provider calls or empirical judgments."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import peerrolebench_scoped_judgment_execute as subject  # noqa: E402


def _fixture(tmp_path):
    prepared = ROOT / "experiments/logs/n03_scoped_judgment_prepare_20261007_v2"
    gold = ROOT / "experiments/logs/n03_scoped_judgment_gold_20261007_v1/summary.json"
    card = {
        "schema_version": subject.VERSION, "status": "AUTHORIZED_EXECUTION",
        "real_api_runs_allowed": True, "prepared_dir": str(prepared),
        "parent_manifest_sha256": subject.sha(prepared / "parent_manifest.json"),
        "gold_summary_path": str(gold), "gold_summary_sha256": subject.sha(gold),
        "gold_config_path": str(gold.parent / "config.json"),
        "gold_config_sha256": subject.sha(gold.parent / "config.json"),
        "max_judgment_requests": 4, "maximum_task_requests": 4, "max_episodes": 4,
        "retries": 0, "candidate_executions": 0, "actions": 0,
        "training_updates": 0, "gpu_runs": 0,
        "budget": {"prior_documented_attempted_episodes": 31,
                   "maximum_documented_cumulative_attempted_episodes": 35},
        "model": "qwen3.8-max", "temperature": 0, "thinking": {"type": "disabled"},
        "stream": True, "request_timeout_seconds": 300, "max_tokens": {"judgment": 1024},
    }
    path = tmp_path / "card.json"
    path.write_text(json.dumps(card))
    return path, prepared


def _answer(case):
    negative = case["expected_producer_verdict"] == "violates_contract"
    return {
        "producer_contract_assessment": {
            "verdict": case["expected_producer_verdict"],
            "observed_artifact_sha256": case["public_file_digests"]["producer.py"],
            "contract_clause_refs": ["C2_producer_timestamp"] if negative else [],
            "rationale": "Timestamp uses a space instead of T" if negative else "Contract appears met",
        },
        "recipient_integration_plan": {
            "needs_change": case["expected_recipient_needs_change"],
            "target_paths": case["expected_recipient_target_paths"],
            "rationale": "Processor responsibility assessed separately",
        },
    }


def test_prepare_verifies_existing_pins_without_provider(tmp_path, monkeypatch):
    card, _ = _fixture(tmp_path)
    monkeypatch.setattr(subject, "call_api", lambda *args: pytest.fail("provider called"))
    out = tmp_path / "run"
    subject.prepare(card, out)
    assert json.loads((out / "summary.json").read_text())["status"] == "READY"
    assert len(list((out / "source_snapshot").iterdir())) == 12
    with pytest.raises(FileExistsError):
        subject.prepare(card, out)
    changed = json.loads(card.read_text())
    changed["parent_manifest_sha256"] = "0" * 64
    card.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="pin"):
        subject.prepare(card, tmp_path / "not-created")
    assert not (tmp_path / "not-created").exists()


def test_structured_validation_rejects_schema_binding_and_gold(tmp_path):
    card, prepared = _fixture(tmp_path)
    _card, _prepared, _manifest, _gold_path, _gold, cases = subject._inputs(card)
    case = cases[1]
    request = json.loads((prepared / case["request_path"]).read_text())
    good = _answer(case)
    subject._validate_answer(good, case, request)
    for edit in (
        lambda x: x.update({"extra": 1}),
        lambda x: x["producer_contract_assessment"].update(observed_artifact_sha256="0" * 64),
        lambda x: x["producer_contract_assessment"].update(contract_clause_refs=[]),
        lambda x: x["recipient_integration_plan"].update(needs_change=False),
    ):
        answer = json.loads(json.dumps(good))
        edit(answer)
        with pytest.raises((ValueError, TypeError)):
            subject._validate_answer(answer, case, request)


def test_one_call_per_resume_requires_parent_review_and_finishes_without_fifth(tmp_path, monkeypatch):
    card, _ = _fixture(tmp_path)
    out = tmp_path / "run"
    subject.prepare(card, out)
    cases = subject._inputs(card)[-1]
    calls = []

    def fake_call(run_dir, stage_dir, stage, prompt, execution_card):
        index = len(calls)
        calls.append(index)
        subject.log(run_dir, "request_start", {"attempt": index + 1, "software_fixture": True})
        (stage_dir / "judgment_response.sse").write_text("software fixture, not a provider response")
        return _answer(cases[index]), {"usage_complete": True,
                                       "returned_model": execution_card["model"], "stop_reason": "end_turn"}

    monkeypatch.setattr(subject, "call_api", fake_call)
    for index, case in enumerate(cases):
        result = subject.run_next(card, out)
        assert result["status"] == "AWAITING_RATIONALE_REVIEW"
        with pytest.raises(ValueError, match="review"):
            subject.run_next(card, out)
        answer = out / f"case_{index}" / "judgment_response.sse"
        subject.save(out / f"case_{index}" / "rationale_review.json", {
            "case_id": case["case_id"], "response_sha256": subject.sha(answer),
            "status": "PASS", "evidence": "Parent checked response rationale against public files",
        })
    assert subject.run_next(card, out)["status"] == "COMPLETE"
    assert calls == [0, 1, 2, 3]
    with pytest.raises(ValueError, match="terminal"):
        subject.run_next(card, out)


def test_wrong_answer_stops_permanently_after_one_consumed_call(tmp_path, monkeypatch):
    card, _ = _fixture(tmp_path)
    out = tmp_path / "run"
    subject.prepare(card, out)

    def bad_call(run_dir, stage_dir, stage, prompt, execution_card):
        subject.log(run_dir, "request_start", {"attempt": 1, "software_fixture": True})
        return {}, {"usage_complete": True, "returned_model": execution_card["model"],
                    "stop_reason": "end_turn"}

    monkeypatch.setattr(subject, "call_api", bad_call)
    assert subject.run_next(card, out)["status"] == "STOPPED"
    with pytest.raises(ValueError, match="terminal"):
        subject.run_next(card, out)


def test_second_cell_failure_preserves_reviewed_first_cell_and_partial_cost(tmp_path, monkeypatch):
    card, _ = _fixture(tmp_path)
    out = tmp_path / "run"
    subject.prepare(card, out)
    cases = subject._inputs(card)[-1]
    attempts = []

    def fixture_call(run_dir, stage_dir, stage, prompt, execution_card):
        index = len(attempts)
        attempts.append(index)
        subject.log(run_dir, "request_start", {"attempt": index + 1, "software_fixture": True})
        (stage_dir / "judgment_response.sse").write_text("software fixture, not an API response")
        if index == 1:
            return {}, {"usage_complete": True, "returned_model": execution_card["model"],
                        "stop_reason": "end_turn"}
        subject.save(stage_dir / "judgment_cost.json", {
            "usage_complete": True, "usage": {"input_tokens": 5, "output_tokens": 7},
            "elapsed_seconds": 2.5,
        })
        return _answer(cases[index]), {"usage_complete": True,
                                        "returned_model": execution_card["model"], "stop_reason": "end_turn"}

    monkeypatch.setattr(subject, "call_api", fixture_call)
    first = subject.run_next(card, out)
    assert first["status"] == "AWAITING_RATIONALE_REVIEW"
    subject.save(out / "case_0/rationale_review.json", {
        "case_id": cases[0]["case_id"], "response_sha256": subject.sha(out / "case_0/judgment_response.sse"),
        "status": "PASS", "evidence": "Parent checked rationale against public source",
    })
    stopped = subject.run_next(card, out)
    assert stopped["status"] == "STOPPED"
    assert [row["status"] for row in stopped["cells"]] == ["PASS", "FAILED", "UNSTARTED", "UNSTARTED"]
    assert stopped["request_starts"] == stopped["api_calls"] == 2
    assert stopped["cumulative_attempted_episodes"] == 33
    assert stopped["known_input_tokens"] == 5 and stopped["known_output_tokens"] == 7
    assert stopped["input_tokens"] is None and stopped["usage_complete"] is False
    assert stopped["known_elapsed_seconds"] == 2.5
    assert stopped["failure_stage"] == "structured_judgment"
    assert "two-field" in stopped["reason"]
    assert json.loads((out / "case_1/answer.json").read_text()) == {}
    assert attempts == [0, 1]
