"""Two real source generations with finite Qp checks; no judgments or learning.

Preparation freezes both sources and the unused target before any API request.
Each run-next command makes at most one generation request and never retries.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import traceback

from peerrolebench_actor_experience import ActorExperience, canonical_bytes, digest
from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_live_producer_stage import (
    RESERVATION_ROOT, finalize, model_config_digest, policy_digest, prepare_request,
    run_generation,
)
from peerrolebench_pipe3_public_contract_v2 import build_materials
from peerrolebench_pipe3_task_qualification import load_pipe3, verify_pin, TEAMBENCH
from peerrolebench_pipe3_producer_scorer_v2 import run_producer_scorer
from peerrolebench_pipe3_two_stage_composition import interfaces

ROOT = Path(__file__).resolve().parents[1]
VERSION = "n03-fresh-support-screen-v1"


def save(path, value):
    Path(path).write_bytes(canonical_bytes(value))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def event(out, kind, value):
    with (out / "raw.jsonl").open("a") as stream:
        stream.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "event_type": kind, "payload": value}) + "\n")


def prepare(card_path: Path, out: Path):
    card = json.loads(card_path.read_bytes())
    if (card["schema"] != VERSION or card["maximum_new_requests"] != 2
            or card["retries"] != 0 or card["real_api_runs_allowed"] is not True
            or card["source_assignments"] != [{"actor_id": "peer-b", "seed": 0},
                                               {"actor_id": "peer-c", "seed": 1}]
            or card["future_target_seed"] != 2
            or any(card[k] != 0 for k in ("judgment_calls", "recipient_action_calls",
                                          "target_calls", "training_updates", "gpu_calls"))):
        raise ValueError("not the two-source/no-target frozen scope")
    out.mkdir(parents=False, exist_ok=False)
    config = {"card": card, "card_sha256": sha(card_path),
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "hardware": platform.platform(),
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "command": sys.argv, "api_calls": 0, "gpu_calls": 0}
    save(out / "config.json", config)
    generator_pin = verify_pin()
    save(out / "generator_pin.json", generator_pin)
    if not generator_pin["passed"]:
        raise ValueError("native TeamBench checkout pin/cleanliness mismatch")
    files = [Path(__file__).resolve(), card_path.resolve()]
    # Snapshot project code, including transitively imported stage/runtime helpers.
    files += sorted((ROOT / "scripts").glob("peerrolebench_*.py"))
    files += [ROOT / "scripts/aamas_real_probe.py", ROOT / "references/aamas/peer_role_protocol_20260925.py"]
    files += [TEAMBENCH / "generators/gen_pipe3_stream_processing.py"]
    pins = {str(p.relative_to(ROOT)): sha(p) for p in dict.fromkeys(files)}
    for name in pins:
        target = out / "source_snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    save(out / "source_pins.json", pins)
    save(out / "materials.json", {str(seed): build_materials(load_pipe3(seed)) for seed in (0, 1, 2)})
    save(out / "freeze.json", {name: sha(out / name) for name in
                              ("config.json", "source_pins.json", "materials.json", "generator_pin.json")})
    save(out / "summary.json", {"status": "PREPARED", "attempted_episodes": 0,
                               "completed_sources": [], "scientific_claim_allowed": False})
    event(out, "prepared", {"sources": [0, 1], "unused_target": 2, "api_calls": 0})


def run_next(out: Path):
    for name, expected in json.loads((out / "freeze.json").read_bytes()).items():
        if sha(out / name) != expected:
            raise ValueError("frozen inputs changed: " + name)
    for name, expected in json.loads((out / "source_pins.json").read_bytes()).items():
        if sha(ROOT / name) != expected:
            raise ValueError("source changed after freeze: " + name)
    card = json.loads((out / "config.json").read_bytes())["card"]
    summary = json.loads((out / "summary.json").read_bytes())
    if summary["status"] not in ("PREPARED", "SOURCE_COMPLETED"):
        raise ValueError("screen is terminal; no repeat allowed")
    index = len(summary["completed_sources"])
    if index >= 2:
        raise ValueError("budget exhausted")
    attempted = out / f"attempt_{index}.json"
    with attempted.open("x") as stream:
        json.dump({"index": index, "timestamp_utc": datetime.now(timezone.utc).isoformat()}, stream)
    assignment = card["source_assignments"][index]
    producer_card = {key: card[key] for key in ("model", "temperature", "thinking", "stream",
                     "max_tokens", "request_timeout_seconds", "maximum_task_requests", "real_api_runs_allowed")}
    producer_card.update(stream_id=out.name, arm_id="source-screen", budget={
        "prior_attempted_episodes": card["prior_documented_episodes"], "additional_cap": 2,
        "attempted_ledger": [f"source-{j}" for j in range(index)]})
    candidate = CandidateRegistryEntry(assignment["actor_id"], "live-v2", policy_digest(),
                                       producer_card["model"], model_config_digest(producer_card))
    materials = json.loads((out / "materials.json").read_bytes())[str(assignment["seed"])]
    store = ActorExperience(stream_id=out.name, arm_id="source-screen", actor_id=candidate.key)
    row = {"index": index, "actor_key": candidate.key, "seed": assignment["seed"]}
    folder = out / f"source_{index}"
    folder.mkdir()
    try:
        prepared = prepare_request(base_payload=materials["agent_payloads"]["producer"],
            candidate=candidate, experience=store, task_index=0,
            interaction_id=f"source-{index}", card=producer_card)
        save(folder / "prepared.json", prepared)
        rid = f"{out.name}-source-{index}"
        reservation = {"status": "reserved", "reservation_id": rid,
            "card_digest": digest(producer_card), "prompt_sha256": prepared["prompt_sha256"],
            "candidate_key": candidate.key, "task_index": 0, "ordinal": index + 1}
        RESERVATION_ROOT.mkdir(parents=True, exist_ok=True)
        reservation_path = RESERVATION_ROOT / f"{rid}.json"
        with reservation_path.open("xb") as stream:
            stream.write(canonical_bytes(reservation))
        event(out, "generation_start", row)
        result = run_generation(prepared=prepared, card=producer_card,
            expected_card_digest=digest(producer_card), output_dir=folder / "generation",
            reservation_path=reservation_path, expected_reservation_digest=sha(reservation_path))
        save(folder / "generation_result.json", result)
        if result["status"] != "PARSED":
            raise RuntimeError("generation UNKNOWN: " + result.get("error", "unspecified"))
        completed = finalize(prepared=prepared, output_dir=folder / "generation",
            expected_receipt_digest=result["completion_receipt_sha256"], recipient_id="not-executed",
            interaction_id=f"source-{index}", delivery_id=f"source-{index}",
            source_event_id=f"source-request-{index}")
        save(folder / "completion.json", completed)
        qp = run_producer_scorer({**completed["source_files"], "models.py":
            materials["agent_payloads"]["producer"]["source_files"]["models.py"]},
            interfaces(materials), "PIPE3_stream_processing", assignment["seed"], folder / "producer_scorer",
            lambda kind, value: event(out, kind, value))
        save(folder / "producer_score.json", qp)
        row.update(status="COMPLETED", Qp=qp, generated_artifact_sha256=completed["delivery"]["artifact_sha256"],
                   actor_after_digest=completed["after"]["state_digest"])
        if qp["status"] == "UNKNOWN":
            raise RuntimeError("producer scoring UNKNOWN")
        summary["completed_sources"].append(row)
        summary["status"] = "SOURCE_COMPLETED"
        if index == 1:
            vectors = [[x["status"] for x in r["Qp"]["checks"]] for r in summary["completed_sources"]]
            summary["status"] = "STOPPED_NO_OBSERVED_CHECK_CONTRAST" if vectors[0] == vectors[1] else "STOPPED_TASK_ACTOR_CONTRAST"
            summary["check_vectors"] = vectors
    except Exception as exc:
        row.update(status="UNKNOWN", error_type=type(exc).__name__, error=str(exc))
        summary.update(status="STOPPED_UNKNOWN", failure=row)
        event(out, "error", {**row, "traceback": traceback.format_exc()})
    save(folder / "result.json", row)
    costs = [json.loads(p.read_bytes()) for p in out.glob("source_*/generation/episode/producer_cost.json")]
    starts = sum(json.loads(line).get("event_type") == "request_start"
        for raw in out.glob("source_*/generation/raw.jsonl") for line in raw.read_text().splitlines())
    summary.update(reserved_attempts=len(list(out.glob("attempt_*.json"))),
        attempted_episodes=starts, task_request_starts=starts,
        cumulative_documented_episodes=card["prior_documented_episodes"] + starts,
        cumulative_documented_task_requests=card["prior_documented_task_requests"] + starts,
        known_input_tokens=sum((c.get("usage") or {}).get("input_tokens", 0) for c in costs if c.get("usage_complete")),
        known_output_tokens=sum((c.get("usage") or {}).get("output_tokens", 0) for c in costs if c.get("usage_complete")),
        unknown_usage_requests=starts-sum(c.get("usage_complete") is True for c in costs),
        cost_receipts=costs, target_executed=False, judgments=0, actions=0, updates=0)
    save(out / "summary.json", summary)
    event(out, "step_completed", {"index": index, "status": summary["status"], "request_starts": starts})
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "run-next"))
    parser.add_argument("--card", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.card.resolve(), args.out.resolve())
    else:
        print(json.dumps(run_next(args.out.resolve()), ensure_ascii=False))
