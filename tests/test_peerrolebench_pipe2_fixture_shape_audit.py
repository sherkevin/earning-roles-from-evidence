from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_fixture_shape_audit import errors, run  # noqa: E402


def test_fixture_shape_audit_finds_unescaped_comma_field():
    assert errors("a,b\n1,hello,extra\n", ["a", "b"])[0]["unexpected_keys"] == [None]


def test_fixture_shape_audit_finds_missing_value():
    assert errors("a,b\n1\n", ["a", "b"])[0]["missing_values"] == ["b"]


def test_fixture_shape_audit_preserves_quoted_newline_and_duplicate_header():
    assert errors('a,b\n1,"line one\nline two"\n', ["a", "b"]) == []
    assert errors("a,a\n1,2\n", ["a", "a"])[0]["reason"] == "duplicate_header"


def test_fixture_shape_audit_rejects_header_only_and_wrong_order():
    assert errors("a,b\n", ["a", "b"])[0]["reason"] == "empty_data"
    assert errors("b,a\n1,2\n", ["a", "b"])[0]["reason"] == "header_mismatch"


def test_fixture_shape_audit_run_records_preconditions_and_case_hashes(tmp_path):
    summary = run(tmp_path / "audit", [0])
    assert summary["preconditions_passed"] is True
    assert summary["status"] == "AUDITED"
    assert summary["cases"][0]["workspace_sha256"]
    assert summary["cases"][0]["structural_root"].startswith("TeamBench@")
