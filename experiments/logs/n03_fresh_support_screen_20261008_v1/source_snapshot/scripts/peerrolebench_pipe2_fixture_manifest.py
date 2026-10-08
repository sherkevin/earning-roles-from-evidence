"""Strict, zero-call authority seam for PIPE2 fixture bundles.

This module deals only with fixture bytes and their provenance.  It never imports
TeamBench generators, loads candidate Python, invokes a grader, calls an LLM, or
executes a GPU job.  A manifest is an authority *candidate*; this seam deliberately
rejects ``benchmark_qualified=true`` so that fixture authority cannot silently be
promoted by a loader.

The public loader verifies all recorded source/expected digests, but returns only the
public source bytes and the public schema.  The expected bytes are used solely for
integrity verification and are never put into the public payload.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


MANIFEST_SCHEMA_VERSION = "pipe2-fixture-authority-v1"
TASK_ID = "PIPE2_data_pipeline"
AUTHORITY_KINDS = frozenset({"pinned", "derived", "valid_subset"})
SPLITS = frozenset({"public", "hidden"})
SHA256_HEX_LENGTH = 64


class ManifestError(ValueError):
    """Raised when a manifest or any referenced fixture fails closed validation."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _is_digest(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != SHA256_HEX_LENGTH:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _required(mapping: Mapping[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ManifestError(f"manifest missing required field: {key}")
    return mapping[key]


def _validate_columns(columns: Any, *, where: str) -> list[str]:
    if not isinstance(columns, list) or not columns:
        raise ManifestError(f"{where}.schema_columns must be a non-empty list")
    if any(not isinstance(value, str) or not value for value in columns):
        raise ManifestError(f"{where}.schema_columns must contain non-empty strings")
    if len(set(columns)) != len(columns):
        raise ManifestError(f"{where}.schema_columns contains duplicate columns")
    return list(columns)


