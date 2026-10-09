"""Zero-call PIPE2 observation/credit separation and parity qualification.

This is a software gate for ADR0049 (Scheme B), not a benchmark result.  It
keeps a recipient's judgment as a typed noisy observation, then binds a later
assignment, target selection, and independent target outcome without allowing
the observation to masquerade as producer credit.  The three parity arms use
the same menu, public feature digest, read cut, arrival order, propensity and
cost scope; only the history payload changes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/aamas2027/n03_pipe2_observation_lineage_parity_20261008.json"
SCHEMA = "pipe2-observation-lineage-parity-v1"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def artifact(seed: int, suffix: str) -> str:
    return hashlib.sha256(f"PIPE2:{seed}:{suffix}".encode()).hexdigest()


def _event(event_type: str, payload: Mapping[str, Any], previous: str) -> dict[str, Any]:
    body = {"schema": SCHEMA, "event_type": event_type, "previous_hash": previous, **payload}
    body["record_hash"] = digest(body)
    return body


def _append(events: list[dict[str, Any]], event_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    previous = events[-1]["record_hash"] if events else "GENESIS"
    row = _event(event_type, payload, previous)
    events.append(row)
    return row


def build_fixture(seed: int = 0) -> dict[str, Any]:
    """Build one authored source->future chain and its public projections."""
    menu = ["producer-a@v1", "producer-b@v1"]
    menu_digest = digest(menu)
    feature_digest = digest({"schema": "matrix-features-v1", "task": "PIPE2_data_pipeline",
                             "menu": menu, "context": "csv-transform"})
    arrival_digest = digest({"source_observation": 3, "target_outcome": 8})
    cost_scope = {"unit": "wall_ms", "scope": "selector+source_observation+target_route",
                  "complete": False}
    source_artifact = artifact(seed, "source-artifact")
    target_artifact = artifact(seed, "target-artifact")
    events: list[dict[str, Any]] = []
    source_selection = _append(events, "source_selection", {
        "selection_id": "pipe2-source-selection-0", "task_id": "PIPE2_data_pipeline",
        "task_index": 0, "candidate_menu": menu, "chosen": "producer-a@v1",
        "propensity": 0.5, "menu_digest": menu_digest, "feature_digest": feature_digest,
        "read_cut": 0,
    })
    source_delivery = _append(events, "source_delivery", {
        "delivery_id": "pipe2-source-delivery-0", "selection_id": source_selection["selection_id"],
        "producer": "producer-a@v1", "recipient": "recipient-0", "artifact_sha256": source_artifact,
        "task_index": 0,
    })
    # The judgment is sealed before action; it is deliberately rework to prove
    # that noisy negative observations are retained rather than filtered.
    source_judgment = _append(events, "source_judgment", {
        "judgment_id": "pipe2-source-judgment-0", "delivery_id": source_delivery["delivery_id"],
        "evaluator": "recipient-0", "decision": "accept_with_rework",
        "observed_artifact_sha256": source_artifact, "sealed_before_action": True,
    })
    source_action = _append(events, "source_action", {
        "action_id": "pipe2-source-action-0", "delivery_id": source_delivery["delivery_id"],
        "action": "repair", "used_artifact": True,
        "recipient_changed_paths": ["pipeline/transform.py"],
        "input_artifact_sha256": source_artifact,
        "output_artifact_sha256": artifact(seed, "recipient-output"),
    })
    source_outcome = _append(events, "source_outcome", {
        "outcome_id": "pipe2-source-outcome-0", "delivery_id": source_delivery["delivery_id"],
        "status": "PASS", "scorer": "recipient-contract-v1", "independent": True,
    })
    observation_payload = {
        "observation_id": "pipe2-observation-0", "source_delivery_id": source_delivery["delivery_id"],
        "source_selection_id": source_selection["selection_id"],
        "source_judgment_id": source_judgment["judgment_id"],
        "source_action_id": source_action["action_id"],
        "source_outcome_id": source_outcome["outcome_id"],
        "candidate_key": "producer-a@v1", "role": "producer",
        "judgment": "accept_with_rework", "action": "repair", "arrival_index": 3,
        "read_cut": 3, "artifact_sha256": source_artifact,
        "observation_kind": "noisy_recipient_judgment", "credit_eligible": False,
    }
    observation = _append(events, "noisy_observation", observation_payload)
    assignment = _append(events, "future_assignment", {
        "assignment_id": "pipe2-assignment-1", "task_id": "PIPE2_data_pipeline",
        "task_index": 1, "agent": "producer-a@v1", "role": "producer",
        "source_observation_id": observation["observation_id"], "read_cut": 4,
        "candidate_menu": menu, "menu_digest": menu_digest,
        "feature_digest": feature_digest, "arrival_digest": arrival_digest,
        "propensity": 0.7, "cost_scope": cost_scope,
        "policy_update_applied": False,
    })
    target_selection = _append(events, "target_selection", {
        "selection_id": "pipe2-target-selection-1", "assignment_id": assignment["assignment_id"],
        "task_index": 1, "candidate_menu": menu, "chosen": "producer-a@v1",
        "propensity": 0.7, "menu_digest": menu_digest, "feature_digest": feature_digest,
        "read_cut": 4,
    })
    target_outcome = _append(events, "target_outcome", {
        "outcome_id": "pipe2-target-outcome-1", "selection_id": target_selection["selection_id"],
        "assignment_id": assignment["assignment_id"], "task_index": 1,
        "delivery_id": "pipe2-target-delivery-1", "artifact_sha256": target_artifact,
        "status": "PASS", "scorer": "independent-target-v1", "arrival_index": 8,
        "independent": True, "credit_computed": False,
    })
    public_observation = {key: observation[key] for key in (
        "observation_id", "source_delivery_id", "source_judgment_id", "candidate_key", "role",
        "judgment", "action", "arrival_index", "read_cut", "artifact_sha256", "observation_kind",
    )}
    # Quality labels, hidden expected-output digests and ownership checks never
    # enter the public selector projection.
    assert "credit_eligible" not in public_observation
    assert "recipient_changed_paths" not in public_observation
    return {
        "schema": SCHEMA, "seed": seed, "events": events,
        "source_observation": observation, "public_observation": public_observation,
        "future_assignment": assignment, "target_selection": target_selection,
        "target_outcome": target_outcome,
        "parity_contract": {
            "candidate_menu": menu, "menu_digest": menu_digest,
            "feature_digest": feature_digest, "arrival_digest": arrival_digest,
            "read_cut": assignment["read_cut"], "propensity": assignment["propensity"],
            "cost_scope": cost_scope,
        },
        "credit": {"observation_is_credit": False, "policy_update_allowed": False,
                    "independent_target_outcome_present": True},
    }


def _parity_arms(fixture: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    contract = fixture["parity_contract"]
    observation = fixture["public_observation"]
    return {
        "observation": {"history_payload": observation, **copy.deepcopy(contract)},
        "count_only": {"history_payload": {"candidate_key": observation["candidate_key"],
                                              "count": 1}, **copy.deepcopy(contract)},
        "j_masked": {"history_payload": {"candidate_key": observation["candidate_key"],
                                           "judgment": "MASKED"}, **copy.deepcopy(contract)},
    }


def validate_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    events = list(fixture["events"])
    failures: list[str] = []
    hashes = [row["record_hash"] for row in events]
    for index, row in enumerate(events):
        expected_previous = "GENESIS" if index == 0 else hashes[index - 1]
        if row["previous_hash"] != expected_previous or row["record_hash"] != digest({k: v for k, v in row.items() if k != "record_hash"}):
            failures.append("event_hash_chain")
    names = [row["event_type"] for row in events]
    required = ["source_selection", "source_delivery", "source_judgment", "source_action",
                "source_outcome", "noisy_observation", "future_assignment", "target_selection",
                "target_outcome"]
    if names != required:
        failures.append("event_order")
    if not fixture["source_observation"]["credit_eligible"]:
        pass
    else:
        failures.append("observation_must_not_be_credit")
    if fixture["target_outcome"]["arrival_index"] <= fixture["future_assignment"]["read_cut"]:
        failures.append("target_outcome_before_read_cut")
    assignment = fixture["future_assignment"]
    target_selection = fixture["target_selection"]
    observation = fixture["source_observation"]
    if assignment["source_observation_id"] != observation["observation_id"]:
        failures.append("assignment_observation_binding")
    if int(observation["arrival_index"]) > int(assignment["read_cut"]):
        failures.append("observation_after_assignment_read_cut")
    if target_selection["assignment_id"] != assignment["assignment_id"]:
        failures.append("target_selection_assignment_binding")
    if target_selection["menu_digest"] != assignment["menu_digest"]:
        failures.append("target_selection_menu_binding")
    if fixture["target_outcome"]["selection_id"] != target_selection["selection_id"]:
        failures.append("target_outcome_selection_binding")
    if observation.get("recipient_changed_paths") and observation.get("credit_eligible"):
        failures.append("recipient_edit_as_producer_credit")
    arms = _parity_arms(fixture)
    contract_keys = ("menu_digest", "feature_digest", "arrival_digest", "read_cut", "propensity", "cost_scope")
    for key in contract_keys:
        if len({json.dumps(arm[key], sort_keys=True) for arm in arms.values()}) != 1:
            failures.append(f"parity:{key}")
    return {"status": "QUALIFIED_OFFLINE" if not failures else "FAILED",
            "failures": failures, "event_count": len(events),
            "event_types": names, "parity_arms": list(arms),
            "policy_update_allowed": False, "scientific_claim_allowed": False}


def _mutate(fixture: Mapping[str, Any], name: str) -> dict[str, Any]:
    candidate = copy.deepcopy(fixture)
    events = candidate["events"]
    if name == "judgment_after_action":
        events[2], events[3] = events[3], events[2]
    elif name == "assignment_before_observation":
        events[5], events[6] = events[6], events[5]
    elif name == "menu_mismatch":
        candidate["target_selection"]["menu_digest"] = digest(["producer-a@v1", "producer-c@v1"])
    elif name == "late_observation_read_cut":
        candidate["future_assignment"]["read_cut"] = 2
    elif name == "target_outcome_before_selection":
        events[7], events[8] = events[8], events[7]
    elif name == "recipient_edit_as_producer_credit":
        candidate["source_observation"]["recipient_changed_paths"] = ["pipeline/transform.py"]
        candidate["source_observation"]["credit_eligible"] = True
    else:
        raise ValueError(f"unknown mutation: {name}")
    return candidate


def mutation_results(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    names = [
        "judgment_after_action", "assignment_before_observation", "menu_mismatch",
        "late_observation_read_cut", "target_outcome_before_selection",
        "recipient_edit_as_producer_credit",
    ]
    rows: list[dict[str, Any]] = []
    for name in names:
        mutated = _mutate(fixture, name)
        validation = validate_fixture(mutated)
        rejected = validation["status"] == "FAILED"
        rows.append({"mutation": name, "accepted": not rejected,
                     "failures": validation["failures"], "runner_started": False,
                     "policy_update": False})
    return rows


def run(output: Path, config_path: Path = CONFIG) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    (output / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture = build_fixture(0)
    result = validate_fixture(fixture)
    result["mutations"] = mutation_results(fixture)
    result["config_sha256"] = digest(config)
    result["source_code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with (output / "events.jsonl").open("w", encoding="utf-8") as stream:
        for row in fixture["events"]:
            stream.write(json.dumps({"event": row}, ensure_ascii=False, sort_keys=True) + "\n")
        stream.write(json.dumps({"validation": result}, ensure_ascii=False, sort_keys=True) + "\n")
    (output / "fixture.json").write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
