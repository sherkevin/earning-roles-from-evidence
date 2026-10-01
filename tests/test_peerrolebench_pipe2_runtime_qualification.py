from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_runtime_qualification import (  # noqa: E402
    csv_shape_errors, expected_extraction, expected_transform, fix_producer,
    fix_recipient, public_extract_contract, public_col_types,
)
from peerrolebench_pipe2_material_adapter_v2 import (  # noqa: E402
    build_materials, load_pipe2, validate_extracted_rows,
)


def test_csv_shape_gate_rejects_unescaped_extra_field():
    text = "a,b\n1,hello,unexpected\n"
    errors = csv_shape_errors(text, ["a", "b"])
    assert errors and errors[0]["unexpected_keys"] == [None]


def test_csv_shape_gate_rejects_missing_field_value():
    text = "a,b\n1\n"
    assert csv_shape_errors(text, ["a", "b"])[0]["missing_values"] == ["b"]


def test_csv_shape_gate_preserves_quoted_newline_and_rejects_duplicate_header():
    text = 'a,b\n1,"line one\nline two"\n'
    assert csv_shape_errors(text, ["a", "b"]) == []
    duplicate = "a,a\n1,2\n"
    assert csv_shape_errors(duplicate, ["a", "a"])[0]["reason"] == "duplicate_header"


def test_parent_contract_transform_is_independent_and_bounded():
    rows = [{"id": "  x ", "note": "z" * 300}]
    assert expected_transform(rows, ["id", "note"]) == [{"id": "x", "note": "z" * 255}]
    typed = expected_transform([{"id": "  7  ", "note": "  text  "}],
                               ["id", "note"], col_types=["int", "str"])
    assert typed == [{"id": "  7  ", "note": "text"}]


def test_parent_contract_comes_from_public_module_constants():
    materials = build_materials(load_pipe2(0))
    producer = materials["agent_payloads"]["producer"]["source_files"]["pipeline/extract.py"]
    transform = materials["agent_payloads"]["recipient"]["source_files"]["pipeline/transform.py"]
    columns, keys = public_extract_contract(producer)
    assert columns[:2] == keys
    assert len(public_col_types(transform)) == len(columns)
    source = materials["agent_payloads"]["producer"]["source_files"]["data/source.csv"]
    assert len(expected_extraction(source, keys)) == 6


def test_control_replacements_touch_only_declared_defects():
    materials = build_materials(load_pipe2(0))
    producer = materials["agent_payloads"]["producer"]["source_files"]["pipeline/extract.py"]
    assert "KEY_COLUMNS" in fix_producer(producer)
    recipient = {path: materials["agent_payloads"]["recipient"]["source_files"][path]
                 for path in ("pipeline/__init__.py", "pipeline/transform.py", "pipeline/load.py")}
    fixed = fix_recipient(recipient)
    assert "TRUNCATION_LIMIT = 255" in fixed["pipeline/transform.py"]
    assert "OUTPUT_COLUMNS = COLUMNS" in fixed["pipeline/load.py"]


def test_control_replacement_is_generic_for_all_schema_families():
    for seed in (3, 4):
        materials = build_materials(load_pipe2(seed))
        recipient = {path: materials["agent_payloads"]["recipient"]["source_files"][path]
                     for path in ("pipeline/__init__.py", "pipeline/transform.py", "pipeline/load.py")}
        assert "OUTPUT_COLUMNS = COLUMNS" in fix_recipient(recipient)["pipeline/load.py"]


def test_v2_recipient_payload_excludes_source_and_orchestrator():
    materials = build_materials(load_pipe2(0))
    recipient = materials["agent_payloads"]["recipient"]
    assert recipient["writable_paths"] == ["pipeline/transform.py", "pipeline/load.py"]
    assert "data/source.csv" not in recipient["source_files"]
    assert "pipeline/run_pipeline.py" not in recipient["source_files"]
    manifest = materials["manifest"]
    assert manifest["schema_version"] == "peerrolebench-pipe2-materials-v2"
    assert manifest["orchestrator_read_only_paths"] == ["pipeline/run_pipeline.py"]


def test_v2_artifact_digest_binds_schema_and_rows():
    first = validate_extracted_rows([{"a": "1", "b": "x"}], columns=["a", "b"])
    second = validate_extracted_rows([{"b": "x", "a": "1"}], columns=["b", "a"])
    assert first["artifact_sha256"] != second["artifact_sha256"]
