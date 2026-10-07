from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_material_adapter import build_materials as build_v1  # noqa: E402
from peerrolebench_pipe3_public_contract_v2 import CLAUSES, TRACE, build_materials  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402


def test_v2_changes_only_task_text_and_payload_digest():
    generated = load_pipe3(0)
    old = build_v1(generated)
    new = build_materials(generated)
    assert new["manifest"]["payload_sha256"] != old["manifest"]["payload_sha256"]
    for role in ("producer", "recipient"):
        before = old["agent_payloads"][role]
        after = new["agent_payloads"][role]
        assert before["source_files"] == after["source_files"]
        assert before["writable_paths"] == after["writable_paths"]
        assert before["required_delivery_paths"] == after["required_delivery_paths"]
        assert {key: value for key, value in before.items() if key != "task_text"} == {
            key: value for key, value in after.items()
            if key not in {"task_text", "contract_clause_refs"}
        }
        assert before["task_text"] != after["task_text"]
        assert after["contract_clause_refs"] == list(CLAUSES)


def test_v2_public_contract_covers_private_behavior_without_hidden_material():
    for seed, categorical_field in ((0, "action"), (1, "metric_type"), (2, "txn_type")):
        materials = build_materials(load_pipe3(seed))
        payloads = materials["agent_payloads"]
        for payload in payloads.values():
            spec = payload["task_text"]["spec_md"]
            for clause_id, clause in CLAUSES.items():
                assert f"**{clause_id}**: {clause}" in spec
            assert payload["contract_clause_refs"] == list(CLAUSES)
            assert categorical_field in payload["source_files"]["models.py"]
        task_text = json.dumps(payloads["producer"]["task_text"], ensure_ascii=False).lower()
        actor_text = json.dumps(payloads, ensure_ascii=False).lower()
        assert "isoformat" not in task_text
        assert "bug 1" not in task_text and "bug 2" not in task_text
        assert "tests/test_" not in actor_text
        assert "expected_projection" not in actor_text
        assert "terminal-001" not in actor_text
        assert "müller" not in task_text and "renée" not in task_text
        assert "public_contract_trace_parent_only" not in actor_text
        assert materials["manifest"]["public_contract_trace_parent_only"] == TRACE
        assert "limited scorer check coverage" in materials["manifest"]["public_contract_trace_scope"]
        assert materials["manifest"]["scientific_task_text_qualified"] is False
