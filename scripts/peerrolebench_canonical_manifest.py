"""Fail-closed validator for the canonical seven-arm engineering manifest.

The canonical manifest is a *nested envelope* around the already registered
``RootRunnerManifest``.  It deliberately does not introduce a second root
identity: the nested ``root`` payload is parsed through
``RootRunnerManifest.validate`` and the registered baseline contract is
checked through ``validate_contract``.

This module is model-free.  It only validates a JSON-like mapping and is safe
to run before a runner, API request, or GPU allocation is started.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping, Sequence

from peerrolebench_baseline_contract import (
    BASELINE_ARM_SPECS,
    COST_FIELDS,
    UNKNOWN_RULE,
    contract_digest,
    validate_contract,
)
from peerrolebench_baseline_root_contract import RootRunnerManifest


CANONICAL_MANIFEST_VERSION = "artifactrole-canonical-seven-arm-v1"
EXPECTED_ARM_NAMES = tuple(spec.name for spec in BASELINE_ARM_SPECS)
EXPECTED_CHANNEL_IDS = ("situated_judgment", "raw_acceptance", "terminal_outcome")
EXPECTED_CELL_CASES = ("positive", "unknown", "late", "duplicate", "mutation")
EXPECTED_DISPOSITIONS = {
    "positive": "eligible_update",
    "unknown": "unknown_no_update",
    "late": "preflight_rejection",
    "duplicate": "preflight_rejection",
    "mutation": "preflight_rejection",
}
STREAM_DIGEST_KEYS = (
    "ordered_candidate_menu",
    "candidate_registry",
    "public_phi",
    "offer_stream",
    "read_cut_decision",
    "arrival_schedule",
    "rng_seed_schedule",
    "propensity",
    "state_schema",
    "state_init",
)
ALLOWED_STATUS = frozenset({"engineering_matrix", "live", "baseline_frozen"})
ALLOWED_COST_MODES = frozenset({"offline_unmeasured", "live_measured"})
ASSIGNMENT_SEMANTICS = "assignment_before_task_start_v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    """Return the canonical SHA-256 digest used by this envelope."""

    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require_digest(name: str, value: Any) -> str:
    if not isinstance(value, str) or len(value) != 64 or value != value.lower():
        raise ValueError(f"{name} must be a lowercase 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a lowercase 64-character sha256") from exc
    return value


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _root_manifest(root: Any) -> tuple[dict[str, Any], str]:
    """Validate and normalize the nested ``RootRunnerManifest`` payload."""

    if isinstance(root, RootRunnerManifest):
        payload = root.validate()
        return payload, root.digest()
    raw = dict(_mapping(root, "root"))
    required = (
        "root_id", "root_commit", "source_digest", "generator_digest", "scorer_digest",
        "schedule_digest", "rng_schedule_digest", "registry_digest", "seed_split",
        "arm_names", "rng_algorithm", "visibility_rule", "max_episode_attempts",
        "max_api_calls", "max_wall_seconds",
    )
    root_metadata = (
        "task_id", "structural_signature", "authority_kind", "split",
        "material_manifest_digest", "task_contract_digest", "adapter_digest",
        "sandbox_digest", "worker_limits_digest",
    )
    missing = [key for key in (*required, *root_metadata) if key not in raw]
    if missing:
        raise ValueError(f"root missing fields={missing}")
    for key in ("task_id", "structural_signature", "authority_kind"):
        if not isinstance(raw[key], str) or not raw[key].strip():
            raise ValueError(f"root.{key} must be a non-empty string")
    split = raw["split"]
    if not isinstance(split, Sequence) or isinstance(split, (str, bytes)) or not split:
        raise ValueError("root.split must be a non-empty ordered array")
    if tuple(sorted(set(split))) != tuple(split):
        raise ValueError("root.split must be sorted and unique")
    for key in (
        "material_manifest_digest", "task_contract_digest", "adapter_digest",
        "sandbox_digest", "worker_limits_digest",
    ):
        _require_digest(f"root.{key}", raw[key])
    kwargs = {key: raw[key] for key in required}
    kwargs["seed_split"] = tuple(kwargs["seed_split"])
    kwargs["arm_names"] = tuple(kwargs["arm_names"])
    try:
        manifest = RootRunnerManifest(**kwargs)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid nested root manifest: {exc}") from exc
    payload = manifest.validate()
    supplied = raw.get("manifest_digest", raw.get("root_manifest_digest"))
    if supplied is not None and supplied != manifest.digest():
        raise ValueError("nested root manifest_digest mismatch")
    payload.update({key: raw[key] for key in root_metadata})
    return payload, manifest.digest()


def _validate_contract_envelope(contract: Any) -> dict[str, Any]:
    raw = dict(_mapping(contract, "contract"))
    expected = validate_contract()
    # A contract digest cannot be used as a substitute for its contents.
    if raw != expected:
        if raw.get("contract_digest") == expected["contract_digest"]:
            raise ValueError("contract contents do not match the registered baseline contract")
        raise ValueError("contract differs from the registered baseline contract")
    if contract_digest({key: value for key, value in raw.items() if key != "contract_digest"}) != raw["contract_digest"]:
        raise ValueError("contract_digest mismatch")
    return expected


def _validate_arm_specs(raw_specs: Any, contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(raw_specs, Sequence) or isinstance(raw_specs, (str, bytes)):
        raise ValueError("arm_specs must be an array")
    if len(raw_specs) != len(EXPECTED_ARM_NAMES):
        raise ValueError("arm_specs must contain exactly seven arms")
    contract_rows = list(contract["arms"])
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_specs):
        row = dict(_mapping(raw, f"arm_specs[{index}]"))
        if row.get("name") != EXPECTED_ARM_NAMES[index]:
            raise ValueError("arm_specs order differs from the registered baseline matrix")
        for key, value in contract_rows[index].items():
            if row.get(key) != value:
                raise ValueError(f"arm_specs[{index}].{key} differs from contract")
        for key in ("policy_factory", "policy_version", "namespace_digest"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"arm_specs[{index}].{key} is required")
        _require_digest(f"arm_specs[{index}].namespace_digest", row["namespace_digest"])
        temperature = row.get("temperature")
        exploration = row.get("exploration")
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)) or not math.isfinite(float(temperature)) or temperature <= 0:
            raise ValueError(f"arm_specs[{index}].temperature must be finite and > 0")
        if isinstance(exploration, bool) or not isinstance(exploration, (int, float)) or not math.isfinite(float(exploration)) or not 0 <= exploration < 1:
            raise ValueError(f"arm_specs[{index}].exploration must be in [0,1)")
        _require_digest(f"arm_specs[{index}].implementation_digest", row.get("implementation_digest"))
        supplied = row.get("spec_digest")
        _require_digest(f"arm_specs[{index}].spec_digest", supplied)
        expected_spec_digest = digest({key: value for key, value in row.items() if key != "spec_digest"})
        if supplied != expected_spec_digest:
            raise ValueError(f"arm_specs[{index}].spec_digest mismatch")
        result.append(row)
    return result


def _validate_channels(raw_channels: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_channels, Sequence) or isinstance(raw_channels, (str, bytes)):
        raise ValueError("channels must be an array")
    if len(raw_channels) != len(EXPECTED_CHANNEL_IDS):
        raise ValueError("channels must contain exactly three channel adapters")
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_channels):
        row = dict(_mapping(raw, f"channels[{index}]"))
        if row.get("channel_id") != EXPECTED_CHANNEL_IDS[index]:
            raise ValueError("channel IDs/order differ from the canonical stream")
        for key in ("mapping_version", "implementation_digest", "mapping_digest", "channel_digest"):
            if key not in row:
                raise ValueError(f"channels[{index}] missing {key}")
        _require_digest(f"channels[{index}].implementation_digest", row["implementation_digest"])
        _require_digest(f"channels[{index}].mapping_digest", row["mapping_digest"])
        supplied = _require_digest(f"channels[{index}].channel_digest", row["channel_digest"])
        expected = digest({key: value for key, value in row.items() if key != "channel_digest"})
        if supplied != expected:
            raise ValueError(f"channels[{index}].channel_digest mismatch")
        result.append(row)
    return result


def _validate_stream(stream: Any, stream_digests: Any) -> dict[str, str]:
    stream_map = dict(_mapping(stream, "stream"))
    digests = dict(_mapping(stream_digests, "stream_digests"))
    if tuple(digests) != STREAM_DIGEST_KEYS:
        raise ValueError("stream_digests keys/order differ from the canonical stream")
    if set(stream_map) != set(STREAM_DIGEST_KEYS):
        raise ValueError("stream keys differ from the canonical stream")
    for key in STREAM_DIGEST_KEYS:
        expected = digest(stream_map[key])
        supplied = _require_digest(f"stream_digests.{key}", digests[key])
        if supplied != expected:
            raise ValueError(f"stream_digests.{key} mismatch")
    return digests


def _validate_cells(raw_cells: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_cells, Sequence) or isinstance(raw_cells, (str, bytes)):
        raise ValueError("cells must be an array")
    expected_keys = {(channel, case) for channel in EXPECTED_CHANNEL_IDS for case in EXPECTED_CELL_CASES}
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_cells):
        row = dict(_mapping(raw, f"cells[{index}]"))
        channel = row.get("channel_id")
        case = row.get("case")
        key = (channel, case)
        if key not in expected_keys or key in seen:
            raise ValueError("cells must contain one canonical cell for every channel/case")
        seen.add(key)
        expected = EXPECTED_DISPOSITIONS[case]
        if row.get("expected_disposition") != expected:
            raise ValueError(f"cells[{index}] expected_disposition mismatch")
        if row.get("independent_unit") != "episode":
            raise ValueError(f"cells[{index}] independent_unit must be episode")
        if row.get("episode_count") != 1:
            raise ValueError(f"cells[{index}] episode_count must be one")
        expected_started = case == "positive"
        expected_updates = 1 if expected_started else 0
        started = row.get("expected_runner_started")
        updates = row.get("expected_updates")
        if started not in (False, True, 0, 1) or bool(started) != expected_started:
            raise ValueError(f"cells[{index}].expected_runner_started mismatch")
        if isinstance(updates, bool) or not isinstance(updates, int) or updates != expected_updates:
            raise ValueError(f"cells[{index}].expected_updates mismatch")
        seeds = row.get("seed_split")
        if not isinstance(seeds, Sequence) or isinstance(seeds, (str, bytes)) or not seeds:
            raise ValueError(f"cells[{index}].seed_split is required")
        if tuple(sorted(set(seeds))) != tuple(seeds):
            raise ValueError(f"cells[{index}].seed_split must be sorted and unique")
        supplied = _require_digest(f"cells[{index}].cell_digest", row.get("cell_digest"))
        if supplied != digest({key: value for key, value in row.items() if key != "cell_digest"}):
            raise ValueError(f"cells[{index}].cell_digest mismatch")
        result.append(row)
    if len(seen) != len(expected_keys):
        missing = sorted(expected_keys - seen)
        raise ValueError(f"cells missing canonical cases={missing}")
    return result


def _validate_execution(execution: Any, contract: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the execution/contract extension without running anything."""

    raw = dict(_mapping(execution, "execution"))
    required = {
        "unknown_rule", "selected_only", "cost_mode", "cost_schema_digest",
        "history_schema_digest", "assignment_semantics",
        "negative_cell_contract_digest", "denominator_preservation",
    }
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"execution missing fields={missing}")
    if raw["unknown_rule"] != UNKNOWN_RULE:
        raise ValueError("execution.unknown_rule differs from the registered contract")
    if raw["selected_only"] is not True:
        raise ValueError("execution.selected_only must be true")
    if raw["cost_mode"] not in ALLOWED_COST_MODES:
        raise ValueError("execution.cost_mode is invalid")
    expected_cost_digest = digest({"cost_fields": list(contract["cost_fields"])})
    if _require_digest("execution.cost_schema_digest", raw["cost_schema_digest"]) != expected_cost_digest:
        raise ValueError("execution.cost_schema_digest does not bind contract cost_fields")
    _require_digest("execution.history_schema_digest", raw["history_schema_digest"])
    if raw["assignment_semantics"] != ASSIGNMENT_SEMANTICS:
        raise ValueError("execution.assignment_semantics differs from the registered semantics")
    expected_negative_digest = digest({"expected_dispositions": EXPECTED_DISPOSITIONS})
    if _require_digest("execution.negative_cell_contract_digest", raw["negative_cell_contract_digest"]) != expected_negative_digest:
        raise ValueError("execution.negative_cell_contract_digest mismatch")
    if raw["denominator_preservation"] is not True:
        raise ValueError("execution.denominator_preservation must be true")
    return raw


