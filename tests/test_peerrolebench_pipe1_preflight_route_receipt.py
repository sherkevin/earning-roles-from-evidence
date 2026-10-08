from datetime import datetime, timezone
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe1_preflight import (  # noqa: E402
    ADAPTER_BUNDLE_SCHEMA,
    MATERIAL,
    _adapter_rebind_check,
    build_material_binding,
    run,
)
from peerrolebench_pipe1_route_receipt import (  # noqa: E402
    EXPECTED_EVENTS,
    SCHEMA_VERSION,
    canonical_digest,
)


def _valid_receipt():
    digest = lambda digit: digit * 64
    d2, d4, d6, d9 = (digest(d) for d in "2469")
    binding = build_material_binding(MATERIAL)
    d0 = binding["materials"]["0"]["material_digest"]
    d1 = binding["materials"]["3"]["material_digest"]
    artifact = canonical_digest({"message_digest": d2})
    post_workspace = canonical_digest({"pre_workspace_digest": d4, "artifact_digest": artifact})
    post_attestation = canonical_digest({"pre_attestation_digest": d6, "post_workspace_digest": post_workspace})
    candidates = [{"candidate_id": "peer-a", "version": "v1"}, {"candidate_id": "peer-b", "version": "v1"}]
    keys = ["peer-a@v1", "peer-b@v1"]
    base = datetime(2026, 10, 7, 0, 0, tzinfo=timezone.utc)
    times = [(base.replace(second=i)).isoformat().replace("+00:00", "Z") for i in range(len(EXPECTED_EVENTS))]
    chain = lambda prefix: {
        "material_event_id": prefix + "-material",
        "message_event_id": prefix + "-message",
        "message_digest": d2,
        "artifact_event_id": prefix + "-artifact",
        "artifact_digest": artifact,
        "executor_event_id": prefix + "-executor",
        "executor_pre_workspace_digest": d4,
        "executor_post_workspace_digest": post_workspace,
        "verifier_event_id": prefix + "-verifier",
        "verifier_pre_attestation_digest": d6,
        "verifier_post_attestation_digest": post_attestation,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "route_id": "pipe1-source0-target3-test",
        "route_status": "COMPLETE",
        "source": {"seed": 0, "task_id": "PIPE1_etl_fix", "root_id": "pipe1-root-v1", "material_digest": d0, "task_timezone": "Asia/Shanghai"},
        "target": {"seed": 3, "task_id": "PIPE1_etl_fix", "root_id": "pipe1-root-v1", "material_digest": d1, "task_timezone": "Asia/Shanghai"},
        "lineage": {"source": chain("source"), "target": chain("target")},
        "candidate_registry": {
            "registry_id": "peer-registry", "registry_version": "v1",
            "registry_digest": canonical_digest({"registry_id": "peer-registry", "registry_version": "v1", "candidates": candidates}),
            "candidates": candidates,
        },
        "allocation": {"algorithm": "pcg64", "seed": 42, "permutation": keys,
                        "probabilities": {key: 0.5 for key in keys},
                        "propensities": {key: 0.5 for key in keys}, "draw": 0.25, "chosen": keys[0]},
        "provider": {"provider": "idealab", "endpoint_id": "internal", "model": "qwen-mini", "model_revision": "2026-10", "request_config_digest": d9, "secret_free": True},
        "clock": {"started_utc": times[0], "finished_utc": times[-1], "task_timezone": "Asia/Shanghai", "started_local": "2026-10-07T08:00:00+08:00", "finished_local": "2026-10-07T08:00:14+08:00"},
        "costs": {phase: {"wall_seconds": 1.0, "input_tokens": 1, "output_tokens": 1, "api_calls": 1, "gpu_seconds": 0.0} for phase in ("source_message", "source_executor", "source_verifier", "target_message", "target_executor", "target_verifier", "selection")},
        "visibility": {"selected_only": True, "selection_read_cut": 4, "eligible_candidate_ids": keys, "chosen_candidate_id": keys[0], "observed_candidate_ids": [keys[0]], "visible_fields": ["task_spec", "history_digest"], "forbidden_fields": ["expected_hash", "scorer_hash"]},
        "operator_only": {"expected_hash": "a" * 64, "scorer_hash": "b" * 64},
        "order": [{"event": event, "seq": i, "at_utc": times[i], "status": "COMPLETE"} for i, event in enumerate(EXPECTED_EVENTS)],
    }


def _load_receipt(out: Path):
    return json.loads((out / "receipt.json").read_text())


def _check(receipt):
    return next(item for item in receipt["checks"] if item["check"] == "route_receipt")


def test_missing_route_receipt_is_blocked(tmp_path):
    out = tmp_path / "missing"
    run(out)
    receipt = _load_receipt(out)
    assert _check(receipt)["status"] == "BLOCKED"
    assert receipt["scientific_claim_allowed"] is False


def test_valid_route_receipt_adds_pass_but_keeps_scientific_gate_closed(tmp_path):
    route = tmp_path / "route.json"
    route.write_text(json.dumps(_valid_receipt(), sort_keys=True))
    out = tmp_path / "valid"
    run(out, route, MATERIAL)
    receipt = _load_receipt(out)
    assert _check(receipt)["status"] == "PASS"
    assert receipt["status"] == "BLOCKED_PRE_EXECUTION"
    assert receipt["scientific_claim_allowed"] is False
    config = json.loads((out / "config.json").read_text())
    assert config["route_receipt"]["exists"] is True
    assert config["route_receipt"]["material_binding"]["material_digests"]["0"] == _valid_receipt()["source"]["material_digest"]


