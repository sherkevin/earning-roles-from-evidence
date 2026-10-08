"""Software-only negative/contract tests for the v4 closure receipt checker.

These fixtures are not benchmark observations and are never scientific results.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.validate_benchmark_baseline_closure import validate_receipt


def _ref(tmp_path: Path, name: str) -> dict[str, str]:
    path = tmp_path / name
    path.write_text(f"synthetic software fixture: {name}\n")
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _denom() -> dict[str, int]:
    return {"attempted": 1, "started": 1, "completed": 1, "known": 1, "unknown": 0, "failed": 0, "unstarted": 0}


def _receipt(tmp_path: Path, *, status: str = "CLOSED_FULL", future_y: bool = True) -> dict:
    root_ref = _ref(tmp_path, "root_manifest.json")
    track_ref = _ref(tmp_path, "track_manifest.json")
    raw_ref = _ref(tmp_path, "raw.jsonl")
    review_ref = _ref(tmp_path, "review.json")
    top_refs = {key: _ref(tmp_path, f"{key}.md") for key in ("goal", "evaluation", "pre_run_manifest")}
    gates = []
    for gid in ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]:
        gates.append({
            "gate_id": gid, "claim_scope": "synthetic contract only",
            "required_evidence": "synthetic fixture bytes", "pre_run_hash": "a" * 64,
            "artifact_path": _ref(tmp_path, f"{gid}.json"), "replay_command": "true",
            "denominator": _denom(), "verifier": {"identity": f"gate-verifier-{gid}", "independent": True, "report": review_ref},
            "status": "PASS", "decision_reason": "software contract test",
        })
    arms = [{"arm_id": aid, "version": "test-v1", "qualified": True, "same_information": True, "history_namespace": f"ns-{aid}"}
            for aid in ["uniform", "no_update", "raw_acceptance", "terminal_only", "contextual_trust_linear", "pooled_controller", "RARE", "closest_published"]]
    roots = [{"root_id": f"r{i}", "structural_signature": f"sig-{i}", "split": "confirmation", "manifest": root_ref} for i in range(3)]
    streams = [{"root_id": r["root_id"], "stream_id": f"s-{r['root_id']}-{a['arm_id']}", "arm_id": a["arm_id"], "history_namespace": f"{r['root_id']}/{a['arm_id']}", "independent": True, "status": "COMPLETE"} for r in roots for a in arms]
    sentinel_evidence = _ref(tmp_path, "sentinel.json")
    y_evidence = _ref(tmp_path, "future_y.json")
    holdout_evidence = _ref(tmp_path, "holdout.json")
    ledger_evidence = _ref(tmp_path, "ledger.json")
    cells = []
    for r in roots:
        for a in arms:
            stream_id = f"s-{r['root_id']}-{a['arm_id']}"
            for hyp in ["H1", "H2", "H3", "safety"]:
                cells.append({
                    "cell_id": f"{r['root_id']}-{a['arm_id']}-{hyp}", "root_id": r["root_id"],
                    "stream_id": stream_id, "arm_id": a["arm_id"], "future_assignment_id": f"fa-{r['root_id']}-{a['arm_id']}",
                    "y_status": "KNOWN" if hyp == "H2" else "NOT_APPLICABLE", "y_artifact": y_evidence if hyp == "H2" else None,
                    "hypothesis": hyp, "pre_run_sealed": True, "execution_status": "COMPLETE",
                    "observed_regime": "neutral", "falsifier_status": "PASS", "estimate": 0.0,
                    "interval": [-0.1, 0.1], "independent_verdict": "PASS"
                })
    return {
        "closure_scope": "benchmark_baseline_acceptance", "guide_version": "v4_20261008",
        "goal_sha256": top_refs["goal"]["sha256"], "goal_ref": top_refs["goal"],
        "evaluation_sha256": top_refs["evaluation"]["sha256"], "evaluation_ref": top_refs["evaluation"],
        "pre_run_manifest_sha256": top_refs["pre_run_manifest"]["sha256"], "pre_run_manifest_ref": top_refs["pre_run_manifest"],
        "gates": gates, "track_manifest": {"primary_track": "ArtifactRole", "secondary_track": "PeerSelect", "manifest": track_ref},
        "roots": roots, "streams": streams, "arms": arms, "minimum_streams_per_arm": 2,
        "holdout": {"kind": "structural_root", "sealed": True, "artifact": holdout_evidence},
        "target_cells": cells,
        "artifactrole": {"future_assignment_y_complete": future_y, "evidence": y_evidence, "cell_count": len(cells)},
        "hard_fail_sentinels": {k: {"status": "PASS", "executed": True, "reason": "synthetic contract fixture", "evidence": sentinel_evidence} for k in ["judgment_permutation", "trace_only", "candidate_id_menu_order_permutation", "version_swap_stale_evidence", "recipient_only_mixed_unknown", "unselected_label_censoring", "replay_idempotence_correction_lineage", "gold_future_label_injection"]},
        "real_api_calls": {"attempted": 1, "charged": 1, "successful": 1, "raw_receipt": raw_ref, "post_stop_calls": 0},
        "stop_receipt": {"stop_rule": "synthetic test stop", "pre_run_sealed": True, "triggered": True, "stop_time": "2026-01-01T00:00:00Z", "attempted_calls": 1, "charged_calls": 1, "post_stop_calls": 0, "rerun_policy": "new card"},
        "denominator_reconciliation": {"verified": True, "ledger": ledger_evidence}, "cost_reconciliation": {"verified": True, "ledger": ledger_evidence},
        "independent_review": {"identity": "independent-software-reviewer", "independent": True, "scientific_review_passed": True, "report": review_ref},
        "clean_replay": True, "same_information_parity": True, "blind_scorer": True, "independent_environment": True, "policy_state_masked": True,
        "method_outcome": "neutral", "readiness_level": "proceedings_ready", "status": status,
    }


def test_duplicate_gate_ids_and_forbidden_bounded_status_fail_closed(tmp_path: Path):
    receipt = _receipt(tmp_path, status="CLOSED_FULL")
    receipt["gates"] = [dict(receipt["gates"][0]) for _ in range(7)]
    receipt["status"] = "CLOSED_BOUNDED"
    errors = validate_receipt(receipt, tmp_path)
    assert any("each of B1..B7 exactly once" in e for e in errors)
    assert any("CLOSED_BOUNDED" in e or "status" in e for e in errors)


def test_complete_neutral_evidence_can_close_acceptance_without_positive_method_result(tmp_path: Path):
    receipt = _receipt(tmp_path, status="CLOSED_FULL")
    assert validate_receipt(receipt, tmp_path) == []


def test_missing_future_y_cannot_be_called_closed(tmp_path: Path):
    receipt = _receipt(tmp_path, status="CLOSED_FULL", future_y=False)
    errors = validate_receipt(receipt, tmp_path)
    assert any("future_assignment_y_complete" in e for e in errors)


def test_denominator_and_required_cell_failures_are_not_silent(tmp_path: Path):
    receipt = _receipt(tmp_path, status="OPEN")
    receipt["open_reason"] = "synthetic unresolved condition"
    receipt["gates"][0]["denominator"]["completed"] = 2
    receipt["target_cells"][0]["execution_status"] = "UNSTUDIED"
    errors = validate_receipt(receipt, tmp_path)
    assert any("completed != known + unknown" in e for e in errors)
    assert any("required cell is not complete" in e for e in errors)


def test_malformed_array_ids_are_rejected_without_validator_crash(tmp_path: Path):
    receipt = _receipt(tmp_path, status="OPEN")
    receipt["open_reason"] = "synthetic malformed input"
    receipt["roots"][0]["root_id"] = []
    receipt["arms"][0]["arm_id"] = []
    receipt["target_cells"][0]["cell_id"] = []
    errors = validate_receipt(receipt, tmp_path)
    assert errors
    assert all("Traceback" not in e for e in errors)


def test_zero_api_success_and_inconsistent_stop_cannot_close(tmp_path: Path):
    receipt = _receipt(tmp_path, status="CLOSED_FULL")
    receipt["real_api_calls"]["successful"] = 0
    receipt["stop_receipt"]["attempted_calls"] = 0
    receipt["gates"][0]["denominator"] = {"attempted": 0, "started": 0, "completed": 0, "known": 0, "unknown": 0, "failed": 0, "unstarted": 0}
    errors = validate_receipt(receipt, tmp_path)
    assert any("stop_receipt" in e for e in errors)
    assert any("denominator" in e for e in errors)


def test_h2_without_y_artifact_is_unstudied_and_rejected(tmp_path: Path):
    receipt = _receipt(tmp_path, status="CLOSED_FULL")
    h2 = next(cell for cell in receipt["target_cells"] if cell["hypothesis"] == "H2")
    h2["y_status"] = "UNKNOWN"
    h2["y_artifact"] = None
    errors = validate_receipt(receipt, tmp_path)
    assert any("future Y" in e or "y_status" in e for e in errors)


def test_unhashable_status_and_hypothesis_are_rejected_without_crash(tmp_path: Path):
    receipt = _receipt(tmp_path, status="OPEN")
    receipt["open_reason"] = "synthetic malformed enum"
    receipt["status"] = []
    receipt["target_cells"][0]["hypothesis"] = []
    errors = validate_receipt(receipt, tmp_path)
    assert errors