def _without_digest(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "manifest_digest"}


def validate_canonical_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a normalized canonical seven-arm manifest.

    Every mutation that can change the registered arm order/specification,
    source channel, stream input, negative-cell semantics, or activation status
    is rejected before a runner may start.
    """

    raw = dict(_mapping(manifest, "manifest"))
    if raw.get("manifest_version") != CANONICAL_MANIFEST_VERSION:
        raise ValueError("unsupported canonical manifest_version")
    required = {
        "manifest_version", "root", "contract", "arm_specs", "channels", "stream",
        "stream_digests", "cells", "execution", "analysis_plan_digest",
        "closest_published", "status", "manifest_digest",
    }
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"canonical manifest missing fields={missing}")
    root_payload, root_digest = _root_manifest(raw["root"])
    contract = _validate_contract_envelope(raw["contract"])
    arm_specs = _validate_arm_specs(raw["arm_specs"], contract)
    arm_attested = _mapping(raw.get("arm_implementation_digests"), "arm_implementation_digests")
    if tuple(arm_attested) != EXPECTED_ARM_NAMES:
        raise ValueError("arm_implementation_digests keys/order differ from baseline matrix")
    for row in arm_specs:
        if arm_attested[row["name"]] != row["implementation_digest"]:
            raise ValueError(f"arm implementation digest mismatch for {row['name']}")
    channels = _validate_channels(raw["channels"])
    channel_attested = _mapping(raw.get("channel_implementation_digests"), "channel_implementation_digests")
    if tuple(channel_attested) != EXPECTED_CHANNEL_IDS:
        raise ValueError("channel_implementation_digests keys/order differ from canonical channels")
    for row in channels:
        if channel_attested[row["channel_id"]] != row["implementation_digest"]:
            raise ValueError(f"channel implementation digest mismatch for {row['channel_id']}")
    stream_digests = _validate_stream(raw["stream"], raw["stream_digests"])
    cells = _validate_cells(raw["cells"])
    execution = _validate_execution(raw["execution"], contract)
    _require_digest("analysis_plan_digest", raw["analysis_plan_digest"])
    closest = dict(_mapping(raw["closest_published"], "closest_published"))
    if closest.get("status") != "blocked_required" or closest.get("placeholder") is not True:
        raise ValueError("closest_published must retain the blocked_required placeholder")
    if not isinstance(closest.get("reason"), str) or not closest["reason"].strip():
        raise ValueError("closest_published blocked placeholder requires a reason")
    status = raw["status"]
    if status not in ALLOWED_STATUS:
        raise ValueError(f"unsupported canonical manifest status={status!r}")
    if status != "engineering_matrix":
        raise ValueError("live/baseline_frozen status is forbidden while closest_published is blocked")
    supplied_manifest_digest = _require_digest("manifest_digest", raw["manifest_digest"])
    if supplied_manifest_digest != digest(_without_digest(raw)):
        raise ValueError("canonical manifest_digest mismatch")
    # Return a copy so callers cannot mutate the object validated above.
    normalized = dict(raw)
    normalized["root"] = root_payload
    normalized["contract"] = contract
    normalized["arm_specs"] = arm_specs
    normalized["channels"] = channels
    normalized["stream_digests"] = stream_digests
    normalized["cells"] = cells
    normalized["execution"] = execution
    normalized["root_manifest_digest"] = root_digest
    normalized["valid"] = True
    return normalized


def validate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Backward-compatible short alias for :func:`validate_canonical_manifest`."""

    return validate_canonical_manifest(manifest)


