"""Versioned, reproducible material adapter for the PIPE2 derived-root candidate.

The pinned TeamBench generator writes CSV by joining fields with commas.  That
serialization is ambiguous when a value contains a comma, so four of the ten
seeded instances are malformed before any agent can act.  This adapter applies
one narrowly scoped overlay: it serializes the *same logical rows* with the
standard-library CSV writer.  It does not change the pipeline bugs, public
interfaces, prompts, ownership contract, or hidden expected semantics.

The adapter is deliberately a candidate-root loader rather than an active
benchmark.  A hash-only recipe records the pinned generator, overlay source,
per-seed derived bytes and visibility bookkeeping.  The expected output is
reconstructed for integrity checks but is never returned in an actor payload.
No LLM, candidate code, native grader, or GPU is invoked here.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
TEAMBENCH = ROOT / "references/benchmark_sources/TeamBench"
TEAMBENCH_COMMIT = "d185aef1916fd86a9ba554d581fd256319a973af"
TASK_ID = "PIPE2_data_pipeline"
RECIPE_SCHEMA_VERSION = "pipe2-derived-root-recipe-v1"
CANDIDATE_ID = "pipe2-csv-writer-v1"
OVERLAY_VERSION = CANDIDATE_ID
GENERATOR_RELATIVE_PATH = "generators/gen_pipe2_data_pipeline.py"
RECIPE_PATH = ROOT / "configs/aamas2027/pipe2_derived_root_candidate_v1.json"
SEEDS = tuple(range(10))


class DerivedRootError(ValueError):
    """Raised when a derived-root precondition or digest fails closed."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _source_hash(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def _ensure_pinned_source() -> tuple[Path, str]:
    actual = _git(TEAMBENCH, "rev-parse", "HEAD")
    if actual != TEAMBENCH_COMMIT:
        raise DerivedRootError(f"TeamBench commit mismatch: {actual} != {TEAMBENCH_COMMIT}")
    if _git(TEAMBENCH, "status", "--porcelain"):
        raise DerivedRootError("TeamBench worktree is dirty")
    source = TEAMBENCH / GENERATOR_RELATIVE_PATH
    actual_hash = _source_hash(source)
    return source, actual_hash


def _load_schema_pool() -> list[dict[str, Any]]:
    root = str(TEAMBENCH)
    if root not in sys.path:
        sys.path.insert(0, root)
    from generators.gen_pipe2_data_pipeline import SCHEMAS  # type: ignore
    return SCHEMAS


