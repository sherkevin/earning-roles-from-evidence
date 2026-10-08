import json
from pathlib import Path
import re
import subprocess

import pytest

import scripts.peerrolebench_c1_pipe3_bounded_live as c1
from scripts.peerrolebench_build_external_source_manifest import build_source_receipt
from scripts.peerrolebench_shared_source_v2 import freeze_source_receipt
from scripts.peerrolebench_shared_source_preflight import prepare_shared_source


def _fake_actor(_out, _stage_dir, stage, prompt, _card):
    if stage == "judgment":
        digest = re.search(r"The artifact digest is ([0-9a-f]{64})", prompt).group(1)
        return ({
            "decision": "accept", "confidence": 1.0, "rationale": "manifest fixture",
            "repair_plan": "", "observed_artifact_sha256": digest,
            "target_role": "producer", "target_paths": ["producer.py"],
            "defect_type": "producer_contract", "evidence_refs": ["artifact_digest"],
        }, {"elapsed_seconds": 0.001, "http_status": "200", "usage_complete": True, "usage": {"input_tokens": 1, "output_tokens": 1}})
    if stage == "action":
        payload = json.loads(prompt.split("ACTION PAYLOAD:\n", 1)[1])
        return ({"source_files": payload["source_files"]}, {"elapsed_seconds": 0.001, "http_status": "200", "usage_complete": True, "usage": {"input_tokens": 1, "output_tokens": 1}})
    raise AssertionError(stage)


@pytest.fixture
def zero_call_run(tmp_path, monkeypatch):
    monkeypatch.setattr(c1.api, "call_api", _fake_actor)
    card = json.loads(c1.CARD.read_text(encoding="utf-8"))
    card["source_commit"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=c1.ROOT, text=True
    ).strip()
    card_copy = tmp_path / "card.json"
    card_copy.write_text(json.dumps(card), encoding="utf-8")
    run_dir = tmp_path / "c1"
    result = c1.run(run_dir, card_path=card_copy, diagnostic_only=True)
    assert result["passed"] is True
    return run_dir


def test_source_manifest_is_parent_sealed_and_validated(zero_call_run):
    source = build_source_receipt(zero_call_run, "parent_source", 0, "zero-call-c1-source-v1")
    assert source["source_seal"]["source_digest"] == source["source_receipt_digest"]
    assert source["provenance"]["policy_invariant"] is True
    assert source["source_lineage"]["selected_candidate"] == "peer-b@v1"
    assert source["source_selection_binding"]["native_selection_id"] == "selection-parent-0"
    assert source["target_status"] == "NOT_STARTED"
    validated = freeze_source_receipt(source, source["source_receipt_digest"])
    assert validated["projection_version"] == "shared-source-projection-v2"


def test_manifest_rejects_external_digest_mutation(zero_call_run):
    source = build_source_receipt(zero_call_run, "parent_source", 0, "zero-call-c1-source-v1")
    source["judgment"]["decision"] = "reject_redo"
    try:
        freeze_source_receipt(source, source["source_receipt_digest"])
    except ValueError as exc:
        assert "source payload does not match external source seal" in str(exc)
    else:
        raise AssertionError("mutated source was accepted")


def test_parent_preflight_projects_one_source_to_three_arm_namespaces(tmp_path, zero_call_run):
    source = build_source_receipt(zero_call_run, "parent_source", 0, "zero-call-c1-source-v1")
    bundle = {
        "manifest_version": "peerrolebench-external-source-manifest-v1",
        "manifest_id": "historical-c1-source-v1",
        "expected_source_digest": source["source_receipt_digest"],
        "source_receipt": source,
        "scientific_claim_allowed": False,
        "historical_conversion": True,
    }
    path = tmp_path / "source_manifest.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")
    prepared = prepare_shared_source(path, source["source_receipt_digest"])
    assert prepared["arms"] == ["no_update", "contextual_trust_linear", "RARE"]
    assert prepared["cost_ledger"]["source_cost_units_counted_once"] > 0
    assert prepared["cost_ledger"]["target_cost_units_sum"] == 0
    assert len({row["policy_namespace"] for row in prepared["projections"]}) == 3


def test_parent_preflight_rejects_source_binding_mutation(tmp_path, zero_call_run):
    source = build_source_receipt(zero_call_run, "parent_source", 0, "zero-call-c1-source-v3")
    bundle = {
        "manifest_version": "peerrolebench-external-source-manifest-v1",
        "manifest_id": "historical-c1-source-v3",
        "expected_source_digest": source["source_receipt_digest"],
        "source_receipt": source,
        "scientific_claim_allowed": False,
        "historical_conversion": True,
    }
    source["source_selection_binding"]["chosen_candidate"] = "peer-c@v1"
    path = tmp_path / "source_manifest.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")
    try:
        prepare_shared_source(path, source["source_receipt_digest"])
    except ValueError as exc:
        assert "source payload" in str(exc) or "binding" in str(exc)
    else:
        raise AssertionError("mutated source selection binding was accepted")


def test_parent_source_failure_writes_root_unknown_receipt(tmp_path, monkeypatch):
    def fail_actor(*_args, **_kwargs):
        raise RuntimeError("synthetic transport failure")
    monkeypatch.setattr(c1.api, "call_api", fail_actor)
    card = json.loads(c1.CARD.read_text(encoding="utf-8"))
    card["source_commit"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=c1.ROOT, text=True
    ).strip()
    card_copy = tmp_path / "card.json"
    card_copy.write_text(json.dumps(card), encoding="utf-8")
    run_dir = tmp_path / "failed-parent"
    result = c1.run(run_dir, card_path=card_copy, diagnostic_only=True)
    assert result["status"] == "UNKNOWN"
    assert result["arm_loop_started"] is False
    assert result["real_api_calls"] == 0
    assert (run_dir / "summary.json").is_file()
    failure = json.loads((run_dir / "parent_source" / "failure.json").read_text())
    assert failure["error_type"] == "RuntimeError"
    assert not (run_dir / "no_update").exists()
