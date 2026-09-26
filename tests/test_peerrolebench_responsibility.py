"""Observed integration work must not be mislabeled as an upstream repair."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from peerrolebench_task_contract import (
    classify_consumer_changes, export_task_materials, load_generated_task,
    attach_selected_delivery, prepare_consumer_action,
)

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926"


@pytest.mark.parametrize("index", [0, 1])
def test_actual_repair_actions_only_changed_consumer(index):
    materials = json.loads((RUN / f"materials_{index}.json").read_text())
    output = json.loads((RUN / f"episode_{index}/sealed_consumer.json").read_text())
    result = classify_consumer_changes(materials, output)
    assert result["declared_repair_without_upstream_change"]
    assert result["producer_owned_paths_changed"] == []
    assert result["consumer_owned_paths_changed"] == ["mqueue/consumer.py"]
    assert not result["producer_correctness_measured"]
    assert not result["marginal_repair_cost_identified"]


def test_upstream_change_is_revision_not_causal_defect_proof():
    materials = json.loads((RUN / "materials_0.json").read_text())
    result = classify_consumer_changes(materials, {"changed_paths": ["mqueue/queue.py"], "consumer_action": "repair"})
    assert result["observed_upstream_revision"]
    assert not result["producer_defect_proven"]


def test_support_file_edit_cannot_be_attributed_to_either_agent():
    materials = json.loads((RUN / "materials_0.json").read_text())
    with pytest.raises(ValueError, match="outside"):
        classify_consumer_changes(materials, {"changed_paths": ["mqueue/config.py"], "consumer_action": "repair"})


@pytest.mark.parametrize("seed", [0, 1])
@pytest.mark.parametrize("action", ["use", "repair", "independent_redo"])
def test_ownership_survives_delivery_and_expanded_repair_permissions(seed, action):
    generated = load_generated_task("DIST1_queue_race", seed)
    materials = export_task_materials(generated)
    producer = materials["agent_payloads"]["producer"]
    recipient = materials["agent_payloads"]["recipient"]
    ownership = producer["responsibility_contract"]
    assert ownership == recipient["responsibility_contract"]
    assert ownership["producer_owned_paths"] == ["mqueue/queue.py", "mqueue/priority.py"]
    assert ownership["recipient_owned_paths"] == ["mqueue/consumer.py"]
    assert set(ownership["read_only_support_paths"]) == {"mqueue/config.py", "mqueue/__init__.py"}
    assert not set(ownership["producer_owned_paths"]) & set(ownership["recipient_owned_paths"])
    delivery = {path: generated.workspace_files[path] for path in producer["writable_paths"]}
    attached = attach_selected_delivery(recipient, delivery)
    payload = prepare_consumer_action(materials, delivery, action)
    assert attached["responsibility_contract"] == ownership
    assert payload["responsibility_contract"] == ownership
    if action != "use":
        assert "mqueue/queue.py" in payload["writable_paths"]
        assert "mqueue/queue.py" not in payload["responsibility_contract"]["recipient_owned_paths"]
    # The actor-facing copies must not modify the operator's original ownership.
    payload["responsibility_contract"]["producer_owned_paths"].clear()
    assert producer["responsibility_contract"]["producer_owned_paths"]
    assert recipient["responsibility_contract"]["producer_owned_paths"]
