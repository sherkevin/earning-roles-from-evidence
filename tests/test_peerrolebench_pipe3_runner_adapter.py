from __future__ import annotations

import copy
import sys

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    adoption_scorer_sources, attach_pipe3_delivery, prepare_pipe3_action,
    producer_scorer_sources, recipient_scorer_sources,
    validate_pipe3_action_result,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402


def materials():
    return build_materials(load_pipe3(0))


def delivery(m):
    return {"producer.py": m["agent_payloads"]["producer"]["source_files"]["producer.py"]}


def test_delivery_and_scorer_views_keep_pipe3_ownership_separate():
    m = materials(); d = delivery(m)
    attached = attach_pipe3_delivery(m["agent_payloads"]["recipient"], d)
    assert set(attached["source_files"]) == {"producer.py", "processor.py", "models.py", "sink.py"}
    assert set(producer_scorer_sources(m, d)) == {"producer.py", "models.py"}
    assert set(recipient_scorer_sources(attached["source_files"])) == {"processor.py", "models.py"}
    assert set(adoption_scorer_sources(attached["source_files"])) == {"producer.py", "processor.py", "models.py", "sink.py"}


def test_action_permissions_and_complete_snapshot_validation():
    m = materials(); d = delivery(m)
    for action, writable in (("use", {"processor.py"}),
                             ("repair", {"producer.py", "processor.py"}),
                             ("independent_redo", {"processor.py"})):
        payload = prepare_pipe3_action(m, d, action)
        assert set(payload["writable_paths"]) == writable
        validated = validate_pipe3_action_result(payload, payload["source_files"])
        assert validated["changed_paths"] == []

    payload = prepare_pipe3_action(m, d, "use")
    mutated = copy.deepcopy(payload["source_files"])
    mutated["producer.py"] += "\n# forbidden\n"
    try:
        validate_pipe3_action_result(payload, mutated)
    except ValueError as exc:
        assert "read-only" in str(exc)
    else:
        raise AssertionError("use action accepted a producer edit")
