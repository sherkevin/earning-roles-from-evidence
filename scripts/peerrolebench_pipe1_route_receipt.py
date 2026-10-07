"""Fail-closed PIPE1 source→target route receipt contract.

The receipt is an operator-owned, zero-call serialization of one candidate route.
It deliberately separates public selected-only fields from operator-only expected
and scorer hashes.  This module performs structural checks only; it does not run
actors, a grader, a model, or a GPU job.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

SCHEMA_VERSION = "pipe1-route-receipt-v1"
DIGEST_LENGTH = 64
_HEX = set("0123456789abcdef")

_TOP_KEYS = {
    "schema_version", "route_id", "route_status", "source", "target", "lineage",
    "candidate_registry", "allocation", "provider", "clock", "costs", "visibility",
    "operator_only", "order",
}
_MATERIAL_KEYS = {"seed", "task_id", "root_id", "material_digest", "task_timezone"}
_REGISTRY_KEYS = {"registry_id", "registry_version", "registry_digest", "candidates"}
_CANDIDATE_KEYS = {"candidate_id", "version"}
_ALLOCATION_KEYS = {"algorithm", "seed", "permutation", "probabilities", "propensities", "draw", "chosen"}
_PROVIDER_KEYS = {"provider", "endpoint_id", "model", "model_revision", "request_config_digest", "secret_free"}
_CLOCK_KEYS = {"started_utc", "finished_utc", "task_timezone", "started_local", "finished_local"}
_COST_KEYS = {"wall_seconds", "input_tokens", "output_tokens", "api_calls", "gpu_seconds"}
_VISIBILITY_KEYS = {"selected_only", "selection_read_cut", "eligible_candidate_ids", "chosen_candidate_id", "observed_candidate_ids", "visible_fields", "forbidden_fields"}
_OPERATOR_KEYS = {"expected_hash", "scorer_hash"}
_ORDER_KEYS = {"event", "seq", "at_utc", "status"}

# Sequence is the causal contract.  Allocation is sealed before the target route.
EXPECTED_EVENTS = (
    "source_material", "source_message", "source_artifact", "source_executor_pre",
    "source_executor_post", "source_verifier_pre", "source_verifier_post",
    "target_material", "allocation", "target_message", "target_artifact",
    "target_executor_pre", "target_executor_post", "target_verifier_pre",
    "target_verifier_post",
)


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == DIGEST_LENGTH and value == value.lower() and set(value) <= _HEX


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _finite_nonnegative(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and float(value) >= 0


def _aware(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo is not None and dt.utcoffset() is not None else None


def _utc(value: Any) -> datetime | None:
    dt = _aware(value)
    if dt is None or dt.utcoffset() != timezone.utc.utcoffset(dt):
        return None
    return dt


def _error(errors: list[str], path: str, reason: str) -> None:
    errors.append(f"{path}: {reason}")


def _exact_keys(obj: Mapping[str, Any], expected: set[str], path: str, errors: list[str]) -> None:
    missing = expected - set(obj)
    extra = set(obj) - expected
    if missing:
        _error(errors, path, f"missing={sorted(missing)}")
    if extra:
        _error(errors, path, f"unknown={sorted(extra)}")


def _check_material(obj: Any, path: str, errors: list[str]) -> None:
    if not isinstance(obj, Mapping):
        _error(errors, path, "must be object")
        return
    _exact_keys(obj, _MATERIAL_KEYS, path, errors)
    if type(obj.get("seed")) is not int or obj.get("seed") < 0:
        _error(errors, path + ".seed", "must be non-negative integer")
    for field in ("task_id", "root_id", "task_timezone"):
        if not _nonempty(obj.get(field)):
            _error(errors, path + "." + field, "must be non-empty string")
    if not _is_digest(obj.get("material_digest")):
        _error(errors, path + ".material_digest", "must be lowercase sha256")
    try:
        ZoneInfo(obj.get("task_timezone"))
    except Exception:
        _error(errors, path + ".task_timezone", "must be valid IANA timezone")


def _check_lineage_chain(chain: Any, name: str, errors: list[str]) -> None:
    if not isinstance(chain, Mapping):
        _error(errors, "lineage." + name, "must be object")
        return
    expected = {
        "material_event_id", "message_event_id", "message_digest", "artifact_event_id", "artifact_digest",
        "executor_event_id", "executor_pre_workspace_digest", "executor_post_workspace_digest",
        "verifier_event_id", "verifier_pre_attestation_digest", "verifier_post_attestation_digest",
    }
    _exact_keys(chain, expected, "lineage." + name, errors)
    for field in ("material_event_id", "message_event_id", "artifact_event_id", "executor_event_id", "verifier_event_id"):
        if not _nonempty(chain.get(field)):
            _error(errors, f"lineage.{name}.{field}", "must be non-empty string")
    for field in ("message_digest", "artifact_digest", "executor_pre_workspace_digest", "executor_post_workspace_digest", "verifier_pre_attestation_digest", "verifier_post_attestation_digest"):
        if not _is_digest(chain.get(field)):
            _error(errors, f"lineage.{name}.{field}", "must be lowercase sha256")
    # The route receipt carries a compact hash chain so a one-field mutation
    # cannot pass as an unrelated but well-formed digest.
    if all(_is_digest(chain.get(field)) for field in ("message_digest", "artifact_digest", "executor_pre_workspace_digest", "executor_post_workspace_digest", "verifier_pre_attestation_digest", "verifier_post_attestation_digest")):
        expected_artifact = canonical_digest({"message_digest": chain["message_digest"]})
        expected_workspace = canonical_digest({"pre_workspace_digest": chain["executor_pre_workspace_digest"], "artifact_digest": expected_artifact})
        expected_attestation = canonical_digest({"pre_attestation_digest": chain["verifier_pre_attestation_digest"], "post_workspace_digest": expected_workspace})
        if chain["artifact_digest"] != expected_artifact:
            _error(errors, f"lineage.{name}.artifact_digest", "does not bind message digest")
        if chain["executor_post_workspace_digest"] != expected_workspace:
            _error(errors, f"lineage.{name}.executor_post_workspace_digest", "does not bind pre-workspace and artifact")
        if chain["verifier_post_attestation_digest"] != expected_attestation:
            _error(errors, f"lineage.{name}.verifier_post_attestation_digest", "does not bind verifier pre-attestation and executor post-workspace")


def _check_registry(registry: Any, errors: list[str]) -> list[str]:
    if not isinstance(registry, Mapping):
        _error(errors, "candidate_registry", "must be object")
        return []
    _exact_keys(registry, _REGISTRY_KEYS, "candidate_registry", errors)
    for field in ("registry_id", "registry_version"):
        if not _nonempty(registry.get(field)):
            _error(errors, "candidate_registry." + field, "must be non-empty string")
    if not _is_digest(registry.get("registry_digest")):
        _error(errors, "candidate_registry.registry_digest", "must be lowercase sha256")
    candidates = registry.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        _error(errors, "candidate_registry.candidates", "must be non-empty list")
        return []
    ids: list[str] = []
    for i, candidate in enumerate(candidates):
        path = f"candidate_registry.candidates[{i}]"
        if not isinstance(candidate, Mapping):
            _error(errors, path, "must be object")
            continue
        _exact_keys(candidate, _CANDIDATE_KEYS, path, errors)
        if not _nonempty(candidate.get("candidate_id")) or not _nonempty(candidate.get("version")):
            _error(errors, path, "candidate_id/version must be non-empty")
        ids.append(f"{candidate.get('candidate_id')}@{candidate.get('version')}")
    if len(ids) != len(set(ids)):
        _error(errors, "candidate_registry.candidates", "duplicate candidate/version")
    if _is_digest(registry.get("registry_digest")):
        expected = canonical_digest({
            "registry_id": registry.get("registry_id"),
            "registry_version": registry.get("registry_version"),
            "candidates": registry.get("candidates"),
        })
        if registry.get("registry_digest") != expected:
            _error(errors, "candidate_registry.registry_digest", "does not bind registry/version/candidates")
    return ids


def _check_allocation(allocation: Any, candidate_keys: list[str], errors: list[str]) -> None:
    if not isinstance(allocation, Mapping):
        _error(errors, "allocation", "must be object")
        return
    _exact_keys(allocation, _ALLOCATION_KEYS, "allocation", errors)
    if not _nonempty(allocation.get("algorithm")):
        _error(errors, "allocation.algorithm", "must be non-empty string")
    if type(allocation.get("seed")) is not int or allocation.get("seed") < 0:
        _error(errors, "allocation.seed", "must be non-negative integer")
    permutation = allocation.get("permutation")
    if permutation != candidate_keys or len(permutation) != len(set(permutation)):
        _error(errors, "allocation.permutation", "must equal registry order exactly and contain no duplicates")
    probs = allocation.get("probabilities")
    props = allocation.get("propensities")
    for field, values in (("probabilities", probs), ("propensities", props)):
        if not isinstance(values, Mapping) or set(values) != set(candidate_keys):
            _error(errors, "allocation." + field, "must map every registered candidate exactly once")
            continue
        total = 0.0
        for key in candidate_keys:
            val = values.get(key)
            if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(float(val)) or not 0.0 <= float(val) <= 1.0:
                _error(errors, f"allocation.{field}.{key}", "must be finite in [0,1]")
            else:
                total += float(val)
        if abs(total - 1.0) > 1e-9:
            _error(errors, "allocation." + field, "must sum to one")
    draw = allocation.get("draw")
    if not isinstance(draw, (int, float)) or isinstance(draw, bool) or not math.isfinite(float(draw)) or not 0.0 <= float(draw) < 1.0:
        _error(errors, "allocation.draw", "must be finite in [0,1)")
    chosen = allocation.get("chosen")
    if chosen not in candidate_keys:
        _error(errors, "allocation.chosen", "must be registered candidate/version")
    elif isinstance(permutation, list) and isinstance(probs, Mapping) and isinstance(draw, (int, float)):
        cursor = 0.0
        expected = None
        for key in permutation:
            cursor += float(probs.get(key, 0.0))
            if float(draw) < cursor:
                expected = key
                break
        if expected != chosen:
            _error(errors, "allocation.chosen", "does not match permutation/probability/draw")


def _check_provider(provider: Any, errors: list[str]) -> None:
    if not isinstance(provider, Mapping):
        _error(errors, "provider", "must be object")
        return
    _exact_keys(provider, _PROVIDER_KEYS, "provider", errors)
    for field in ("provider", "endpoint_id", "model", "model_revision"):
        if not _nonempty(provider.get(field)):
            _error(errors, "provider." + field, "must be non-empty string")
    if not _is_digest(provider.get("request_config_digest")):
        _error(errors, "provider.request_config_digest", "must be lowercase sha256")
    if provider.get("secret_free") is not True:
        _error(errors, "provider.secret_free", "must be true")
    # ``secret_free`` is an explicit boolean attestation and is therefore
    # allowed.  Reject credential-bearing names/values while keeping ordinary
    # model names such as ``tokenizer-free`` out of the false-positive path.
    for key in provider:
        if any(fragment in str(key).lower() for fragment in ("api_key", "access_key", "authorization", "bearer", "token")):
            _error(errors, "provider", "contains secret-like field")
    for value in provider.values():
        if isinstance(value, str) and any(fragment in value.lower() for fragment in ("bearer ", "sk-", "api_key=")):
            _error(errors, "provider", "contains secret-like value")


def _check_clock(clock: Any, errors: list[str]) -> None:
    if not isinstance(clock, Mapping):
        _error(errors, "clock", "must be object")
        return
    _exact_keys(clock, _CLOCK_KEYS, "clock", errors)
    started, finished = _utc(clock.get("started_utc")), _utc(clock.get("finished_utc"))
    if started is None or finished is None or finished < started:
        _error(errors, "clock", "UTC interval invalid or not explicitly UTC")
    tzname = clock.get("task_timezone")
    try:
        zone = ZoneInfo(tzname)
    except Exception:
        zone = None
        _error(errors, "clock.task_timezone", "must be valid IANA timezone")
    local_start, local_finish = _aware(clock.get("started_local")), _aware(clock.get("finished_local"))
    if local_start is None or local_finish is None or local_finish < local_start:
        _error(errors, "clock", "local task interval invalid")
    if zone and started and finished and local_start and local_finish:
        if local_start != started.astimezone(zone) or local_finish != finished.astimezone(zone):
            _error(errors, "clock", "local timestamps do not match UTC and task timezone")


def _check_costs(costs: Any, errors: list[str]) -> None:
    phases = {"source_message", "source_executor", "source_verifier", "target_message", "target_executor", "target_verifier", "selection"}
    if not isinstance(costs, Mapping):
        _error(errors, "costs", "must be object")
        return
    if set(costs) != phases:
        _error(errors, "costs", f"must contain exactly {sorted(phases)}")
    for phase in phases:
        row = costs.get(phase)
        if not isinstance(row, Mapping):
            _error(errors, "costs." + phase, "must be object")
            continue
        _exact_keys(row, _COST_KEYS, "costs." + phase, errors)
        for field in _COST_KEYS:
            if not _finite_nonnegative(row.get(field)):
                _error(errors, f"costs.{phase}.{field}", "must be finite and non-negative")


def _check_visibility(visibility: Any, chosen: Any, candidate_keys: list[str], errors: list[str]) -> None:
    if not isinstance(visibility, Mapping):
        _error(errors, "visibility", "must be object")
        return
    _exact_keys(visibility, _VISIBILITY_KEYS, "visibility", errors)
    if visibility.get("selected_only") is not True:
        _error(errors, "visibility.selected_only", "must be true")
    if type(visibility.get("selection_read_cut")) is not int or visibility.get("selection_read_cut") < 0:
        _error(errors, "visibility.selection_read_cut", "must be non-negative integer")
    if visibility.get("eligible_candidate_ids") != candidate_keys:
        _error(errors, "visibility.eligible_candidate_ids", "must equal candidate registry order")
    if visibility.get("chosen_candidate_id") != chosen:
        _error(errors, "visibility.chosen_candidate_id", "must equal allocation choice")
    observed = visibility.get("observed_candidate_ids")
    if not isinstance(observed, list) or observed != [chosen]:
        _error(errors, "visibility.observed_candidate_ids", "selected-only route must observe chosen candidate only")
    for field in ("visible_fields", "forbidden_fields"):
        values = visibility.get(field)
        if not isinstance(values, list) or not values or any(not _nonempty(v) for v in values):
            _error(errors, "visibility." + field, "must be non-empty string list")
    if any(v in visibility.get("visible_fields", []) for v in ("expected_hash", "scorer_hash")):
        _error(errors, "visibility.visible_fields", "operator-only hashes cannot be visible")
    if not {"expected_hash", "scorer_hash"}.issubset(set(visibility.get("forbidden_fields", []))):
        _error(errors, "visibility.forbidden_fields", "must explicitly forbid expected/scorer hashes")


def _check_operator(operator: Any, public: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(operator, Mapping):
        _error(errors, "operator_only", "must be object")
        return
    _exact_keys(operator, _OPERATOR_KEYS, "operator_only", errors)
    for field in _OPERATOR_KEYS:
        if not _is_digest(operator.get(field)):
            _error(errors, "operator_only." + field, "must be lowercase sha256")
    forbidden_names = {"expected_hash", "scorer_hash", "hidden_tests", "gold_output"}
    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                # visibility.forbidden_fields names are a contract declaration,
                # not a leak of the corresponding operator value.
                if key in forbidden_names:
                    _error(errors, "public", f"contains operator-only field {key}")
                walk(child, path + "." + str(key))
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, path + f"[{i}]")
    walk({k: v for k, v in public.items() if k != "visibility"})
    for secret_value in operator.values():
        if isinstance(secret_value, str) and secret_value in json.dumps(public, ensure_ascii=False):
            _error(errors, "public", "contains operator-only hash value")


def validate_pipe1_route_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Return PASS/INVALID with deterministic reasons; malformed input fails closed."""
    errors: list[str] = []
    if not isinstance(receipt, Mapping):
        return {"status": "INVALID", "valid": False, "errors": ["receipt: must be object"]}
    _exact_keys(receipt, _TOP_KEYS, "receipt", errors)
    if receipt.get("schema_version") != SCHEMA_VERSION:
        _error(errors, "schema_version", "unsupported schema")
    if not _nonempty(receipt.get("route_id")):
        _error(errors, "route_id", "must be non-empty string")
    if receipt.get("route_status") != "COMPLETE":
        _error(errors, "route_status", "must be COMPLETE; UNKNOWN is not eligible")
    _check_material(receipt.get("source"), "source", errors)
    _check_material(receipt.get("target"), "target", errors)
    source, target = receipt.get("source"), receipt.get("target")
    if isinstance(source, Mapping) and isinstance(target, Mapping):
        if source.get("material_digest") == target.get("material_digest"):
            _error(errors, "source/target", "material digests overlap")
        if source.get("task_id") != target.get("task_id"):
            _error(errors, "source/target.task_id", "source and target must share the native task contract")
        if source.get("root_id") != target.get("root_id"):
            _error(errors, "source/target.root_id", "source and target must share one structural root")
        if source.get("seed") != 0 or target.get("seed") != 3:
            _error(errors, "source/target", "PIPE1 receipt must be source seed 0 -> target seed 3")
        if source.get("task_timezone") != target.get("task_timezone"):
            _error(errors, "source/target.task_timezone", "source and target task timezone mismatch")
    lineage = receipt.get("lineage")
    if not isinstance(lineage, Mapping):
        _error(errors, "lineage", "must be object")
    else:
        if set(lineage) != {"source", "target"}:
            _error(errors, "lineage", "must contain source and target chains")
        _check_lineage_chain(lineage.get("source"), "source", errors)
        _check_lineage_chain(lineage.get("target"), "target", errors)
    candidate_keys = _check_registry(receipt.get("candidate_registry"), errors)
    _check_allocation(receipt.get("allocation"), candidate_keys, errors)
    chosen = receipt.get("allocation", {}).get("chosen") if isinstance(receipt.get("allocation"), Mapping) else None
    _check_provider(receipt.get("provider"), errors)
    _check_clock(receipt.get("clock"), errors)
    _check_costs(receipt.get("costs"), errors)
    _check_visibility(receipt.get("visibility"), chosen, candidate_keys, errors)
    public = {k: v for k, v in receipt.items() if k != "operator_only"}
    _check_operator(receipt.get("operator_only"), public, errors)
    order = receipt.get("order")
    if not isinstance(order, list) or len(order) != len(EXPECTED_EVENTS):
        _error(errors, "order", "must list every causal event exactly once")
    else:
        names: list[str] = []
        prev_time: datetime | None = None
        for i, row in enumerate(order):
            path = f"order[{i}]"
            if not isinstance(row, Mapping):
                _error(errors, path, "must be object")
                continue
            _exact_keys(row, _ORDER_KEYS, path, errors)
            event = row.get("event")
            names.append(event)
            if row.get("seq") != i:
                _error(errors, path + ".seq", "sequence must be contiguous from zero")
            if row.get("status") != "COMPLETE":
                _error(errors, path + ".status", "UNKNOWN/incomplete event fails closed")
            timestamp = _utc(row.get("at_utc"))
            if timestamp is None:
                _error(errors, path + ".at_utc", "must be explicit UTC timestamp")
            elif prev_time and timestamp < prev_time:
                _error(errors, path + ".at_utc", "causal order timestamp regressed")
            else:
                prev_time = timestamp
        if names != list(EXPECTED_EVENTS):
            _error(errors, "order.event", "causal event order mismatch or overlap")
    valid = not errors
    return {"status": "PASS" if valid else "INVALID", "valid": valid, "errors": errors,
            "schema_version": SCHEMA_VERSION}


__all__ = ["SCHEMA_VERSION", "EXPECTED_EVENTS", "canonical_digest", "validate_pipe1_route_receipt"]
