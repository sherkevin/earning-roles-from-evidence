from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


QUAL = _load("pipe3_qualification_for_adapter", ROOT / "scripts/peerrolebench_pipe3_task_qualification.py")
ADAPTER = _load("pipe3_material_adapter", ROOT / "scripts/peerrolebench_pipe3_material_adapter.py")


def test_redacted_pipe3_material_is_parseable_and_non_oracular():
    for seed in (0, 1, 2):
        materials = ADAPTER.build_materials(QUAL.load_pipe3(seed))
        manifest = materials["manifest"]
        assert manifest["scientific_task_text_qualified"] is True
        assert manifest["task_text_oracle_patterns"] == []
        assert manifest["source_comment_oracle_patterns"] == []
        assert manifest["hidden_path_leaks"] == []
        assert manifest["expected_bug_ids_not_in_payload"] is True
        assert manifest["expected_metadata_in_payload"] is False
        assert manifest["runtime_dispatch_verified"] is False
        assert set(materials["agent_payloads"]) == {"producer", "recipient"}


def test_redacted_material_preserves_role_boundary():
    materials = ADAPTER.build_materials(QUAL.load_pipe3(0))
    producer = materials["agent_payloads"]["producer"]
    recipient = materials["agent_payloads"]["recipient"]
    assert producer["writable_paths"] == ["producer.py"]
    assert recipient["writable_paths"] == ["processor.py"]
    assert set(producer["source_files"]) == {"producer.py", "models.py", "sink.py"}
    assert set(recipient["source_files"]) == {"processor.py", "models.py", "sink.py"}
    assert "tests/test_pipeline.py" not in str(materials["agent_payloads"])
