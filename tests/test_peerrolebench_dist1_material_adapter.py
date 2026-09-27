from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_dist1_material_adapter import build_materials  # noqa: E402
from peerrolebench_task_contract import load_generated_task  # noqa: E402
from peerrolebench_pipe3_material_adapter import strip_comments_and_docstrings  # noqa: E402


def test_dist1_neutral_material_removes_native_oracle_names_and_keeps_contract():
    materials = build_materials(load_generated_task("DIST1_queue_race", 0))
    manifest = materials["manifest"]
    assert manifest["scientific_task_text_qualified"] is True
    assert manifest["hidden_path_leaks"] == []
    assert set(materials["agent_payloads"]["producer"]["writable_paths"]) == {
        "mqueue/queue.py", "mqueue/priority.py"
    }
    assert materials["agent_payloads"]["recipient"]["required_delivery_paths"] == [
        "mqueue/queue.py", "mqueue/priority.py"
    ]


def test_comment_stripping_keeps_docstring_only_suite_valid():
    source = 'class Marker:\n    """description"""\n'
    cleaned = strip_comments_and_docstrings(source)
    compile(cleaned, "marker.py", "exec")
    assert "pass" in cleaned
