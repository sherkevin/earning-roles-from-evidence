from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_fixture_manifest import (  # noqa: E402
    ManifestError,
    create_manifest,
    load_manifest,
    load_public_fixture,
    sha256_bytes,
)


COMMIT = "d185aef1916fd86a9ba554d581fd256319a973af"
POLICY = {
    "invalid_action": "reject_without_label",
    "unknown_action": "unknown_without_label",
    "emits_label": False,
}


def _write_bundle(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "public").mkdir()
    (tmp_path / "hidden").mkdir()
    (tmp_path / "public/0.source.csv").write_bytes(b"id,value\n0,public\n")
    (tmp_path / "hidden/0.expected.csv").write_bytes(b"id,value\n0,expected\n")
    (tmp_path / "public/1.source.csv").write_bytes(b"id,value\n1,public\n")
    (tmp_path / "hidden/1.expected.csv").write_bytes(b"id,value\n1,expected\n")
    manifest = create_manifest(
        tmp_path,
        authority_kind="derived",
        teambench_commit=COMMIT,
        generator_sha256="1" * 64,
        overlay_sha256="2" * 64,
        schema_name="toy",
        schema_columns=("id", "value"),
        key_columns=("id",),
        fixtures=(
            {"seed": 0, "split": "public", "source_path": "public/0.source.csv",
             "expected_path": "hidden/0.expected.csv"},
            {"seed": 1, "split": "hidden", "source_path": "public/1.source.csv",
             "expected_path": "hidden/1.expected.csv"},
        ),
        malformed_policy=POLICY,
    )
    path = tmp_path / "fixture_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def _rehashed(manifest: dict) -> dict:
    body = copy.deepcopy(manifest)
    body.pop("root_digest", None)
    body["root_digest"] = sha256_bytes(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    )
    return body


def test_manifest_records_authority_and_public_loader_hides_expected(tmp_path: Path):
    path = _write_bundle(tmp_path)
    manifest = load_manifest(path)
    assert manifest["authority_kind"] == "derived"
    assert manifest["teambench_commit"] == COMMIT
    assert manifest["generator_sha256"] == "1" * 64
    assert manifest["overlay_sha256"] == "2" * 64
    assert manifest["splits"] == {"public": [0], "hidden": [1]}
    assert manifest["benchmark_qualified"] is False
    assert manifest["malformed_policy"] == POLICY

    payload = load_public_fixture(path, 0)
    assert payload["source_bytes"] == b"id,value\n0,public\n"
    assert payload["schema_columns"] == ["id", "value"]
    assert "expected_bytes" not in payload
    assert "expected_path" not in payload
    assert "expected_sha256" not in payload
    with pytest.raises(ManifestError, match="public split"):
        load_public_fixture(path, 1)


@pytest.mark.parametrize(
    "mutator, message",
    [
        (lambda m: m["fixtures"].append(copy.deepcopy(m["fixtures"][0])), "duplicate fixture seed"),
        (lambda m: m["fixtures"][0].__setitem__("split", "sideways"), "unknown"),
        (lambda m: m.__setitem__("malformed_policy", {
            "invalid_action": "skip_silently", "unknown_action": "unknown_without_label",
            "emits_label": True,
        }), "rejected without a label"),
        (lambda m: m.__setitem__("benchmark_qualified", True), "benchmark-qualified"),
        (lambda m: m.__delitem__("overlay_sha256"), "missing required field"),
    ],
)
def test_manifest_fails_closed_on_shape_or_policy_mutation(tmp_path: Path, mutator, message: str):
    path = _write_bundle(tmp_path)
    manifest = json.loads(path.read_text())
    mutator(manifest)
    if "root_digest" in manifest:
        manifest = _rehashed(manifest)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ManifestError, match=message):
        load_manifest(path)


def test_manifest_fails_closed_on_source_and_expected_digest_mutations(tmp_path: Path):
    path = _write_bundle(tmp_path)
    (tmp_path / "public/0.source.csv").write_bytes(b"id,value\n0,tampered\n")
    with pytest.raises(ManifestError, match="source digest mismatch"):
        load_manifest(path)

    path = _write_bundle(tmp_path / "second")
    (tmp_path / "second/hidden/0.expected.csv").write_bytes(b"id,value\n0,tampered\n")
    with pytest.raises(ManifestError, match="expected digest mismatch"):
        load_manifest(path)


def test_manifest_rejects_unknown_split_and_cross_split_duplicate(tmp_path: Path):
    path = _write_bundle(tmp_path)
    manifest = json.loads(path.read_text())
    manifest["splits"]["hidden"].append(0)
    path.write_text(json.dumps(_rehashed(manifest)), encoding="utf-8")
    with pytest.raises(ManifestError, match="both public and hidden"):
        load_manifest(path)
