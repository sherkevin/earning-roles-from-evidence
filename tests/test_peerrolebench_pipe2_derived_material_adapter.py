from __future__ import annotations

import copy
import csv
import io
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_derived_material_adapter import (  # noqa: E402
    DerivedRootError,
    RECIPE_PATH,
    SEEDS,
    build_derived_materials,
    load_derived_pipe2,
    sha256_bytes,
)


def _recipe_with_digest(recipe: dict) -> dict:
    body = copy.deepcopy(recipe)
    body.pop("root_digest", None)
    body["root_digest"] = sha256_bytes(
        json.dumps(body, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    )
    return body


def test_all_candidate_seeds_load_and_repair_only_serialization():
    changed = []
    for seed in SEEDS:
        generated = load_derived_pipe2(seed)
        columns = generated.expected["columns"]
        rows = list(csv.DictReader(io.StringIO(
            generated.workspace_files["data/source.csv"], newline="")))
        assert rows
        assert all(tuple(row) == tuple(columns) for row in rows)
        record = next(item for item in json.loads(RECIPE_PATH.read_text())["fixtures"]
                      if item["seed"] == seed)
        assert sha256_bytes(generated.workspace_files["data/source.csv"].encode()) == record["source_sha256"]
        assert sha256_bytes(generated.workspace_files["data/expected_output.csv"].encode()) == record["expected_sha256"]
        if record["source_changed"]:
            changed.append(seed)
    assert changed == [1, 4, 6, 9]


def test_public_payload_omits_expected_output_and_retains_contract():
    materials = build_derived_materials(1)
    for role in ("producer", "recipient"):
        payload = materials["agent_payloads"][role]
        assert "data/expected_output.csv" not in payload["source_files"]
        assert payload["task_id"] == "PIPE2_data_pipeline"
    assert materials["manifest"]["benchmark_qualified"] is False


def test_recipe_mutation_fails_closed_even_if_root_digest_is_recomputed(tmp_path: Path):
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    recipe["fixtures"][0]["source_sha256"] = "0" * 64
    path = tmp_path / "recipe.json"
    path.write_text(json.dumps(_recipe_with_digest(recipe)), encoding="utf-8")
    with pytest.raises(DerivedRootError, match="record mismatch"):
        load_derived_pipe2(0, recipe_path=path)


def test_recipe_overlay_hash_mutation_fails_closed(tmp_path: Path):
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    recipe["overlay"]["version"] = "other-overlay"
    path = tmp_path / "recipe.json"
    path.write_text(json.dumps(_recipe_with_digest(recipe)), encoding="utf-8")
    with pytest.raises(DerivedRootError, match="overlay hash/version"):
        load_derived_pipe2(0, recipe_path=path)


def test_recipe_seed_record_mutation_fails_closed_even_if_root_is_recomputed(tmp_path: Path):
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    recipe["fixtures"][0]["source_changed"] = True
    path = tmp_path / "recipe.json"
    path.write_text(json.dumps(_recipe_with_digest(recipe)), encoding="utf-8")
    with pytest.raises(DerivedRootError, match="record mismatch"):
        load_derived_pipe2(0, recipe_path=path)


def test_seed_outside_candidate_is_rejected():
    with pytest.raises(DerivedRootError, match="not in the candidate recipe"):
        load_derived_pipe2(10)
