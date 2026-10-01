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

from peerrolebench_pipe3_two_stage_composition import run  # noqa: E402


def _unit_scorer(kind, sources, info, out, log, seed):
    out.mkdir(parents=True, exist_ok=True)
    return {
        "status": "PASS", "label": 1, "quality_score": 0.8,
        "coverage_complete": True, "decision_complete": True,
        "scorer_version": "unit-injected-scorer", "response_digest": "a" * 64,
    }


def test_producer_source_publication_is_separate_from_later_update(tmp_path: Path):
    result = run(tmp_path / "composition", scorer=_unit_scorer)
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


def test_recipient_and_mixed_controls_stop_unknown_without_fabricated_target(tmp_path: Path):
    result = run(tmp_path / "composition", scorer=_unit_scorer)
    for control in ("recipient_owned", "mixed"):
        case = next(item for item in result["cases"] if item.get("control") == control)
        assert case["status"] == "UNKNOWN"
        assert case["target"]["status"] == "NOT_RUN_UNKNOWN"
        assert case["policy_updates"] == 0


def test_raw_stage_logs_are_written_incrementally(tmp_path: Path):
    run(tmp_path / "composition", scorer=_unit_scorer)
    raw = tmp_path / "composition" / "producer_owned" / "raw.jsonl"
    rows = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["event"] == "config"
    assert any(row["event"] == "task_start_sealed" for row in rows)
    assert any(row["event"] == "delayed_update" for row in rows)
