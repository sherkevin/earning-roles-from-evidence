from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_validate_manifest import validate  # noqa: E402


MANIFEST = ROOT / "configs/aamas2027/n03_benchmark_baseline_candidate_v1.json"
MANIFEST_V2 = ROOT / "configs/aamas2027/n03_benchmark_baseline_candidate_v2.json"


def test_candidate_manifest_has_two_roots_and_shared_information_contract():
    result = validate(json.loads(MANIFEST.read_text()))
    assert result == {"valid": True, "errors": [], "root_count": 2, "baseline_count": 7}


def test_candidate_manifest_rejects_baseline_or_split_drift():
    manifest = json.loads(MANIFEST.read_text())
    manifest["baselines"] = ["uniform"]
    manifest["roots"][1]["split"] = "development"
    result = validate(manifest)
    assert result["valid"] is False
    assert "baseline_matrix_incomplete" in result["errors"]
    assert "development_confirmation_split" in result["errors"]


def test_candidate_manifest_v2_is_accepted_without_freezing_science():
    result = validate(json.loads(MANIFEST_V2.read_text()))
    assert result == {"valid": True, "errors": [], "root_count": 2, "baseline_count": 7}
