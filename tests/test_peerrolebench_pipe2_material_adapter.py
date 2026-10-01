from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_material_adapter import (  # noqa: E402
    DELIVERY_PATH, build_materials, load_pipe2, validate_extracted_rows, attach_extracted_rows,
)


def test_pipe2_materials_hide_native_oracle_and_split_etl_ownership():
    materials = build_materials(load_pipe2(0))
    manifest = materials["manifest"]
    assert manifest["scientific_task_text_qualified"] is True
    assert manifest["hidden_path_leaks"] == []
    assert manifest["producer_writable_paths"] == ["pipeline/extract.py"]
    assert manifest["recipient_writable_paths"] == [
        "pipeline/transform.py", "pipeline/load.py", "pipeline/run_pipeline.py"
    ]
    producer = materials["agent_payloads"]["producer"]
    recipient = materials["agent_payloads"]["recipient"]
    assert set(producer["source_files"]) == {
        "pipeline/extract.py", "pipeline/__init__.py", "PIPELINE_SPEC.md", "data/source.csv"
    }
    assert "data/expected_output.csv" not in str(producer)
    assert recipient["required_delivery_paths"] == [DELIVERY_PATH]


def test_pipe2_delivery_shape_is_separate_from_correctness_label():
    materials = build_materials(load_pipe2(1))
    columns = load_pipe2(1).expected["columns"]
    artifact = validate_extracted_rows([{column: "x" for column in columns}], columns=columns)
    assert artifact["correctness_label"] is None
    attached = attach_extracted_rows(materials["agent_payloads"]["recipient"], artifact)
    assert attached["required_delivery_paths"] == []
    assert DELIVERY_PATH in attached["source_files"]


def test_pipe2_delivery_rejects_wrong_columns():
    with pytest.raises(ValueError, match="columns"):
        validate_extracted_rows([{"wrong": "x"}], columns=("emp_id", "full_name"))
