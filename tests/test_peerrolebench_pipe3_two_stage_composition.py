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
from peerrolebench_baseline_policies import (  # noqa: E402
    FeatureContextualTrustPolicy, NoUpdatePolicy, TerminalOnlyPolicy, policy_from_name,
)
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


def _feature_policy_factory(name):
    assert name == "contextual_trust_linear"
    return FeatureContextualTrustPolicy(
        dimension=64, ridge=1.0, trust_scale=2.0, temperature=1.0, exploration=0.0,
        encoder_version="hash64-v1", feature_schema="matrix-features-v1",
    )


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
    assert all(case["version"] == "pipe3-two-stage-composition-v1.8" for case in result["cases"])


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


def test_recipient_judgment_arm_uses_its_declared_feedback_channel(tmp_path: Path):
    """Contextual trust consumes target recipient judgment, not terminal quality."""
    result = run(
        tmp_path / "composition", scorer=_unit_scorer,
        policy_factory=lambda name: policy_from_name(name),
        policy_name="contextual_trust",
    )
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["contract_passed"] is True
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["policy_update_expected"] is True
    assert producer["policy_update_applied"] is True
    assert producer["feedback_contract_ok"] is True
    assert producer["status"] == "QUALIFIED_OFFLINE"
    rows = [json.loads(line) for line in (tmp_path / "composition" / "producer_owned" / "raw.jsonl").read_text().splitlines()]
    delayed = next(row["payload"] for row in rows if row["event"] == "delayed_update")
    assert delayed["feedback_source"] == "recipient_judgment"


def test_feature_contextual_trust_uses_canonical_feature_contract(tmp_path: Path):
    result = run(
        tmp_path / "composition", scorer=_unit_scorer,
        policy_factory=_feature_policy_factory,
        policy_name="contextual_trust_linear",
    )
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["contract_passed"] is True
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["policy"] == "contextual_trust_linear"
    assert producer["policy_update_applied"] is True
    assert producer["feedback_contract_ok"] is True
    # The source and target policy selections consume the same canonical
    # versioned feature map.  The native ledger intentionally stores only the
    # protocol selection, so the richer policy input is preserved in raw.jsonl
    # as the sidecar contract receipt.
    rows = [json.loads(line) for line in (tmp_path / "composition" / "producer_owned" / "raw.jsonl").read_text().splitlines()]
    feature_rows = [row["payload"] for row in rows if row["event"] == "selection_feature_contract"]
    sidecar_rows = [row["payload"] for row in rows
                    if row["event"] in {"source_selection_sidecar", "target_selection_sidecar"}]
    assert len(feature_rows) == 1
    assert len(sidecar_rows) == 2
    feature = feature_rows[0]
    assert feature["encoder_version"] == "hash64-v1"
    assert feature["feature_schema"] == "matrix-features-v1"
    assert set(feature["captured_features"]) == {"peer-b@v1", "peer-c@v1"}
    assert all(len(values) == 64 for values in feature["captured_features"].values())
    for sidecar in sidecar_rows:
        payload = sidecar["payload"]
        assert sidecar["sidecar_digest"]
        assert sidecar["feature_digest"] == feature["feature_digest"]
        assert payload["policy_name"] == "contextual_trust_linear"
        assert payload["policy_version"] == "linear-ridge-v1"
        assert payload["captured_features"] == feature["captured_features"]
    assignments = [row["payload"] for row in producer["ledger"] if row["event_type"] == "later_assignment"]
    target_selection = next(row["payload"] for row in producer["ledger"]
                            if row["event_type"] == "peer_selection" and row["payload"]["task_index"] == 1)
    assert assignments[0]["agent_id"] == target_selection["chosen_peer_id"]
    assert producer["scientific_claim_allowed"] is False


def test_raw_acceptance_arm_stays_unknown_without_raw_projection(tmp_path: Path):
    result = run(
        tmp_path / "composition", scorer=_unit_scorer,
        policy_factory=lambda name: policy_from_name(name),
        policy_name="raw_acceptance",
    )
    assert result["status"] == "UNKNOWN"
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["policy_update_expected"] is True
    assert producer["policy_update_applied"] is False
    assert producer["feedback_contract_ok"] is False


def test_public_judgment_assignment_mode_reaches_canonical_composition(tmp_path: Path):
    result = run(
        tmp_path / "composition", scorer=_unit_scorer,
        assignment_mode="public_judgment", public_judgment_fixture="accept",
    )
    assert result["status"] == "QUALIFIED_OFFLINE"
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["assignment_mode"] == "public_judgment"
    preview_rows = [json.loads(line) for line in (tmp_path / "composition" / "producer_owned" / "raw.jsonl").read_text().splitlines()
                    if json.loads(line)["event"] == "target_selection_preview"]
    assert len(preview_rows) == 1
    payload = preview_rows[0]["payload"]
    assert payload["assignment_mode"] == "public_judgment"
    assert payload["assignment_score"]["version"] == "role-evidence-judgment-beta-v1"
    assert payload["assignment_score"]["input_digest"]
    assert payload["base_scores"] == [0.0, 0.0]
    assert payload["assignment_effect_observed"] is True
    assert producer["assignment_effect_observed"] is True
    assert abs(payload["assignment_score"]["scores"][0] - 1.0 / 3.0) < 1e-12
    assert payload["assignment_score"]["scores"][1] == 0.0


def test_history_mode_appends_after_committed_target_credit(tmp_path: Path):
    result = run(tmp_path / "composition", scorer=_unit_scorer, history_mode="append")
    assert result["status"] == "QUALIFIED_OFFLINE"
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    assert producer["history"]["adapter_version"] == "peer-history-canonical-adapter-v1"
    assert producer["history"]["entry"]["status"] == "PASS"
    assert producer["history"]["receipt"]["later_credit_digest"] == producer["credit"]["credit_digest"]
    assert producer["history"]["history_projection"]["entry_count"] == 1
    for control in ("recipient_owned", "mixed"):
        case = next(item for item in result["cases"] if item.get("control") == control)
        assert case["history"]["status"] == "NOT_RUN_UNKNOWN"