def csv_text(rows: list[list[str]], columns: list[str]) -> str:
    """Serialize logical PIPE2 rows with explicit, portable CSV settings."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter=",", quotechar='"',
                        quoting=csv.QUOTE_MINIMAL, lineterminator="\n",
                        doublequote=True, escapechar=None)
    writer.writerow(columns)
    writer.writerows(rows)
    return stream.getvalue()


def logical_rows(schema: Mapping[str, Any]) -> tuple[list[list[str]], list[list[str]]]:
    columns = list(schema["columns"])
    key_columns = list(schema["key_columns"])
    source_rows = [list(row) for row in schema["rows"]]
    kept = [row for row in source_rows
            if all(row[columns.index(key)].strip() for key in key_columns)]
    expected_rows = []
    for row in kept:
        expected_rows.append([
            value[: int(schema["truncation_limit"])]
            if schema["col_types"][index] == "str"
            and len(value) > int(schema["truncation_limit"])
            else value
            for index, value in enumerate(row)
        ])
    return source_rows, expected_rows


def _pinned_generated(seed: int) -> Any:
    root = str(TEAMBENCH)
    if root not in sys.path:
        sys.path.insert(0, root)
    from generators import registry  # type: ignore
    if Path(registry.__file__).resolve() != TEAMBENCH / "generators/registry.py":
        raise DerivedRootError("another package shadows the pinned TeamBench registry")
    generated = registry.get_generator(TASK_ID).generate(seed=seed)
    if generated.task_id != TASK_ID:
        raise DerivedRootError(f"unexpected generated task: {generated.task_id}")
    return generated


def derive_seed(seed: int, *, generated: Any | None = None,
                schemas: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if seed not in SEEDS:
        raise DerivedRootError(f"seed {seed} is outside the candidate recipe: {SEEDS}")
    generated = generated or _pinned_generated(seed)
    schemas = schemas or _load_schema_pool()
    schema = schemas[seed % len(schemas)]
    columns = list(schema["columns"])
    source_rows, expected_rows = logical_rows(schema)
    source = csv_text(source_rows, columns)
    expected = csv_text(expected_rows, columns)
    original_source = str(generated.workspace_files["data/source.csv"]).encode()
    original_expected = str(generated.workspace_files["data/expected_output.csv"]).encode()
    return {
        "seed": seed,
        "schema_name": schema["name"],
        "schema_index": seed % len(schemas),
        "columns": columns,
        "key_columns": list(schema["key_columns"]),
        "source_sha256": sha256_bytes(source.encode()),
        "expected_sha256": sha256_bytes(expected.encode()),
        "original_source_sha256": sha256_bytes(original_source),
        "original_expected_sha256": sha256_bytes(original_expected),
        "source_changed": source.encode() != original_source,
        "expected_changed": expected.encode() != original_expected,
        "source_row_count": len(source_rows),
        "expected_row_count": len(expected_rows),
        "serializer": "python-csv-writer-quote-minimal-lf-v1",
        "source_bytes": source,
        "expected_bytes": expected,
    }


def _recipe_overlay_hash() -> str:
    return _source_hash(Path(__file__).resolve())


def _recipe_body(records: list[dict[str, Any]], generator_sha256: str) -> dict[str, Any]:
    public = [seed for seed in SEEDS if seed in (0, 2, 3, 5, 7, 8)]
    hidden = [seed for seed in SEEDS if seed in (1, 4, 6, 9)]
    compact_records = [{key: value for key, value in record.items()
                        if key not in {"source_bytes", "expected_bytes"}}
                       for record in records]
    body: dict[str, Any] = {
        "schema_version": RECIPE_SCHEMA_VERSION,
        "candidate_id": CANDIDATE_ID,
        "status": "CANDIDATE_DERIVED_ROOT",
        "task_id": TASK_ID,
        "authority_kind": "derived",
        "base": {
            "repository": "nokia-applied-research/TeamBench",
            "teambench_commit": TEAMBENCH_COMMIT,
            "generator_path": GENERATOR_RELATIVE_PATH,
            "generator_sha256": generator_sha256,
        },
        "overlay": {
            "version": OVERLAY_VERSION,
            "module": "scripts/peerrolebench_pipe2_derived_material_adapter.py",
            "sha256": _recipe_overlay_hash(),
            "scope": "CSV serialization only; logical rows and pipeline code are unchanged",
        },
        "seeds": list(SEEDS),
        "visibility": {
            "public_shape_development": public,
            "hidden_shape_development": hidden,
            "status": "NOT_A_SCIENTIFIC_SPLIT",
            "note": "Visibility bookkeeping inherited from the prior shape audit; no confirmatory split is frozen.",
        },
        "serialization": {
            "delimiter": ",", "quotechar": '"', "quoting": "QUOTE_MINIMAL",
            "doublequote": True, "escapechar": None, "lineterminator": "\\n",
        },
        "malformed_policy": {
            "invalid_action": "reject_without_label",
            "unknown_action": "unknown_without_label",
            "emits_label": False,
        },
        "fixtures": compact_records,
        "benchmark_qualified": False,
        "scientific_claim_allowed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
    }
    body["root_digest"] = sha256_bytes(canonical(body))
    return body


def build_recipe() -> dict[str, Any]:
    source, generator_sha256 = _ensure_pinned_source()
    if _source_hash(source) != generator_sha256:
        raise DerivedRootError("generator hash changed during recipe build")
    schemas = _load_schema_pool()
    records = [derive_seed(seed, schemas=schemas) for seed in SEEDS]
    return _recipe_body(records, generator_sha256)


def _load_recipe(path: Path = RECIPE_PATH) -> dict[str, Any]:
    try:
        recipe = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DerivedRootError(f"cannot read derived recipe: {path}") from exc
    if not isinstance(recipe, dict) or recipe.get("schema_version") != RECIPE_SCHEMA_VERSION:
        raise DerivedRootError("unsupported PIPE2 derived recipe")
    body = copy.deepcopy(recipe)
    root_digest = body.pop("root_digest", None)
    if root_digest != sha256_bytes(canonical(body)):
        raise DerivedRootError("derived recipe root_digest mismatch")
    if recipe.get("candidate_id") != CANDIDATE_ID or recipe.get("task_id") != TASK_ID:
        raise DerivedRootError("derived recipe identity mismatch")
    if recipe.get("status") != "CANDIDATE_DERIVED_ROOT":
        raise DerivedRootError("derived recipe status cannot be promoted implicitly")
    if recipe.get("benchmark_qualified") is not False or recipe.get("scientific_claim_allowed") is not False:
        raise DerivedRootError("derived recipe must remain non-scientific")
    base = recipe.get("base", {})
    if base.get("teambench_commit") != TEAMBENCH_COMMIT:
        raise DerivedRootError("derived recipe base commit mismatch")
    source, generator_sha = _ensure_pinned_source()
    if base.get("generator_sha256") != generator_sha:
        raise DerivedRootError("derived recipe generator hash mismatch")
    overlay = recipe.get("overlay", {})
    if overlay.get("version") != OVERLAY_VERSION or overlay.get("sha256") != _recipe_overlay_hash():
        raise DerivedRootError("derived recipe overlay hash/version mismatch")
    if tuple(recipe.get("seeds", ())) != SEEDS:
        raise DerivedRootError("derived recipe seed order mismatch")
    return recipe


def load_derived_pipe2(seed: int, *, recipe_path: str | Path = RECIPE_PATH) -> Any:
    """Load one PIPE2 task with only the versioned CSV serialization overlay."""
    recipe = _load_recipe(Path(recipe_path))
    if seed not in SEEDS:
        raise DerivedRootError(f"seed {seed} is not in the candidate recipe")
    generated = _pinned_generated(seed)
    derived = derive_seed(seed, generated=generated)
    record = next(item for item in recipe["fixtures"] if item["seed"] == seed)
    for key in ("source_sha256", "expected_sha256", "schema_name", "columns", "key_columns"):
        if derived[key] != record[key]:
            raise DerivedRootError(f"derived seed {seed} record mismatch for {key}")
    updated = copy.deepcopy(generated)
    updated.workspace_files["data/source.csv"] = derived["source_bytes"]
    updated.workspace_files["data/expected_output.csv"] = derived["expected_bytes"]
    updated.metadata = dict(updated.metadata)
    updated.metadata["derived_root_candidate_id"] = CANDIDATE_ID
    updated.metadata["derived_root_digest"] = recipe["root_digest"]
    updated.metadata["derived_overlay_scope"] = recipe["overlay"]["scope"]
    return updated


def build_derived_materials(seed: int, *, recipe_path: str | Path = RECIPE_PATH) -> dict[str, Any]:
    """Delegate actor-payload construction to the pinned non-oracular adapter."""
    from peerrolebench_pipe2_material_adapter_v2 import build_materials
    return build_materials(load_derived_pipe2(seed, recipe_path=recipe_path))


__all__ = [
    "CANDIDATE_ID", "DerivedRootError", "RECIPE_PATH", "RECIPE_SCHEMA_VERSION",
    "SEEDS", "TEAMBENCH_COMMIT", "build_derived_materials", "build_recipe",
    "csv_text", "derive_seed", "load_derived_pipe2", "logical_rows", "sha256_bytes",
]
