"""Contract tests for the CPU two-stage composition.

The injected scorer is a unit-test seam only.  The composition's default
entrypoint still calls the real sandbox scorer workers and never uses this
fixture as an experiment result.
"""

from __future__ import annotations

import json
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_pipe3_two_stage_composition import _patch_producer, _prepare_case, run  # noqa: E402
from peerrolebench_baseline_policies import NoUpdatePolicy, TerminalOnlyPolicy  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402


def _unit_scorer(kind, sources, info, out, log, seed):
    out.mkdir(parents=True, exist_ok=True)
    return {
        "status": "FAIL" if kind == "producer" else "PASS",
        "label": 0 if kind == "producer" else 1,
        "quality_score": 0.0 if kind == "producer" else 0.8,
        "coverage_complete": True, "decision_complete": True,
        "scorer_version": "unit-injected-scorer", "response_digest": "a" * 64,
    }


def test_producer_source_publication_is_separate_from_later_update(tmp_path: Path):
    result = run(tmp_path / "composition", scorer=_unit_scorer)
    assert result["contract_passed"] is True
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["status"] == "QUALIFIED_OFFLINE"
    assert producer["source_gate"]["evidence_publish_allowed"] is True
    assert producer["source_gate"]["policy_update_allowed"] is False
    assert producer["policy_updates"] == 1
    events = producer["ledger"]
    assignment_i = next(i for i, row in enumerate(events) if row["event_type"] == "later_assignment")
    target_selection_i = next(i for i, row in enumerate(events)
                              if row["event_type"] == "peer_selection" and row["payload"]["task_index"] == 1)
    target_start_i = next(i for i, row in enumerate(events)
                          if row["event_type"] == "task_start" and row["payload"]["task_index"] == 1)
    assert assignment_i < target_selection_i < target_start_i
    assert producer["credit"]["assignment_id"] == producer["assignment_id"]
    delayed_rows = [json.loads(line) for line in (tmp_path / "composition" / "producer_owned" / "raw.jsonl").read_text().splitlines()]
    assert any(row["event"] == "delayed_update" and row["payload"]["feedback_source"] == "terminal_outcome"
               for row in delayed_rows)


def test_recipient_and_mixed_controls_stop_unknown_without_fabricated_target(tmp_path: Path):
    result = run(tmp_path / "composition", scorer=_unit_scorer)
    for control in ("recipient_owned", "mixed"):
        case = next(item for item in result["cases"] if item.get("control") == control)
        assert case["status"] == "UNKNOWN"
        assert case["contract_passed"] is True
        assert case["passed"] is False
        assert case["target"]["status"] == "NOT_RUN_UNKNOWN"
        assert case["policy_updates"] == 0


def test_raw_stage_logs_are_written_incrementally(tmp_path: Path):
    run(tmp_path / "composition", scorer=_unit_scorer)
    raw = tmp_path / "composition" / "producer_owned" / "raw.jsonl"
    rows = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["event"] == "config"
    assert any(row["event"] == "task_start_sealed" for row in rows)
    assert any(row["event"] == "delayed_update" for row in rows)


def test_producer_patch_uses_seed_specific_timestamp_field():
    for seed, field in ((0, "timestamp"), (1, "measured_at")):
        materials = build_materials(load_pipe3(seed))
        patched = _patch_producer(materials["agent_payloads"]["producer"]["source_files"], field)
        assert f'data["{field}"] = event.{field}.isoformat()' in patched["producer.py"]


def test_target_unknown_preserves_incomplete_ledger_and_does_not_update(tmp_path: Path):
    def target_unknown(kind, sources, info, out, log, seed):
        if seed == 1 and kind == "adoption" and "after_action" in out.parts:
            out.mkdir(parents=True, exist_ok=True)
            return {"status": "UNKNOWN", "label": None, "quality_score": None,
                    "coverage_complete": False, "decision_complete": False,
                    "unknown_reason": "unit-target-adoption-unknown"}
        return _unit_scorer(kind, sources, info, out, log, seed)

    result = run(tmp_path / "composition", scorer=target_unknown)
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["status"] == "UNKNOWN"
    assert producer["contract_passed"] is False
    assert producer["target"]["outcome"]["status"] == "UNKNOWN"
    assert producer["replay"]["status"] == "NOT_RUN_INCOMPLETE"
    assert producer["credit"] is None
    assert producer["policy_updates"] == 0
    assert any(row["event_type"] == "later_assignment" for row in producer["ledger"])
    assert not any(row["event_type"] == "terminal_outcome" and row["payload"]["outcome_id"].endswith("-1")
                   for row in producer["ledger"])


def test_policy_factory_is_explicit_and_default_behavior_remains_terminal_only(tmp_path: Path):
    calls = []

    def factory(name):
        calls.append(name)
        return TerminalOnlyPolicy()

    result = run(tmp_path / "composition", scorer=_unit_scorer, policy_factory=factory)
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert calls == ["terminal_only", "terminal_only", "terminal_only"]
    assert all(case["policy"] == "terminal_only" for case in result["cases"])
    assert all(case["version"] == "pipe3-two-stage-composition-v1.3" for case in result["cases"])


def test_no_update_policy_is_explicitly_not_counted_as_terminal_update_success(tmp_path: Path):
    calls = []

    def factory(name):
        calls.append(name)
        return NoUpdatePolicy()

    result = run(
        tmp_path / "composition", scorer=_unit_scorer,
        policy_factory=factory, policy_name="no_update",
    )
    assert calls == ["no_update", "no_update", "no_update"]
    assert result["status"] == "QUALIFIED_OFFLINE"
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["policy"] == "no_update"
    assert producer["policy_updates"] == 0
    assert producer["delayed_credit_count"] == 1
    assert producer["policy_update_expected"] is False
    assert producer["policy_update_applied"] is False
    assert producer["scientific_claim_allowed"] is False
