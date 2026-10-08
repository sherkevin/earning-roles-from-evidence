"""Offline binding tests; these handwritten files are not model evidence."""
from pathlib import Path
import hashlib
import json
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_actor_experience import digest, canonical_bytes
from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_live_producer_stage import model_config_digest, policy_digest
from peerrolebench_pipe3_material_adapter import digest_files
from peerrolebench_pipe3_public_contract_v2 import build_materials
from peerrolebench_pipe3_task_qualification import load_pipe3
import peerrolebench_c1_pipe3_bounded_live as c1
import peerrolebench_actor_route_screen as route


def test_materials_keep_unmodified_public_recipient_source():
    actual = route._materials(0)
    expected = build_materials(load_pipe3(0))
    assert actual["agent_payloads"]["recipient"]["source_files"] == expected["agent_payloads"]["recipient"]["source_files"]


def test_cost_keeps_failed_attempt_and_unknown_usage(tmp_path):
    producer = tmp_path / "producer_0"
    (producer / "episode").mkdir(parents=True)
    (producer / "raw.jsonl").write_text(json.dumps({"event_type": "request_start"}) + "\n")
    (producer / "episode" / "producer_cost.json").write_text(json.dumps({
        "elapsed_seconds": 2.5, "usage": None, "usage_complete": False,
        "http_status": "500", "exit_code": 22}))
    cost = route._cost_receipts(tmp_path)
    assert cost["attempted_api_requests"] == 1
    assert cost["observed_wall_seconds"] == 2.5
    assert cost["status"] == "UNKNOWN"
    assert any("input_tokens" in field for field in cost["unknown_fields"])


def _producer_card():
    return {"real_api_runs_allowed": True, "stream_id": "screen", "arm_id": "route",
            "model": "fixture-model", "temperature": 0, "max_tokens": {"producer": 100},
            "stream": False, "thinking": {"type": "disabled"},
            "request_timeout_seconds": 30, "maximum_task_requests": 1,
            "budget": {"prior_attempted_episodes": 31, "additional_cap": 2,
                       "attempted_ledger": []}}


def test_card_requires_bound_calls_and_recipient_request_budget():
    card = _producer_card()
    route_card = {"runner_version": route.VERSION, "diagnostic_only": True,
                  "selected_key": route.SELECTED_KEY, "source_seed": 0, "target_seed": 1,
                  "episode_limit": 2,
                  "stream_id": "screen", "recipient_card": {
                      "model": "fixture-model", "maximum_task_requests": 4,
                      "max_tokens": {"judgment": 10, "action": 10}},
                  "producer_calls": [{"card": card, "expected_card_digest": digest(card),
                                      "reservation_path": "/tmp/reservation.json",
                                      "expected_reservation_digest": "a" * 64}] * 2}
    candidate = route._validate_card(route_card)
    assert candidate.source_digest == policy_digest()
    assert candidate.model_config_digest == model_config_digest(card)
    route_card["recipient_card"]["maximum_task_requests"] = 3
    with pytest.raises(ValueError, match="two judgment/action calls per episode"):
        route._validate_card(route_card)


def _sealed_fixture(tmp_path: Path):
    output = tmp_path / "producer_0"
    output.mkdir()
    (output / "episode").mkdir()
    candidate = CandidateRegistryEntry("peer-b", "live-v1", policy_digest(),
                                       "fixture-model", "a" * 64)
    prepared = {"decision_digest": "b" * 64, "candidate": candidate.payload(),
                "task_index": 0, "before": {"state_digest": "c" * 64}}
    source = {"producer.py": "def produce():\n    return 1\n"}
    artifact = digest_files(source)
    completed = {"status": "COMPLETED", "candidate": candidate.payload(),
                 "source_files": source, "before": prepared["before"],
                 "delivery": {"delivery_id": "route-delivery-0", "task_id": c1.TASK_ID,
                              "producer_id": "peer-b", "recipient_id": "peer-a",
                              "artifact_sha256": artifact, "source_event_id": "request-0",
                              "task_index": 0, "selection_id": "selection-route-0",
                              "candidate_source_digest": candidate.source_digest}}
    files = {"config.json": {"prepared": prepared, "card_digest": "d" * 64},
             "parsed_result.json": {"status": "PARSED", "parsed": {"source_files": source}},
             "episode/producer_request.json": {}, "episode/producer_cost.json": {}}
    hashes = {}
    for name, content in files.items():
        target = output / name
        target.write_bytes(canonical_bytes(content))
        hashes[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    receipt = {"schema": "peerrolebench-live-producer-stage-v1", "status": "PARSED",
               "decision_digest": prepared["decision_digest"], "card_digest": "d" * 64,
               "files": hashes}
    receipt_path = output / "completion_receipt.json"
    receipt_path.write_bytes(canonical_bytes(receipt))
    receipt_digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    completed["completion_receipt_sha256"] = receipt_digest
    (output / "completion.json").write_bytes(canonical_bytes(completed))
    return candidate, prepared, output, receipt_digest, completed


def test_fresh_route_preserves_policy_hash_and_generated_artifact_hash(tmp_path, monkeypatch):
    candidate, prepared, output, receipt_digest, completed = _sealed_fixture(tmp_path)
    assert completed["delivery"]["artifact_sha256"] != candidate.source_digest
    calls = []
    ledger = SimpleNamespace(record_task_start=lambda *args: calls.append(("start", args)),
                             record_delivery=lambda delivery: calls.append(("delivery", delivery)))
    boundary = SimpleNamespace(registry=(candidate,), ledger=ledger)

    def stop_after_delivery(*args, **kwargs):
        raise RuntimeError("binding reached scorer")

    monkeypatch.setattr(c1, "_score_producer", stop_after_delivery)
    monkeypatch.setattr(c1, "interfaces", lambda materials: {})
    context = {"prepared": prepared, "output_dir": str(output),
               "expected_receipt_digest": receipt_digest, "completion": completed}
    with pytest.raises(RuntimeError, match="binding reached scorer"):
        c1._run_episode(arm="route", decision_index=0, arm_dir=tmp_path,
                        decision_dir=tmp_path / "decision_0", boundary=boundary,
                        materials={}, candidates={}, selected_key=candidate.key,
                        card={}, raw=tmp_path / "raw.jsonl", task_seed=0,
                        fresh_producer=context)
    delivery = calls[-1][1]
    assert delivery.candidate_source_digest == candidate.source_digest
    assert delivery.artifact_sha256 == completed["delivery"]["artifact_sha256"]

    (output / "parsed_result.json").write_text(json.dumps({"status": "PARSED", "parsed": {"source_files": {}}}))
    with pytest.raises(ValueError, match="sealed file changed"):
        c1._run_episode(arm="route", decision_index=0, arm_dir=tmp_path,
                        decision_dir=tmp_path / "decision_0", boundary=boundary,
                        materials={}, candidates={}, selected_key=candidate.key,
                        card={}, raw=tmp_path / "raw.jsonl", task_seed=0,
                        fresh_producer=context)
