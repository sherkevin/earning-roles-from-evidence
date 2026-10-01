from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_runtime_qualification import (  # noqa: E402
    csv_shape_errors, expected_transform, fix_producer, fix_recipient,
)
from peerrolebench_pipe2_material_adapter import build_materials, load_pipe2  # noqa: E402


def test_csv_shape_gate_rejects_unescaped_extra_field():
    text = "a,b\n1,hello,unexpected\n"
    errors = csv_shape_errors(text, ["a", "b"])
    assert errors and errors[0]["unexpected_keys"] == [None]


def test_parent_contract_transform_is_independent_and_bounded():
    rows = [{"id": "  x ", "note": "z" * 300}]
    assert expected_transform(rows, ["id", "note"]) == [{"id": "x", "note": "z" * 255}]


def test_control_replacements_touch_only_declared_defects():
    materials = build_materials(load_pipe2(0))
    producer = materials["agent_payloads"]["producer"]["source_files"]["pipeline/extract.py"]
    assert "KEY_COLUMNS" in fix_producer(producer)
    recipient = {path: materials["agent_payloads"]["recipient"]["source_files"][path]
                 for path in ("pipeline/__init__.py", "pipeline/transform.py", "pipeline/load.py")}
    fixed = fix_recipient(recipient)
    assert "TRUNCATION_LIMIT = 255" in fixed["pipeline/transform.py"]
    assert "OUTPUT_COLUMNS = COLUMNS" in fixed["pipeline/load.py"]
