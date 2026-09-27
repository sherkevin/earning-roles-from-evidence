from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_manifest_provenance import audit_root  # noqa: E402


MANIFEST = json.loads((ROOT / "configs/aamas2027/n03_benchmark_baseline_candidate_v1.json").read_text())


def test_dist1_neutral_adapter_removes_observed_spec_test_name_leak():
    result = audit_root(MANIFEST["roots"][0])
    assert result["all_static_visibility_passed"] is True
    assert result["seeds"][0]["hidden_path_leaks"] == []


def test_pipe3_audit_has_no_hidden_path_leak_for_candidate_materials():
    result = audit_root(MANIFEST["roots"][1])
    assert result["all_static_visibility_passed"] is True
    assert all(not row["hidden_path_leaks"] for row in result["seeds"])