def validate_runtime_binding(
    manifest: Mapping[str, Any],
    *,
    root_commit: str,
    registry_digest: str,
    schedule_digest: str,
    rng_schedule_digest: str,
    stream_values: Mapping[str, Any],
    arm_names: Sequence[str] = EXPECTED_ARM_NAMES,
) -> dict[str, Any]:
    """Bind a validated envelope to one concrete offer/schedule stream.

    The caller supplies the already materialized runtime values; this helper
    only compares their canonical digests to the sealed manifest.  It is
    intentionally side-effect free and must run before policy construction.
    """

    normalized = validate_canonical_manifest(manifest)
    root = normalized["root"]
    if root.get("root_commit") != root_commit:
        raise ValueError("runtime root_commit differs from canonical manifest")
    for name, actual in (
        ("registry_digest", registry_digest),
        ("schedule_digest", schedule_digest),
        ("rng_schedule_digest", rng_schedule_digest),
    ):
        expected = _require_digest(f"runtime.{name}", actual)
        if root.get(name) != expected:
            raise ValueError(f"runtime {name} differs from canonical manifest")
    if tuple(arm_names) != EXPECTED_ARM_NAMES:
        raise ValueError("runtime arm order differs from canonical manifest")
    if set(stream_values) != set(STREAM_DIGEST_KEYS):
        raise ValueError("runtime stream keys differ from canonical stream")
    for key in STREAM_DIGEST_KEYS:
        expected = normalized["stream_digests"][key]
        actual = digest(stream_values[key])
        if actual != expected:
            raise ValueError(f"runtime stream digest mismatch: {key}")
    return {
        "bound": True,
        "manifest_digest": normalized["manifest_digest"],
        "root_manifest_digest": normalized["root_manifest_digest"],
        "stream_digests": dict(normalized["stream_digests"]),
    }


def manifest_digest(manifest: Mapping[str, Any]) -> str:
    """Compute the envelope digest without validating it."""

    return digest(_without_digest(manifest))


__all__ = [
    "ALLOWED_STATUS",
    "CANONICAL_MANIFEST_VERSION",
    "EXPECTED_ARM_NAMES",
    "EXPECTED_CELL_CASES",
    "EXPECTED_CHANNEL_IDS",
    "EXPECTED_DISPOSITIONS",
    "ALLOWED_COST_MODES",
    "ASSIGNMENT_SEMANTICS",
    "STREAM_DIGEST_KEYS",
    "digest",
    "manifest_digest",
    "validate_runtime_binding",
    "validate_canonical_manifest",
    "validate_manifest",
]
