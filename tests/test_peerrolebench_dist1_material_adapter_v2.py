from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_dist1_material_adapter_v2 import build_materials  # noqa: E402
from peerrolebench_task_contract import load_generated_task  # noqa: E402


def test_dist1_v2_exposes_the_contract_used_by_the_diagnostic_scorer():
    materials = build_materials(load_generated_task("DIST1_queue_race", 0))
    manifest = materials["manifest"]
    spec = materials["agent_payloads"]["producer"]["task_text"]["spec_md"]

    assert manifest["schema_version"] == "peerrolebench-dist1-materials-v2"
    assert manifest["public_interface_contract_version"] == "dist1-queue-interface-v1"
    assert "exactly `(message, receipt)`" in spec
    assert "returns `None` when empty" in spec
    assert "TaskQueue.ack(receipt)" in spec
    assert "TaskQueue.nack(receipt)" in spec
    assert manifest["scientific_task_text_qualified"] is True
    assert manifest["hidden_path_leaks"] == []


def test_dist1_v2_does_not_expose_hidden_tests_or_native_oracle_text():
    materials = build_materials(load_generated_task("DIST1_queue_race", 0))
    payload_blob = repr(materials["agent_payloads"]).lower()
    assert "test_capacity.py" not in payload_blob
    assert "planner" not in payload_blob
    assert "bug 1" not in payload_blob
    assert set(materials["agent_payloads"]["recipient"]["required_delivery_paths"]) == {
        "mqueue/queue.py", "mqueue/priority.py"
    }