def test_valid_route_without_material_binding_remains_blocked(tmp_path):
    route = tmp_path / "route.json"
    route.write_text(json.dumps(_valid_receipt(), sort_keys=True))
    out = tmp_path / "missing-binding"
    run(out, route)
    receipt = _load_receipt(out)
    assert _check(receipt)["status"] == "BLOCKED"
    assert "material binding" in _check(receipt)["reason"]
    assert receipt["status"] == "BLOCKED_PRE_EXECUTION"


def test_material_digest_mismatch_fails_closed(tmp_path):
    value = _valid_receipt()
    value["source"]["material_digest"] = "f" * 64
    route = tmp_path / "mismatch.json"
    route.write_text(json.dumps(value, sort_keys=True))
    out = tmp_path / "mismatch"
    run(out, route, MATERIAL)
    receipt = _load_receipt(out)
    assert _check(receipt)["status"] == "FAIL"
    assert "material_digest" in _check(receipt)["reason"]
    assert receipt["status"] == "BLOCKED_PRE_EXECUTION"


def test_invalid_route_receipt_fails_closed(tmp_path):
    route = tmp_path / "invalid.json"
    route.write_text(json.dumps({"schema_version": "wrong"}))
    out = tmp_path / "invalid"
    run(out, route)
    receipt = _load_receipt(out)
    assert _check(receipt)["status"] == "FAIL"
    assert receipt["status"] == "BLOCKED_PRE_EXECUTION"
    assert receipt["scientific_claim_allowed"] is False


def test_required_native_rebind_is_blocked_without_bundle(tmp_path):
    route = tmp_path / "route.json"
    route.write_text(json.dumps(_valid_receipt(), sort_keys=True))
    result, metadata = _adapter_rebind_check(None, route, required=True)
    assert result["status"] == "BLOCKED"
    assert metadata["required"] is True


def test_native_rebind_bundle_matches_adapter_and_route(tmp_path):
    # Reuse the independent adapter qualification fixture as a serialized
    # bundle; the preflight only consumes the public bundle contract.
    from test_peerrolebench_pipe1_adapter_route_join import _adapter, _events, _request, _route
    from peerrolebench_pipe3_live_contract_qualification import _registry

    request = _request()
    request["registry"] = [entry.payload() for entry in _registry()]

    bundle = tmp_path / "rebind.json"
    bundle.write_text(json.dumps({
        "schema": ADAPTER_BUNDLE_SCHEMA,
        "adapter_result": _adapter(),
        "native_events": _events(),
        "adapter_request": request,
    }, sort_keys=True))
    route = tmp_path / "route.json"
    route.write_text(json.dumps(_route(), sort_keys=True))
    result, metadata = _adapter_rebind_check(bundle, route, required=True)
    assert result["status"] == "PASS"
    assert metadata["join_status"] == "READY_FOR_PREFLIGHT"


def test_native_rebind_bundle_rejects_forged_serialized_adapter(tmp_path):
    from test_peerrolebench_pipe1_adapter_route_join import _adapter, _events, _request, _route
    from peerrolebench_pipe3_live_contract_qualification import _registry

    adapter = _adapter()
    adapter["selection_binding"]["target_selection"]["chosen_peer_id"] = "peer-c"
    bundle = tmp_path / "forged.json"
    request = _request()
    request["registry"] = [entry.payload() for entry in _registry()]
    bundle.write_text(json.dumps({
        "schema": ADAPTER_BUNDLE_SCHEMA,
        "adapter_result": adapter,
        "native_events": _events(),
        "adapter_request": request,
    }, sort_keys=True))
    route = tmp_path / "route.json"
    route.write_text(json.dumps(_route(), sort_keys=True))
    result, metadata = _adapter_rebind_check(bundle, route, required=True)
    assert result["status"] == "FAIL"
    assert metadata["join_status"] == "UNKNOWN"


def test_full_preflight_requires_native_rebind_in_strict_mode(tmp_path):
    route = tmp_path / "route.json"
    route.write_text(json.dumps(_valid_receipt(), sort_keys=True))
    out = tmp_path / "strict-missing"
    run(out, route, require_adapter_join=True)
    receipt = _load_receipt(out)
    adapter_check = next(item for item in receipt["checks"] if item["check"] == "adapter_route_join")
    assert adapter_check["status"] == "BLOCKED"
    assert receipt["status"] == "BLOCKED_PRE_EXECUTION"


def test_full_preflight_records_native_rebind_pass(tmp_path):
    from test_peerrolebench_pipe1_adapter_route_join import _adapter, _events, _request, _route
    from peerrolebench_pipe3_live_contract_qualification import _registry

    request = _request()
    request["registry"] = [entry.payload() for entry in _registry()]
    bundle = tmp_path / "rebind.json"
    bundle.write_text(json.dumps({
        "schema": ADAPTER_BUNDLE_SCHEMA,
        "adapter_result": _adapter(),
        "native_events": _events(),
        "adapter_request": request,
    }, sort_keys=True))
    route = tmp_path / "route.json"
    route.write_text(json.dumps(_route(), sort_keys=True))
    out = tmp_path / "strict-valid"
    run(out, route, adapter_bundle=bundle, require_adapter_join=True)
    receipt = _load_receipt(out)
    adapter_check = next(item for item in receipt["checks"] if item["check"] == "adapter_route_join")
    assert adapter_check["status"] == "PASS"
    assert receipt["status"] == "BLOCKED_PRE_EXECUTION"
    assert receipt["scientific_claim_allowed"] is False
