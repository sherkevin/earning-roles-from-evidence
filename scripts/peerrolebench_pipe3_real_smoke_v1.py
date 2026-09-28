"""Run one bounded real-API PIPE3 integration episode.

This is an integration smoke after the zero-call dispatch gates.  It uses the
existing named ``内部`` provider, preserves raw SSE/cost logs, and stops on any
UNKNOWN scorer or malformed stage.  It never updates a role policy and cannot
support an efficacy claim.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

import peerrolebench_real_closed_loop as legacy_api  # noqa: E402
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, ProducerScore,
    RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_producer_scorer import run_producer_scorer as run_producer_scorer_v1  # noqa: E402
from peerrolebench_pipe3_producer_scorer_v2 import run_producer_scorer as run_producer_scorer_v2  # noqa: E402
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_recipient_scorer import run_scorer as run_recipient_scorer_v1  # noqa: E402
from peerrolebench_pipe3_recipient_scorer_v2 import run_scorer as run_recipient_scorer_v2  # noqa: E402
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    attach_pipe3_delivery, prepare_pipe3_action, validate_pipe3_action_result,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402


CARD_DEFAULT = ROOT / "configs/aamas2027/n03_pipe3_real_smoke_v1.json"


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_event(ledger: PeerRoleLedger, event: object) -> dict:
    methods = {
        PeerSelection: "record_selection", Delivery: "record_delivery", ProducerScore: "record_producer_score",
        RecipientJudgment: "record_judgment", ConsumerAction: "record_action",
        TerminalOutcome: "record_outcome", RoleEvidenceUpdate: "record_evidence_update",
    }
    for cls, method in methods.items():
        if isinstance(event, cls):
            getattr(ledger, method)(event)
            return ledger.events[-1]
    raise TypeError(type(event).__name__)


def run_qp(card: dict, sources: dict, info: dict, task_id: str, seed: int, evidence_dir: Path, log):
    version = card.get("producer_scorer", {}).get("version")
    if version == "pipe3-producer-objective-v1":
        scorer = run_producer_scorer_v1
    elif version == "pipe3-producer-objective-v2":
        scorer = run_producer_scorer_v2
    else:
        raise ValueError(f"unsupported producer scorer version: {version}")
    return scorer(sources, info, task_id, seed, evidence_dir, log)


def run_qr(card: dict, sources: dict, info: dict, mode: str, task_id: str, seed: int,
           evidence_dir: Path, log):
    version = (card.get("recipient_scorer", {}).get("version")
               if mode == "recipient" else card.get("adoption_scorer", {}).get("version"))
    if version == "pipe3-recipient-objective-v1":
        scorer = run_recipient_scorer_v1
    elif version == "pipe3-recipient-objective-v2":
        scorer = run_recipient_scorer_v2
    else:
        raise ValueError(f"unsupported {mode} scorer version: {version}")
    return scorer(sources, info, mode, task_id, seed, evidence_dir, log)


def run(out_dir: Path, card_path: Path) -> dict:
    out_dir.mkdir(parents=False, exist_ok=False)
    raw = out_dir / "raw.jsonl"

    def log(event_type: str, payload: object) -> None:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()

    card = json.loads(card_path.read_text(encoding="utf-8"))
    teambench = ROOT / "references/benchmark_sources/TeamBench"
    actual_pin = subprocess.check_output(["git", "-C", str(teambench), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(teambench), "status", "--porcelain"], text=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    config = {
        "experiment_id": out_dir.name,
        "card_path": str(card_path.relative_to(ROOT)),
        "card_sha256": sha_bytes(card_path.read_bytes()),
        "task_id": card["task_id"], "task_seed": card["task_seed"],
        "teambench_expected_pin": card["source_commit"], "teambench_actual_pin": actual_pin,
        "teambench_clean": not dirty, "earning_roles_git_commit": commit,
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "platform": platform.platform()},
        "provider": card["provider"], "model": card["model"],
        "request_budget": card["maximum_task_requests"], "maximum_episode_attempts": card["maximum_episode_attempts"],
        "real_api_calls": 0, "gpu_jobs": 0, "role_policy_update": False,
        "scientific_claim_allowed": False,
    }
    # This file is written before the first API request.
    save(out_dir / "config.json", config)
    log("config", config)

    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    status = "UNKNOWN"
    result: dict = {"status": status, "reason": None}
    try:
        generated = load_pipe3(int(card["task_seed"]))
        materials = build_materials(generated)
        save(out_dir / "material_manifest.json", materials["manifest"])
        save(out_dir / "public_materials.json", materials["agent_payloads"])
        info = interfaces(materials)
        selection = PeerSelection("selection-0", card["task_id"], 0, "peer-a", "producer",
                                  ("peer-b", "peer-c"), "peer-b", 0.5)
        append_event(ledger, selection)
        ledger.record_task_start(card["task_id"], 0)
        save(out_dir / "ledger.json", ledger.events)

        episode = out_dir / "episode_0"
        episode.mkdir()
        common = ("You are a participant in a bounded public Python collaboration task. "
                  "Do not inspect tests, hidden evaluator files, or external files. "
                  "Return one JSON object and no markdown. ")
        producer_prompt = common + (
            "You are the producer. Repair only producer.py, preserve its public names and signatures, "
            "and return {\"source_files\":{\"producer.py\":\"complete file text\"}}. "
            "Public task payload:\n" + json.dumps(materials["agent_payloads"]["producer"], ensure_ascii=False))
        produced, producer_meta = legacy_api.call_api(out_dir, episode, "producer", producer_prompt, card)
        config["real_api_calls"] += 1
        save(episode / "producer_parsed.json", produced)
        delivery_files = produced.get("source_files")
        if not isinstance(delivery_files, dict) or set(delivery_files) != {"producer.py"}:
            raise ValueError("producer response must contain exactly producer.py")
        recipient_payload = attach_pipe3_delivery(materials["agent_payloads"]["recipient"], delivery_files)
        artifact_digest = digest_files(delivery_files)
        delivery = Delivery("delivery-0", card["task_id"], "peer-b", "peer-a", artifact_digest,
                            "producer-request-0", 0, selection.selection_id)
        append_event(ledger, delivery)
        save(episode / "delivery.json", delivery_files)

        qp_dir = episode / "producer_scorer"
        qp = run_qp(card, {"producer.py": delivery_files["producer.py"],
                           "models.py": materials["agent_payloads"]["producer"]["source_files"]["models.py"]},
                    info, card["task_id"], int(card["task_seed"]), qp_dir, log)
        save(episode / "producer_score.json", qp)
        qp_event = ProducerScore("producer-score-0", delivery.delivery_id, artifact_digest,
                                 qp.get("scorer_version", "unknown"), qp.get("status", "UNKNOWN"),
                                 qp.get("label"), qp.get("quality_score"), qp.get("response_digest"),
                                 bool(qp.get("coverage_complete")), bool(qp.get("decision_complete")))
        append_event(ledger, qp_event)
        if qp.get("status") == "UNKNOWN" or not qp.get("coverage_complete"):
            result = {"status": "UNKNOWN", "reason": "producer_scorer_incomplete", "producer_score": qp}
            save(out_dir / "ledger.json", ledger.events)
            return {**config, **result, "ended_at_utc": datetime.now(timezone.utc).isoformat()}

        judgment_prompt = common + (
            "You are the recipient. Review the delivered producer.py and decide accept, "
            "accept_with_rework, or reject_redo before executing anything. Return "
            "{\"decision\":\"...\",\"confidence\":0.0,\"rationale\":\"...\","
            "\"repair_plan\":\"...\",\"observed_artifact_sha256\":\"...\"}. "
            "The producer artifact is:\n" + json.dumps(recipient_payload, ensure_ascii=False))
        judged, judgment_meta = legacy_api.call_api(out_dir, episode, "judgment", judgment_prompt, card)
        config["real_api_calls"] += 1
        save(episode / "judgment.json", judged)
        decision = judged.get("decision")
        if decision not in {"accept", "accept_with_rework", "reject_redo"} or judged.get("observed_artifact_sha256") != artifact_digest:
            raise ValueError("invalid judgment decision or artifact binding")
        judgment = RecipientJudgment("judgment-0", delivery.delivery_id, "peer-a", decision, artifact_digest,
                                     repair_note=str(judged.get("repair_plan", "")))
        append_event(ledger, judgment)
        action = {"accept": "use", "accept_with_rework": "repair", "reject_redo": "independent_redo"}[decision]
        action_payload = prepare_pipe3_action(materials, delivery_files, action)
        action_prompt = common + (
            "You are the same recipient carrying out the sealed decision. Return the complete current "
            "public source_files snapshot. Change only paths in writable_paths; preserve all other files. "
            "A consumer action must leave processor.py present. Sealed decision:\n" + json.dumps(judged, ensure_ascii=False)
            + "\nAction payload:\n" + json.dumps(action_payload, ensure_ascii=False))
        consumed, consumer_meta = legacy_api.call_api(out_dir, episode, "consumer", action_prompt, card)
        config["real_api_calls"] += 1
        save(episode / "consumer_parsed.json", consumed)
        final_sources = consumed.get("source_files")
        if not isinstance(final_sources, dict):
            raise ValueError("consumer response missing source_files")
        validated = validate_pipe3_action_result(action_payload, final_sources)
        save(episode / "action.json", validated)
        consumer_action = ConsumerAction("action-0", delivery.delivery_id, "peer-a", action in {"use", "repair"},
                                         artifact_digest, validated["output_source_sha256"],
                                         float(consumer_meta.get("elapsed_seconds", 0.0)) if action != "use" else 0.0,
                                         action)
        append_event(ledger, consumer_action)

        qr = run_qr(card, final_sources, info, "recipient", card["task_id"], int(card["task_seed"]),
                    episode / "recipient_scorer", log)
        adoption = run_qr(card, final_sources, info, "adoption", card["task_id"], int(card["task_seed"]),
                          episode / "adoption_scorer", log)
        save(episode / "recipient_score.json", qr)
        save(episode / "adoption_score.json", adoption)
        if qr.get("status") == "UNKNOWN" or adoption.get("status") == "UNKNOWN" or not qr.get("coverage_complete") or not adoption.get("coverage_complete"):
            result = {"status": "UNKNOWN", "reason": "recipient_or_adoption_scorer_incomplete", "producer_score": qp,
                      "recipient_score": qr, "adoption_score": adoption}
            save(out_dir / "ledger.json", ledger.events)
            return {**config, **result, "ended_at_utc": datetime.now(timezone.utc).isoformat()}
        success = qr.get("status") == "PASS" and adoption.get("status") == "PASS"
        outcome = TerminalOutcome("outcome-0", delivery.delivery_id, success, "pipe3-adoption-v1",
                                  float(adoption.get("quality_score", 0.0)), sha_bytes(json.dumps(adoption, sort_keys=True).encode()))
        append_event(ledger, outcome)
        evidence = RoleEvidenceUpdate("evidence-0", judgment.judgment_id, consumer_action.action_id,
                                      outcome.outcome_id, "pipe3-real-smoke-v1", 1.0)
        append_event(ledger, evidence)
        replay = replay_ledger_events(ledger.events)
        if replay.status != "PASS":
            raise RuntimeError(f"strict ledger replay failed: {replay.status}")
        result = {"status": "COMPLETE", "reason": None, "producer_score": qp,
                  "recipient_score": qr, "adoption_score": adoption,
                  "ledger_status": replay.status, "ledger_event_count": len(ledger.events),
                  "consumer_action": action, "real_api_calls": config["real_api_calls"]}
        save(out_dir / "ledger.json", ledger.events)
        return {**config, **result, "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        result = {"status": "UNKNOWN", "reason": f"{type(exc).__name__}: {exc}",
                  "traceback": traceback.format_exc(limit=8)}
        try:
            save(out_dir / "ledger.json", ledger.events)
        except Exception:
            pass
        return {**config, **result, "ended_at_utc": datetime.now(timezone.utc).isoformat()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--card", type=Path, default=CARD_DEFAULT)
    args = parser.parse_args()
    result = run(args.output.resolve(), args.card.resolve())
    save(args.output.resolve() / "summary.json", result)
    print(json.dumps({key: result.get(key) for key in ("status", "reason", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] in {"COMPLETE", "UNKNOWN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
