"""Regression checks using frozen real C1 artifact lineage; no API replay."""
import json
from copy import deepcopy
from pathlib import Path

import pytest
from scripts.peerrolebench_independent_y_contract_v2 import bind_episode

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "experiments/logs/n03_c1_parent_source_live_20261006_v1"


def load_arm(arm):
    summary = json.loads((DATA / arm / "summary.json").read_text())
    ep = summary.get("target", summary["source"])
    request = json.loads((DATA / arm / f"decision_{ep['decision_index']}" /
                          "action/action_request.json").read_text())
    payload = json.loads(request["messages"][0]["content"].split("ACTION PAYLOAD:\n", 1)[1])
    return summary["ledger"], ep, payload


@pytest.mark.parametrize("arm,assigned", [("parent_source", False), ("no_update", False),
                                          ("contextual_trust_linear", True), ("RARE", True)])
def test_real_lineage_binds_both_assigned_and_unassigned(arm, assigned):
    ledger, ep, payload = load_arm(arm)
    binding = bind_episode(ledger, ep["delivery_id"], payload, ep["final_sources"])
    assert binding["assignment_bound"] is assigned
    assert binding["delivery_artifact_sha256"] != binding["action_input_sha256"]
    assert binding["action_input_sha256"] == binding["target_snapshot_sha256"]
    assert binding["target_snapshot_sha256"] == ep["action"]["output_source_sha256"]


def test_recomputed_ledger_hash_and_snapshot_mutations_rejected():
    ledger, ep, payload = load_arm("RARE")
    corrupt = deepcopy(ledger)
    corrupt[0]["record_hash"] = "f" * 64
    with pytest.raises(ValueError):
        bind_episode(corrupt, ep["delivery_id"], payload, ep["final_sources"])
    swapped = dict(ep["final_sources"])
    swapped["producer.py"] += "\n# altered\n"
    with pytest.raises(ValueError):
        bind_episode(ledger, ep["delivery_id"], payload, swapped)


def test_full_action_input_digest_cannot_be_replaced_by_delivery_digest():
    ledger, ep, payload = load_arm("no_update")
    payload["input_source_sha256"] = ep["artifact_digest"]
    with pytest.raises(ValueError):
        bind_episode(ledger, ep["delivery_id"], payload, ep["final_sources"])
