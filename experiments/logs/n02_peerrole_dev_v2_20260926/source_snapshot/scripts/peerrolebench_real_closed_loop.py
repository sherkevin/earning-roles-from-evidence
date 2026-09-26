"""Bounded real API integration, with an explicit source-review execution seam.

prepare -> generate(0) -> inspect sealed source -> evaluate(0) -> generate(1)
-> inspect -> evaluate(1). No retries/resume of an attempted generation stage.
All LLM requests use the existing named provider and preserve raw responses.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback

from aamas_real_probe import load_provider
from peerrolebench_consumer_checks import CHECK_VERSION, run_checks
from peerrolebench_sandbox import ROOT, SandboxedWorker
from peerrolebench_task_contract import (TEAMBENCH, export_task_materials, load_generated_task,
    attach_selected_delivery, prepare_consumer_action, validate_consumer_result, _digest_files)

sys.path.insert(0, str(ROOT / "references/aamas"))
from peer_role_protocol_20260925 import (PeerRoleLedger, PeerSelection, Delivery, RecipientJudgment,
    ConsumerAction, TerminalOutcome, RoleEvidenceUpdate, LaterAssignment)

CARD = ROOT / "configs/aamas2027/n02_peerrole_dev_v1.json"
DECISIONS = {"accept": "use", "accept_with_rework": "repair", "reject_redo": "independent_redo"}
EVENT_METHODS = {"peer_selection": ("record_selection", PeerSelection),
    "producer_delivery": ("record_delivery", Delivery), "recipient_judgment": ("record_judgment", RecipientJudgment),
    "consumer_action": ("record_action", ConsumerAction), "terminal_outcome": ("record_outcome", TerminalOutcome),
    "role_evidence_update": ("record_evidence_update", RoleEvidenceUpdate), "later_assignment": ("record_assignment", LaterAssignment)}


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def log(out, event_type, payload):
    with (out / "raw.jsonl").open("a") as stream:
        stream.write(json.dumps({"timestamp_utc": now(), "event_type": event_type, "payload": payload}, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def sources():
    paths = list((ROOT / "scripts").glob("peerrolebench_*.py"))
    paths += [ROOT / "scripts/aamas_real_probe.py", ROOT / "references/aamas/peer_role_protocol_20260925.py",
              ROOT / "tools/peerrole-runtime/package-lock.json", CARD]
    return {str(path.relative_to(ROOT)): sha(path) for path in paths}


def validate_public_source(files, card):
    """Conservative review aid, not a sandbox or a hostile-code verifier."""
    trees = {}
    forbidden = {"eval", "exec", "compile", "open", "__import__", "globals", "locals", "vars", "getattr", "setattr", "delattr", "breakpoint"}
    for name, text in files.items():
        if not isinstance(text, str) or len(text.encode()) > 64 * 1024:
            raise ValueError("Source must be bounded text")
        tree = ast.parse(text, filename=name)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                           else ["mqueue" if node.level else node.module or "mqueue"])
                if any(module.split(".")[0] not in card["source_import_allowlist"] for module in modules):
                    raise ValueError("Source import outside reviewed task scope: " + name)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbidden:
                raise ValueError("Source contains execution/introspection/IO outside task scope")
            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                raise ValueError("Source contains dunder introspection outside task scope")
        trees[name] = tree
    return trees


def load_ledger(out):
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    path = out / "ledger.json"
    if path.exists():
        for event in json.loads(path.read_text()):
            if event["event_type"] == "task_start":
                ledger.record_task_start(**event["payload"])
            else:
                method, kind = EVENT_METHODS[event["event_type"]]
                getattr(ledger, method)(kind(**event["payload"]))
            if ledger.events[-1]["record_hash"] != event["record_hash"]:
                raise RuntimeError("Ledger replay hash mismatch")
    return ledger


def append_event(out, ledger, method, event):
    getattr(ledger, method)(event)
    save(out / "ledger.json", ledger.events)
    log(out, "ledger_event", ledger.events[-1])


def parse_object(text):
    text = text.strip()
    if text.startswith("```json") and text.endswith("```"):
        text = text[7:-3].strip()
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object")
    return value


def parse_sse(raw):
    """Decode only complete Anthropic-compatible SSE; retain raw stream on disk.

    The named provider reports provisional zero usage at message_start and
    actual usage at message_delta. A missing final event is never success.
    """
    blocks = {}
    result = {"usage": {}, "content": []}
    message_started = message_stopped = final_usage = False
    for frame in raw.replace("\r\n", "\n").split("\n\n"):
        data = "\n".join(line[5:].lstrip() for line in frame.splitlines() if line.startswith("data:"))
        if not data or data == "[DONE]":
            continue
        event = json.loads(data)
        kind = event.get("type")
        if kind == "error":
            raise RuntimeError("Provider stream error: " + json.dumps(event.get("error")))
        if kind == "message_start":
            message_started = True
            message = event["message"]
            result.update({"model": message.get("model"), "id": message.get("id")})
            result["usage"].update(message.get("usage", {}))
        elif kind == "content_block_start" and event["content_block"].get("type") == "text":
            blocks[event["index"]] = event["content_block"].get("text", "")
        elif kind == "content_block_delta" and event["delta"].get("type") == "text_delta":
            blocks[event["index"]] = blocks.get(event["index"], "") + event["delta"]["text"]
        elif kind == "message_delta":
            result["stop_reason"] = event.get("delta", {}).get("stop_reason")
            usage = event.get("usage", {})
            result["usage"].update(usage)
            final_usage = all(isinstance(usage.get(k), int) for k in ("input_tokens", "output_tokens"))
        elif kind == "message_stop":
            message_stopped = True
    if not message_started or not message_stopped:
        raise ValueError("Incomplete SSE response")
    result["content"] = [{"type": "text", "text": blocks[i]} for i in sorted(blocks)]
    result["final_usage_observed"] = final_usage
    return result


def call_api(out, stage_dir, stage, prompt, card):
    attempts = sum(1 for line in (out / "raw.jsonl").read_text().splitlines()
                   if json.loads(line)["event_type"] == "request_start")
    if attempts >= card["maximum_task_requests"]:
        raise RuntimeError("Request budget exhausted")
    provider = load_provider()
    secret = provider["secret"]
    request = {"model": card["model"], "messages": [{"role": "user", "content": prompt}],
               "temperature": card["temperature"], "max_tokens": card["max_tokens"][stage],
               "stream": card.get("stream", False)}
    request_path = stage_dir / (stage + "_request.json")
    save(request_path, request)
    response_path = stage_dir / (stage + ("_response.sse" if request["stream"] else "_response.json"))
    command = ["curl", "-q", "--silent", "--show-error", "--no-buffer", "--fail-with-body", "--noproxy", "*",
               "--connect-timeout", "15", "--max-time", str(card["request_timeout_seconds"]),
               "--config", "-", "--data-binary", "@" + str(request_path),
               "--output", str(response_path), "--write-out", "%{json}", provider["base"] + "/v1/messages"]
    # Feed auth through stdin, not process arguments or an on-disk config.
    if any(c in secret for c in '\n\r"\\'):
        raise ValueError("Unsupported credential serialization")
    curl_config = 'header = "Content-Type: application/json"\nheader = "anthropic-version: 2023-06-01"\nheader = "Authorization: Bearer ' + secret + '"\n'
    log(out, "request_start", {"attempt": attempts + 1, "stage": stage, "directory": stage_dir.name,
                               "request": request, "command_without_secret": command,
                               "provider": provider["base"], "retries": 0})
    started = time.monotonic()
    proc = subprocess.run(command, input=curl_config, text=True, capture_output=True,
                          timeout=card["request_timeout_seconds"] + 10)
    raw_text = response_path.read_text() if response_path.exists() else ""
    raw_text = raw_text.replace(secret, "[REDACTED]")
    response_path.write_text(raw_text)
    try:
        timing = json.loads(proc.stdout)
    except ValueError:
        timing = {}
    metadata = {"elapsed_seconds": time.monotonic() - started, "http_status": str(timing.get("http_code", "unknown")),
                "exit_code": proc.returncode, "stderr": proc.stderr.replace(secret, "[REDACTED]"),
                "stage": stage, "directory": stage_dir.name, "usage": None, "usage_complete": False,
                "transport_metrics": {k: timing.get(k) for k in ("time_namelookup", "time_connect", "time_appconnect", "time_starttransfer", "time_total", "size_download")}}
    try:
        result = parse_sse(raw_text) if request["stream"] else json.loads(raw_text)
        metadata.update({"usage": result.get("usage"), "returned_model": result.get("model"),
                         "stop_reason": result.get("stop_reason")})
        metadata["usage_complete"] = (all(isinstance((result.get("usage") or {}).get(k), int) for k in ("input_tokens", "output_tokens"))
                                       and (not request["stream"] or result.get("final_usage_observed")))
        if request["stream"]:
            save(stage_dir / (stage + "_parsed_response.json"), result)
    except (ValueError, RuntimeError) as exc:
        metadata["response_decode_error"] = repr(exc)
        result = {}
    save(stage_dir / (stage + "_cost.json"), metadata)
    log(out, "request_result", metadata)
    if proc.returncode or metadata["http_status"] != "200":
        raise RuntimeError("Real API request failed; see recorded HTTP/transport outcome")
    if result.get("stop_reason") in {"max_tokens", "length"}:
        raise ValueError("Model output truncated")
    text = "\n".join(block.get("text", "") for block in result.get("content", []) if block.get("type") == "text")
    if not text.strip():
        raise ValueError("Model returned no text")
    return parse_object(text), metadata


def prepare(out):
    out.mkdir(parents=True, exist_ok=False)
    card = json.loads(CARD.read_text())
    source_hashes = sources()
    git_pin = subprocess.check_output(["git", "-C", str(TEAMBENCH), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(TEAMBENCH), "status", "--porcelain"], text=True)
    if git_pin != card["source_commit"] or dirty:
        raise RuntimeError("Task source pin mismatch")
    metadata = {"created_utc": now(), "card": card, "card_path": str(CARD.relative_to(ROOT)), "source_hashes": source_hashes,
                "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "python": sys.version, "command": sys.argv, "scientific_claim_allowed": False}
    save(out / "config.json", metadata)
    snapshot = out / "source_snapshot"
    for name in source_hashes:
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    rng = random.Random(card["policy_seed"])
    first = card["first_consumer"]
    menu = sorted(set(card["agents"]) - {first})
    draw = rng.random()
    selected = menu[min(int(draw * len(menu)), len(menu) - 1)]
    second = next(a for a in card["agents"] if a not in {first, selected})
    state = {"consumers": [first, second], "selected": [selected], "propensities": [1 / len(menu)],
             "initial_draw": draw, "next_draw": rng.random(), "statuses": ["unstarted", "unstarted"],
             "shared_evidence": [], "scores": {a: card["update"]["initial_score"] for a in card["agents"]}}
    save(out / "state.json", state)
    for index, seed in enumerate(card["task_seeds"]):
        materials = export_task_materials(load_generated_task(card["task_id"], seed))
        save(out / f"materials_{index}.json", materials)
    log(out, "config", metadata)
    log(out, "first_selection_draw", state)
    print(json.dumps({"prepared": True, "first_peer": selected, "first_consumer": first, "next_consumer": second}))


def generate(out, index, config, state):
    card = config["card"]
    if index not in {0, 1} or state["statuses"][index] != "unstarted":
        raise RuntimeError("Attempt already started or index invalid; no retries")
    if index == 1 and state["statuses"][0] != "complete":
        raise RuntimeError("No complete first chain; second episode forbidden")
    state["statuses"][index] = "attempted"
    save(out / "state.json", state)
    directory = out / f"episode_{index}"
    directory.mkdir(exist_ok=False)
    log(out, "episode_attempt", {"index": index, "seed": card["task_seeds"][index]})
    materials = json.loads((out / f"materials_{index}.json").read_text())
    consumer, peer = state["consumers"][index], state["selected"][index]
    ledger = load_ledger(out)
    selection = PeerSelection(f"selection-{index}", card["task_id"], index, consumer, "producer",
                              tuple(sorted(set(card["agents"]) - {consumer})), peer, state["propensities"][index])
    append_event(out, ledger, "record_selection", selection)
    ledger.record_task_start(card["task_id"], index)
    save(out / "ledger.json", ledger.events)
    log(out, "ledger_event", ledger.events[-1])
    common = "You are one member of a team of otherwise identical agents. Solve the assigned public Python task. Do not inspect evaluation machinery or external files. No tools are available. Return a single JSON object, with no markdown or commentary. "
    prompt = common + "You are the producer for this task. Repair only the writable source paths. Preserve public names/signatures. Return {\"source_files\":{\"path\":\"full file text\"}} with exactly the writable paths. Task payload:\n" + json.dumps(materials["agent_payloads"]["producer"], ensure_ascii=False)
    produced, producer_cost = call_api(out, directory, "producer", prompt, card)
    delivery_files = produced.get("source_files")
    if not isinstance(delivery_files, dict):
        raise ValueError("Producer source_files missing")
    recipient = attach_selected_delivery(materials["agent_payloads"]["recipient"], delivery_files)
    validate_public_source(delivery_files, card)
    digest = _digest_files(delivery_files)
    delivery = Delivery(f"delivery-{index}", card["task_id"], peer, consumer, digest,
                        f"producer-request-{index}", index, selection.selection_id)
    append_event(out, ledger, "record_delivery", delivery)
    save(directory / "delivery.json", delivery_files)
    visible_history = state["shared_evidence"] if index == 1 else []
    judgment_payload = {"task": recipient, "producer_id": peer, "recipient_id": consumer,
                        "artifact_sha256": digest, "legally_shared_prior_evidence": visible_history}
    prompt = common + 'You are the recipient who will integrate this actual delivery. Review its code before any execution. Choose accept (use producer files unchanged), accept_with_rework (repair their copy before use), or reject_redo (rebuild from the original public template). Your integration must still implement consumer.py. Return {"decision":"accept|accept_with_rework|reject_redo","confidence":0.0,"rationale":"explain concrete observations","repair_plan":"needed work","observed_artifact_sha256":"copy the given digest"}. No terminal score is available. Public payload:\n' + json.dumps(judgment_payload, ensure_ascii=False)
    judged, judgment_cost = call_api(out, directory, "judgment", prompt, card)
    if judged.get("decision") not in DECISIONS or judged.get("observed_artifact_sha256") != digest:
        raise ValueError("Judgment decision or artifact digest invalid")
    if not isinstance(judged.get("rationale"), str) or not judged["rationale"].strip():
        raise ValueError("Judgment lacks a source-review rationale")
    if not 0 <= float(judged.get("confidence", -1)) <= 1:
        raise ValueError("Judgment confidence outside range")
    judgment = RecipientJudgment(f"judgment-{index}", delivery.delivery_id, consumer, judged["decision"],
                                 digest, repair_note=judged.get("repair_plan", ""))
    append_event(out, ledger, "record_judgment", judgment)
    save(directory / "judgment.json", judged)
    action = DECISIONS[judged["decision"]]
    action_payload = prepare_consumer_action(materials, delivery_files, action)
    prompt = common + 'You are the same recipient, now carrying out your sealed decision. Implement the consumer and any repair/rebuild permitted by writable_paths. Use only public requirements. Return {"source_files":{"path":"full file text"}} for changed writable files; consumer.py is required. Read-only files must not be returned or changed. Sealed judgment:\n' + json.dumps(judged, ensure_ascii=False) + "\nAction payload:\n" + json.dumps(action_payload, ensure_ascii=False)
    consumed, consumer_cost = call_api(out, directory, "consumer", prompt, card)
    changes = consumed.get("source_files")
    if not isinstance(changes, dict) or "mqueue/consumer.py" not in changes or not set(changes) <= set(action_payload["writable_paths"]):
        raise ValueError("Consumer changed paths violate action contract")
    final_sources = {**action_payload["source_files"], **changes}
    trees = validate_public_source(final_sources, card)
    validated = validate_consumer_result(action_payload, final_sources)
    # Derive interface names from public source, not expected.json metadata.
    queue_names = [n.name for n in trees["mqueue/queue.py"].body if isinstance(n, ast.ClassDef) and n.name not in {"QueueFull", "QueueEmpty"}]
    consumer_names = [n.name for n in trees["mqueue/consumer.py"].body if isinstance(n, ast.ClassDef) and n.name.endswith("Consumer")]
    if len(queue_names) != 1 or len(consumer_names) != 1:
        raise ValueError("Public interface class inventory ambiguous")
    save(directory / "sealed_consumer.json", validated)
    save(directory / "interfaces.json", {"queue": queue_names[0], "consumer": consumer_names[0]})
    materialized = directory / "sealed_source"
    for name, text in final_sources.items():
        path = materialized / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    consumer_action = ConsumerAction(f"action-{index}", delivery.delivery_id, consumer,
                                    action in {"use", "repair"}, digest, validated["output_source_sha256"],
                                    consumer_cost["elapsed_seconds"] if action != "use" else 0.0, action)
    append_event(out, ledger, "record_action", consumer_action)
    log(out, "sealed_consumer", {"index": index, "sha256": validated["output_source_sha256"],
        "action": action, "changed_paths": validated["changed_paths"],
        "producer_objective_quality": None, "repair_cost_unit": "full consumer call seconds when repair/redo; not marginal causal overhead"})
    state["statuses"][index] = "awaiting_source_review"
    save(out / "state.json", state)
    print(json.dumps({"index": index, "status": state["statuses"][index],
                      "source": str(materialized), "sha256": validated["output_source_sha256"]}))


def evaluate(out, index, reviewed_sha256, config, state):
    card = config["card"]
    if state["statuses"][index] != "awaiting_source_review":
        raise RuntimeError("Episode not awaiting review")
    directory = out / f"episode_{index}"
    sealed = json.loads((directory / "sealed_consumer.json").read_text())
    if reviewed_sha256 != sealed["output_source_sha256"] or _digest_files(sealed["source_files"]) != reviewed_sha256:
        raise RuntimeError("Reviewed source digest mismatch")
    validate_public_source(sealed["source_files"], card)
    log(out, "source_review", {"index": index, "sha256": reviewed_sha256,
                                "scope": "static task-source review, not adversarial proof"})
    state["statuses"][index] = "evaluating"
    save(out / "state.json", state)
    interfaces = json.loads((directory / "interfaces.json").read_text())
    with SandboxedWorker(sealed["source_files"], directory / "evaluation", lambda e,p: log(out,e,p),
                         interfaces["queue"], interfaces["consumer"]) as worker:
        result = run_checks(worker.request)
    save(directory / "consumer_score.json", result)
    log(out, "consumer_score", {"index": index, "result": result})
    if result["status"] == "UNKNOWN" or not result["coverage_complete"]:
        state["statuses"][index] = "UNKNOWN"
        save(out / "state.json", state)
        log(out, "stop", {"reason": "Scorer incomplete; no capability label or role evidence update"})
        print(json.dumps({"index": index, "status": "UNKNOWN", "no_update": True}))
        return
    ledger = load_ledger(out)
    score = sum(r["status"] == "PASS" for r in result["checks"]) / len(result["checks"])
    outcome = TerminalOutcome(f"outcome-{index}", f"delivery-{index}", result["status"] == "PASS",
                              CHECK_VERSION, score, sha(directory / "consumer_score.json"))
    append_event(out, ledger, "record_outcome", outcome)
    evidence = RoleEvidenceUpdate(f"evidence-{index}", f"judgment-{index}", f"action-{index}",
                                  outcome.outcome_id, "integration-action-score-v1", time.time())
    append_event(out, ledger, "record_evidence_update", evidence)
    peer = state["selected"][index]
    prior = state["scores"][peer]
    action = sealed["consumer_action"]
    value = card["update"]["action_values"][action]
    step = card["update"]["step_size"]
    state["scores"][peer] = (1 - step) * prior + step * value
    shared = {"evidence_id": evidence.evidence_id, "judge_id": state["consumers"][index],
              "producer_id": peer, "task_family": card["task_id"], "instance_seed": card["task_seeds"][index],
              "decision": json.loads((directory / "judgment.json").read_text()), "action": action,
              "producer_objective_quality": "not measured", "final_quality_not_used_as_producer_correctness": True}
    state["shared_evidence"].append(shared)
    log(out, "controller_update", {"peer": peer, "old": prior, "new": state["scores"][peer],
                                   "target": "source-review action suitability, not objective correctness"})
    if index == 0:
        consumer = state["consumers"][1]
        menu = sorted(set(card["agents"]) - {consumer})
        weights = [math.exp(state["scores"][p]) for p in menu]
        probabilities = [0.5 / len(menu) + 0.5 * w / sum(weights) for w in weights]
        draw = state["next_draw"]
        chosen = menu[0] if draw < probabilities[0] else menu[1]
        propensity = probabilities[menu.index(chosen)]
        state["selected"].append(chosen)
        state["propensities"].append(propensity)
        log(out, "evidence_transfer", {"consumer": consumer, "evidence": shared,
            "menu": menu, "scores": state["scores"], "probabilities": probabilities, "draw": draw,
            "selection_owner": "consumer controller", "chosen": chosen})
        append_event(out, ledger, "record_assignment", LaterAssignment("assignment-1", card["task_id"], 1,
            chosen, "producer", (evidence.evidence_id,), propensity))
    state["statuses"][index] = "complete"
    save(out / "state.json", state)
    print(json.dumps({"index": index, "status": "complete", "consumer_behavior_score": score,
                      "action": action, "future_assignment": state["selected"][1:]}))


def main():
    global CARD
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["prepare", "generate", "evaluate"])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--reviewed-sha256")
    parser.add_argument("--card", type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if args.stage == "prepare":
        if args.card:
            CARD = args.card.resolve()
        prepare(out)
        return
    config = json.loads((out / "config.json").read_text())
    CARD = ROOT / config.get("card_path", str(CARD.relative_to(ROOT)))
    state = json.loads((out / "state.json").read_text())
    if config["source_hashes"] != sources():
        raise RuntimeError("Frozen source changed: version a new contract before another request")
    try:
        if args.stage == "generate":
            generate(out, args.index, config, state)
        else:
            evaluate(out, args.index, args.reviewed_sha256, config, state)
    except Exception as exc:
        log(out, "stage_error", {"index": args.index, "stage": args.stage, "error": repr(exc), "traceback": traceback.format_exc()})
        state["statuses"][args.index] = "UNKNOWN"
        save(out / "state.json", state)
        log(out, "stop", {"reason": "This version permits no retry or replacement after incomplete episode"})
        raise


if __name__ == "__main__":
    main()