def _safe_relative(root: Path, value: Any, *, where: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{where} must be a non-empty relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ManifestError(f"{where} must stay inside the fixture bundle")
    resolved_root = root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ManifestError(f"{where} escapes the fixture bundle") from exc
    if not resolved.is_file():
        raise ManifestError(f"{where} does not reference a file: {value}")
    return resolved


def _validate_policy(policy: Any) -> dict[str, Any]:
    if not isinstance(policy, dict):
        raise ManifestError("malformed_policy must be an object")
    required = {"invalid_action", "unknown_action", "emits_label"}
    missing = sorted(required - set(policy))
    if missing:
        raise ManifestError("malformed_policy missing required fields: " + ", ".join(missing))
    if policy.get("invalid_action") != "reject_without_label":
        raise ManifestError("malformed fixtures must be rejected without a label")
    if policy.get("unknown_action") != "unknown_without_label":
        raise ManifestError("unknown fixtures must remain UNKNOWN without a label")
    if policy.get("emits_label") is not False:
        raise ManifestError("malformed_policy cannot emit a silent label")
    # A fallback value is an implicit label path even when emits_label is false.
    if any(key in policy for key in ("fallback_label", "default_label", "label")):
        raise ManifestError("malformed_policy contains an implicit label fallback")
    return copy.deepcopy(policy)


def _root_digest(manifest: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(manifest))
    body.pop("root_digest", None)
    return sha256_bytes(_canonical(body))


def _validate_shape(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise ManifestError("manifest must be a JSON object")
    required = {
        "schema_version", "task_id", "authority_kind", "teambench_commit",
        "generator_sha256", "overlay_sha256", "schema", "splits", "fixtures",
        "malformed_policy", "root_digest", "benchmark_qualified",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ManifestError("manifest missing required fields: " + ", ".join(missing))
    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise ManifestError("unsupported PIPE2 fixture manifest schema")
    if manifest["task_id"] != TASK_ID:
        raise ManifestError("manifest task_id is not PIPE2_data_pipeline")
    if manifest["authority_kind"] not in AUTHORITY_KINDS:
        raise ManifestError("authority_kind must be pinned, derived, or valid_subset")
    commit = manifest["teambench_commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ManifestError("teambench_commit must be a lowercase 40-character git SHA")
    for key in ("generator_sha256", "overlay_sha256", "root_digest"):
        if not _is_digest(manifest[key]):
            raise ManifestError(f"{key} must be a SHA-256 hex digest")
    if manifest.get("benchmark_qualified") is not False:
        raise ManifestError("PIPE2 fixture manifests cannot be benchmark-qualified")

    schema = _required(manifest, "schema")
    if not isinstance(schema, Mapping):
        raise ManifestError("schema must be an object")
    if set(schema) - {"name", "columns", "key_columns"}:
        raise ManifestError("schema contains unknown fields")
    if not isinstance(schema.get("name"), str) or not schema["name"]:
        raise ManifestError("schema.name must be a non-empty string")
    schema_columns = _validate_columns(schema.get("columns"), where="schema")
    key_columns = schema.get("key_columns")
    if not isinstance(key_columns, list) or not key_columns or any(value not in schema_columns for value in key_columns):
        raise ManifestError("schema.key_columns must be a non-empty subset of schema.columns")
    if len(set(key_columns)) != len(key_columns):
        raise ManifestError("schema.key_columns contains duplicate columns")

    splits = _required(manifest, "splits")
    if not isinstance(splits, Mapping) or set(splits) != SPLITS:
        raise ManifestError("splits must contain exactly public and hidden seed lists")
    split_seeds: dict[str, list[int]] = {}
    all_split_seeds: list[int] = []
    for split in ("public", "hidden"):
        values = splits[split]
        if not isinstance(values, list) or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in values):
            raise ManifestError(f"splits.{split} must be a list of integer seeds")
        if len(set(values)) != len(values):
            raise ManifestError(f"splits.{split} contains duplicate seeds")
        split_seeds[split] = list(values)
        all_split_seeds.extend(values)
    if len(set(all_split_seeds)) != len(all_split_seeds):
        raise ManifestError("a seed cannot occur in both public and hidden splits")

    fixtures = _required(manifest, "fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ManifestError("fixtures must be a non-empty list")
    fixture_seeds: set[int] = set()
    normalized_fixtures: list[dict[str, Any]] = []
    for index, item in enumerate(fixtures):
        where = f"fixtures[{index}]"
        if not isinstance(item, Mapping):
            raise ManifestError(f"{where} must be an object")
        required_item = {"seed", "split", "schema_columns", "source_path", "expected_path",
                         "source_sha256", "expected_sha256"}
        missing_item = sorted(required_item - set(item))
        if missing_item:
            raise ManifestError(f"{where} missing required fields: {', '.join(missing_item)}")
        seed = item["seed"]
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ManifestError(f"{where}.seed must be an integer")
        if seed in fixture_seeds:
            raise ManifestError(f"duplicate fixture seed: {seed}")
        fixture_seeds.add(seed)
        split = item["split"]
        if split not in SPLITS:
            raise ManifestError(f"{where}.split is unknown: {split!r}")
        if seed not in split_seeds[split]:
            raise ManifestError(f"{where}.seed is absent from splits.{split}")
        columns = _validate_columns(item["schema_columns"], where=where)
        if columns != schema_columns:
            raise ManifestError(f"{where}.schema_columns disagrees with schema.columns")
        if not _is_digest(item["source_sha256"]) or not _is_digest(item["expected_sha256"]):
            raise ManifestError(f"{where} source/expected digest is invalid")
        source_path = item["source_path"]
        expected_path = item["expected_path"]
        if source_path == expected_path:
            raise ManifestError(f"{where} source_path and expected_path must differ")
        normalized_fixtures.append(dict(item))
    if fixture_seeds != set(all_split_seeds):
        raise ManifestError("splits and fixtures must enumerate exactly the same seeds")
    if len(fixtures) != len(fixture_seeds):
        raise ManifestError("duplicate fixture seeds are not allowed")
    _validate_policy(manifest["malformed_policy"])
    if manifest["root_digest"] != _root_digest(manifest):
        raise ManifestError("root_digest does not match manifest contents")
    return copy.deepcopy(dict(manifest))


def _read_and_verify(manifest_path: Path) -> tuple[dict[str, Any], dict[int, bytes]]:
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest: {manifest_path}") from exc
    manifest = _validate_shape(raw)
    root = manifest_path.parent
    sources: dict[int, bytes] = {}
    for item in manifest["fixtures"]:
        seed = int(item["seed"])
        source = _safe_relative(root, item["source_path"], where=f"fixtures[{seed}].source_path")
        expected = _safe_relative(root, item["expected_path"], where=f"fixtures[{seed}].expected_path")
        source_bytes = source.read_bytes()
        expected_bytes = expected.read_bytes()
        if sha256_bytes(source_bytes) != item["source_sha256"]:
            raise ManifestError(f"source digest mismatch for seed {seed}")
        if sha256_bytes(expected_bytes) != item["expected_sha256"]:
            raise ManifestError(f"expected digest mismatch for seed {seed}")
        sources[seed] = source_bytes
    return manifest, sources


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Validate a manifest and all referenced bytes, returning no fixture payload."""
    manifest, _ = _read_and_verify(Path(path))
    return manifest


def load_public_fixture(path: str | Path, seed: int) -> dict[str, Any]:
    """Return only a public fixture's source bytes and schema.

    Integrity checking reads the hidden expected bytes internally, but the returned
    mapping contains no expected path, expected digest, or expected bytes.
    """
    manifest, sources = _read_and_verify(Path(path))
    if seed not in manifest["splits"]["public"]:
        raise ManifestError(f"seed {seed} is not in the public split")
    item = next(item for item in manifest["fixtures"] if item["seed"] == seed)
    return {
        "task_id": manifest["task_id"],
        "seed": seed,
        "split": "public",
        "schema_name": manifest["schema"]["name"],
        "schema_columns": list(manifest["schema"]["columns"]),
        "key_columns": list(manifest["schema"]["key_columns"]),
        "source_bytes": sources[seed],
        "source_sha256": item["source_sha256"],
        "authority_kind": manifest["authority_kind"],
        "fixture_authority_digest": manifest["root_digest"],
    }


def create_manifest(
    root: str | Path,
    *,
    authority_kind: str,
    teambench_commit: str,
    generator_sha256: str,
    overlay_sha256: str,
    schema_name: str,
    schema_columns: Sequence[str],
    key_columns: Sequence[str],
    fixtures: Sequence[Mapping[str, Any]],
    malformed_policy: Mapping[str, Any],
) -> dict[str, Any]:
    """Create a digest-bound manifest from existing fixture files.

    This helper performs no candidate execution.  Callers still need a separately
    reviewed decision before using a derived or valid-subset manifest scientifically.
    """
    root = Path(root)
    normalized: list[dict[str, Any]] = []
    split_values: dict[str, list[int]] = {"public": [], "hidden": []}
    columns = list(schema_columns)
    for item in fixtures:
        if not isinstance(item, Mapping):
            raise ManifestError("fixture records must be objects")
        seed = item.get("seed")
        split = item.get("split")
        if isinstance(seed, bool) or not isinstance(seed, int) or split not in SPLITS:
            raise ManifestError("fixture records require an integer seed and known split")
        source_path = str(item.get("source_path", ""))
        expected_path = str(item.get("expected_path", ""))
        source = _safe_relative(root, source_path, where="source_path")
        expected = _safe_relative(root, expected_path, where="expected_path")
        normalized.append({
            "seed": seed, "split": split, "schema_columns": list(columns),
            "source_path": source_path, "expected_path": expected_path,
            "source_sha256": sha256_bytes(source.read_bytes()),
            "expected_sha256": sha256_bytes(expected.read_bytes()),
        })
        split_values[split].append(seed)
    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "authority_kind": authority_kind,
        "teambench_commit": teambench_commit,
        "generator_sha256": generator_sha256,
        "overlay_sha256": overlay_sha256,
        "schema": {"name": schema_name, "columns": columns, "key_columns": list(key_columns)},
        "splits": split_values,
        "fixtures": sorted(normalized, key=lambda value: value["seed"]),
        "malformed_policy": dict(malformed_policy),
        "benchmark_qualified": False,
    }
    manifest["root_digest"] = _root_digest(manifest)
    return _validate_shape(manifest)


__all__ = [
    "AUTHORITY_KINDS", "MANIFEST_SCHEMA_VERSION", "ManifestError", "TASK_ID",
    "create_manifest", "load_manifest", "load_public_fixture", "sha256_bytes",
]
