from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe1_route_receipt import (  # noqa: E402
    EXPECTED_EVENTS,
    SCHEMA_VERSION,
    canonical_digest,
    validate_pipe1_route_receipt,
)

D0 = "0" * 64
D1 = "1" * 64
D2 = "2" * 64
D3 = "3" * 64
D4 = "4" * 64
D5 = "5" * 64
D6 = "6" * 64
D7 = "7" * 64
D8 = "8" * 64
D9 = "9" * 64
REGISTRY_CANDIDATES = [{"candidate_id": "peer-a", "version": "v1"}, {"candidate_id": "peer-b", "version": "v1"}]
REGISTRY_DIGEST = canonical_digest({"registry_id": "peer-registry", "registry_version": "v1", "candidates": REGISTRY_CANDIDATES})
ARTIFACT = canonical_digest({"message_digest": D2})
POST_WORKSPACE = canonical_digest({"pre_workspace_digest": D4, "artifact_digest": ARTIFACT})
POST_ATTESTATION = canonical_digest({"pre_attestation_digest": D6, "post_workspace_digest": POST_WORKSPACE})


def _receipt():
    base = datetime(2026, 10, 7, 0, 0, tzinfo=timezone.utc)
    times = [(base.replace(second=i)).isoformat().replace("+00:00", "Z") for i in range(len(EXPECTED_EVENTS))]
    return {
        "schema_version": SCHEMA_VERSION,
        "route_id": "pipe1-source0-target3-r0",
        "route_status": "COMPLETE",
        "source": {"seed": 0, "task_id": "PIPE1_etl_fix", "root_id": "pipe1-root-v1", "material_digest": D0, "task_timezone": "Asia/Shanghai"},
        "target": {"seed": 3, "task_id": "PIPE1_etl_fix", "root_id": "pipe1-root-v1", "material_digest": D1, "task_timezone": "Asia/Shanghai"},
        "lineage": {
            "source": {"material_event_id": "source-material-0", "message_event_id": "source-message-0", "message_digest": D2, "artifact_event_id": "source-artifact-0", "artifact_digest": ARTIFACT, "executor_event_id": "source-executor-0", "executor_pre_workspace_digest": D4, "executor_post_workspace_digest": POST_WORKSPACE, "verifier_event_id": "source-verifier-0", "verifier_pre_attestation_digest": D6, "verifier_post_attestation_digest": POST_ATTESTATION},
            "target": {"material_event_id": "target-material-3", "message_event_id": "target-message-3", "message_digest": D2, "artifact_event_id": "target-artifact-3", "artifact_digest": ARTIFACT, "executor_event_id": "target-executor-3", "executor_pre_workspace_digest": D4, "executor_post_workspace_digest": POST_WORKSPACE, "verifier_event_id": "target-verifier-3", "verifier_pre_attestation_digest": D6, "verifier_post_attestation_digest": POST_ATTESTATION},
        },
        "candidate_registry": {"registry_id": "peer-registry", "registry_version": "v1", "registry_digest": REGISTRY_DIGEST, "candidates": REGISTRY_CANDIDATES},
        "allocation": {"algorithm": "pcg64", "seed": 42, "permutation": ["peer-a@v1", "peer-b@v1"], "probabilities": {"peer-a@v1": 0.5, "peer-b@v1": 0.5}, "propensities": {"peer-a@v1": 0.5, "peer-b@v1": 0.5}, "draw": 0.25, "chosen": "peer-a@v1"},
        "provider": {"provider": "idealab", "endpoint_id": "internal", "model": "qwen-mini", "model_revision": "2026-10", "request_config_digest": D9, "secret_free": True},
        "clock": {"started_utc": times[0], "finished_utc": times[-1], "task_timezone": "Asia/Shanghai", "started_local": "2026-10-07T08:00:00+08:00", "finished_local": "2026-10-07T08:00:14+08:00"},
        "costs": {phase: {"wall_seconds": 1.0, "input_tokens": 1, "output_tokens": 1, "api_calls": 1, "gpu_seconds": 0.0} for phase in ("source_message", "source_executor", "source_verifier", "target_message", "target_executor", "target_verifier", "selection")},
        "visibility": {"selected_only": True, "selection_read_cut": 4, "eligible_candidate_ids": ["peer-a@v1", "peer-b@v1"], "chosen_candidate_id": "peer-a@v1", "observed_candidate_ids": ["peer-a@v1"], "visible_fields": ["task_spec", "history_digest", "source_summary"], "forbidden_fields": ["expected_hash", "scorer_hash"]},
        "operator_only": {"expected_hash": "a" * 64, "scorer_hash": "b" * 64},
        "order": [{"event": event, "seq": i, "at_utc": times[i], "status": "COMPLETE"} for i, event in enumerate(EXPECTED_EVENTS)],
    }


def assert_invalid(receipt):
    result = validate_pipe1_route_receipt(receipt)
    assert result["status"] == "INVALID", result
    assert result["valid"] is False
    assert result["errors"]


def test_valid_source0_target3_receipt_passes():
    result = validate_pipe1_route_receipt(_receipt())
    assert result == {"status": "PASS", "valid": True, "errors": [], "schema_version": SCHEMA_VERSION}


@pytest.mark.parametrize("mutation", [
    lambda r: r.pop("provider"),
    lambda r: r.update({"route_status": "UNKNOWN"}),
    lambda r: r["source"].update({"material_digest": r["target"]["material_digest"]}),
    lambda r: r["target"].update({"task_id": "other-task"}),
    lambda r: r["lineage"]["source"].update({"artifact_digest": "f" * 64}),
    lambda r: r["candidate_registry"]["candidates"][0].update({"version": "v2"}),
    lambda r: r["allocation"].update({"seed": -1}),
    lambda r: r["allocation"].update({"permutation": ["peer-b@v1", "peer-a@v1"]}),
    lambda r: r["allocation"]["propensities"].update({"peer-a@v1": 0.8}),
    lambda r: r["provider"].update({"request_config_digest": "secret-token"}),
    lambda r: r["clock"].update({"task_timezone": "not/a-zone"}),
    lambda r: r["costs"]["target_executor"].update({"wall_seconds": -1.0}),
    lambda r: r["visibility"].update({"selected_only": False}),
    lambda r: r["operator_only"].update({"expected_hash": "not-a-digest"}),
    lambda r: r["order"].__setitem__(8, {**r["order"][8], "seq": 15}),
    lambda r: r["order"].__setitem__(9, {**r["order"][9], "event": "allocation"}),
    lambda r: r["order"].__setitem__(0, {**r["order"][0], "status": "UNKNOWN"}),
])
def test_critical_mutations_fail_closed(mutation):
    receipt = deepcopy(_receipt())
    mutation(receipt)
    assert_invalid(receipt)


def test_unknown_public_hash_or_extra_field_is_rejected():
    receipt = _receipt()
    receipt["public_expected_hash"] = "a" * 64
    assert_invalid(receipt)
    receipt = _receipt()
    receipt["visibility"]["visible_fields"].append("expected_hash")
    assert_invalid(receipt)
