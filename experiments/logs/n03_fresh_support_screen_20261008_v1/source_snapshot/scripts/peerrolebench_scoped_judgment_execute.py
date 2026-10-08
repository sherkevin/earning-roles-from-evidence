"""Four frozen scoped-judgment calls; each resume spends at most one request.

The private manifest and local gold never enter the provider prompt. A structured
pass pauses for parent-only rationale review before another call is permitted.
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
from typing import Any

from peerrolebench_pipe3_material_adapter import digest_files
from peerrolebench_real_closed_loop import call_api, log, save

ROOT = Path(__file__).resolve().parents[1]
CLAUSES = {f"C{i}_{name}" for i, name in enumerate((
    "interfaces", "producer_timestamp", "producer_jsonl", "processor_jsonl",
    "sink_shape", "processor_semantics"), 1)}
PUBLIC_FILES = {"producer.py", "processor.py", "models.py", "sink.py"}
VERSION = "n03-scoped-judgment-execution-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(path: str, base: Path) -> Path:
    value = (base / path).resolve()
    if not value.is_relative_to(base.resolve()) or not value.is_file():
        raise ValueError("pinned input is absent or outside its directory")
    return value


def _inputs(card_path: Path) -> tuple[dict, Path, dict, Path, dict, list[dict]]:
    card = json.loads(card_path.read_text(encoding="utf-8"))
    if (card.get("schema_version") != VERSION or card.get("status") != "AUTHORIZED_EXECUTION"
            or card.get("real_api_runs_allowed") is not True
            or card.get("max_judgment_requests") != 4 or card.get("maximum_task_requests") != 4
            or card.get("max_episodes") != 4
            or card.get("retries") != 0 or card.get("model") != "qwen3.8-max"
            or any(card.get(field) != 0 for field in
                   ("candidate_executions", "actions", "training_updates", "gpu_runs"))
            or card.get("budget", {}).get("prior_documented_attempted_episodes") != 31
            or card.get("budget", {}).get("maximum_documented_cumulative_attempted_episodes") != 35
            or card.get("temperature") != 0 or card.get("thinking") != {"type": "disabled"}
            or card.get("stream") is not True or card.get("request_timeout_seconds") != 300
            or card.get("max_tokens") != {"judgment": 1024}):
        raise ValueError("execution card differs from four-call freeze")
    prepared = _inside(card["prepared_dir"] + "/parent_manifest.json", ROOT).parent
    manifest_path = prepared / "parent_manifest.json"
    gold_path = _inside(card["gold_summary_path"], ROOT)
    gold_config = _inside(card["gold_config_path"], ROOT)
    if (sha(manifest_path) != card["parent_manifest_sha256"]
            or sha(gold_path) != card["gold_summary_sha256"]
            or sha(gold_config) != card["gold_config_sha256"]):
        raise ValueError("parent manifest or local gold pin changed")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    cases = manifest.get("cases")
    if (manifest.get("schema_version") != "n03-scoped-judgment-parent-manifest-v1"
            or gold.get("status") != "FINITE_COMPONENT_GOLD_SUPPORTED"
            or not isinstance(cases, list) or len(cases) != 4
            or [c.get("order") for c in cases] != list(range(4))
            or len({c.get("case_id") for c in cases}) != 4):
        raise ValueError("four frozen cells or component gold are invalid")
    components = gold.get("components", {})
    if set(components) != {f"{axis}_{origin}" for axis in ("producer", "recipient")
                           for origin in ("historical", "native")}:
        raise ValueError("four independent component records are required")
    if (components["producer_native"].get("failed_check_ids") != ["P2_iso_serialization"]
            or len(gold.get("four_cell_projections", [])) != 4):
        raise ValueError("local component gold changed")
    support = None
    for case, projection in zip(cases, gold["four_cell_projections"]):
        request_path = _inside(case["request_path"], prepared)
        if sha(request_path) != case["request_sha256"]:
            raise ValueError("public request pin changed")
        request = json.loads(request_path.read_text(encoding="utf-8"))
        if set(request) != {"messages"} or len(request["messages"]) != 1 or request["messages"][0].get("role") != "user":
            raise ValueError("public-only request shape changed")
        visible = json.loads(request["messages"][0]["content"].split("\n\nPublic task payload:\n", 1)[1])
        files = visible["public_source_files"]
        if (set(visible) != {"case_id", "task_id", "public_task_text", "public_source_files",
                            "producer_artifact_sha256", "public_contract_clauses"}
                or visible["case_id"] != case["case_id"] or set(files) != PUBLIC_FILES
                or set(visible["public_contract_clauses"]) != CLAUSES
                or {name: digest_files({name: text}) for name, text in files.items()} != case["public_file_digests"]
                or visible["producer_artifact_sha256"] != case["public_file_digests"]["producer.py"]):
            raise ValueError("public request and component hashes differ")
        current_support = digest_files({name: files[name] for name in ("models.py", "sink.py")})
        support = current_support if support is None else support
        if current_support != support or support != manifest["support_digest"]:
            raise ValueError("support sources differ")
        p, r = case["producer_origin"], case["recipient_origin"]
        if (p not in ("historical", "native") or r not in ("historical", "native")
                or components[f"producer_{p}"].get("artifact_sha256") != case["public_file_digests"]["producer.py"]
                or components[f"recipient_{r}"].get("artifact_sha256") != case["public_file_digests"]["processor.py"]
                or any(components[f"{axis}_{origin}"].get("status") != ("PASS" if origin == "historical" else "FAIL")
                       or components[f"{axis}_{origin}"].get("coverage_complete") is not True
                       for axis, origin in (("producer", p), ("recipient", r)))
                or case["expected_producer_verdict"] != ("meets_contract" if p == "historical" else "violates_contract")
                or case["expected_recipient_needs_change"] is not (r == "native")
                or case["expected_recipient_target_paths"] != (["processor.py"] if r == "native" else [])
                or projection.get("case_id") != case["case_id"]
                or projection.get("producer_status") != components[f"producer_{p}"]["status"]
                or projection.get("recipient_self_status") != components[f"recipient_{r}"]["status"]):
            raise ValueError("private gold does not bind four original components")
    if {(c["producer_origin"], c["recipient_origin"]) for c in cases} != {
            (p, r) for p in ("historical", "native") for r in ("historical", "native")}:
        raise ValueError("four-cell crossing changed")
    return card, prepared, manifest, gold_path, gold, cases


def prepare(card_path: Path, out: Path) -> None:
    card_path = card_path.resolve()
    card, prepared, manifest, gold_path, _gold, cases = _inputs(card_path)
    out.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__).resolve(), ROOT / "scripts/peerrolebench_real_closed_loop.py",
               ROOT / "scripts/peerrolebench_pipe3_material_adapter.py",
               ROOT / "scripts/aamas_real_probe.py", card_path,
               prepared / "parent_manifest.json", gold_path, _inside(card["gold_config_path"], ROOT)]
    sources += [prepared / c["request_path"] for c in cases]
    hashes = {str(path): sha(path) for path in sources}
    save(out / "config.json", {"version": VERSION, "card": card, "card_path": str(card_path),
         "card_sha256": sha(card_path), "source_sha256": hashes, "python": sys.version,
         "platform": platform.platform(), "timestamp_utc": datetime.now(timezone.utc).isoformat(),
         "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "command": list(sys.argv),
         "scope": "four fixed judgment requests; no candidate, action, policy update or GPU"})
    snap = out / "source_snapshot"
    snap.mkdir()
    for i, source in enumerate(sources):
        shutil.copy2(source, snap / f"{i:02d}_{source.name}")
    _summary(out, "READY", 0, cases)
    log(out, "execution_prepared", {"card_sha256": sha(card_path),
                                   "parent_manifest_sha256": sha(prepared / "parent_manifest.json"),
                                   "gold_summary_sha256": sha(gold_path)})


def _validate_answer(answer: Any, case: dict, request: dict) -> None:
    if not isinstance(answer, dict) or set(answer) != {"producer_contract_assessment", "recipient_integration_plan"}:
        raise ValueError("two-field response schema invalid")
    p, r = answer["producer_contract_assessment"], answer["recipient_integration_plan"]
    if (not isinstance(p, dict) or set(p) != {"verdict", "observed_artifact_sha256", "contract_clause_refs", "rationale"}
            or not isinstance(r, dict) or set(r) != {"needs_change", "target_paths", "rationale"}
            or p["verdict"] not in {"meets_contract", "violates_contract", "uncertain"}
            or p["observed_artifact_sha256"] != case["public_file_digests"]["producer.py"]
            or not isinstance(p["contract_clause_refs"], list)
            or any(type(x) is not str or x not in CLAUSES for x in p["contract_clause_refs"])
            or len(set(p["contract_clause_refs"])) != len(p["contract_clause_refs"])
            or type(r["needs_change"]) is not bool
            or r["target_paths"] not in ([], ["processor.py"])
            or r["target_paths"] != (["processor.py"] if r["needs_change"] else [])
            or any(not isinstance(x, str) or not x.strip() for x in (p["rationale"], r["rationale"]))):
        raise ValueError("response fields or producer artifact binding invalid")
    if p["verdict"] != case["expected_producer_verdict"] or r["needs_change"] is not case["expected_recipient_needs_change"] or r["target_paths"] != case["expected_recipient_target_paths"]:
        raise ValueError("structured judgment disagrees with frozen component gold")
    if p["verdict"] == "violates_contract":
        if "C2_producer_timestamp" not in p["contract_clause_refs"]:
            raise ValueError("negative judgment lacks C2 reference")


def _summary(out: Path, status: str, completed: int, cases: list[dict], *,
             reason: str | None = None, failure_stage: str | None = None,
             stopped_case_index: int | None = None) -> dict:
    raw = out / "raw.jsonl"
    events = [json.loads(line) for line in raw.read_text().splitlines()] if raw.exists() else []
    starts = sum(row.get("event_type") == "request_start" for row in events)
    cells = []
    input_total = output_total = 0
    usage_complete = True
    elapsed_total = 0.0
    for index, case in enumerate(cases):
        folder = out / f"case_{index}"
        cost_path = folder / "judgment_cost.json"
        if cost_path.exists():
            cost = json.loads(cost_path.read_text(encoding="utf-8"))
            elapsed = cost.get("elapsed_seconds")
            if type(elapsed) in (int, float) and 0 <= elapsed < float("inf"):
                elapsed_total += float(elapsed)
            usage = cost.get("usage") or {}
            if (cost.get("usage_complete") is True
                    and all(type(usage.get(k)) is int and usage[k] >= 0 for k in ("input_tokens", "output_tokens"))):
                input_total += usage["input_tokens"]
                output_total += usage["output_tokens"]
            else:
                usage_complete = False
        elif folder.exists():
            usage_complete = False
        if index < completed:
            cell_status = "PASS" if (folder / "rationale_review.json").exists() else "AWAITING_RATIONALE_REVIEW"
            if status == "COMPLETE":
                cell_status = "PASS"
        elif folder.exists():
            cell_status = "FAILED" if status == "STOPPED" else "IN_PROGRESS"
        else:
            cell_status = "UNSTARTED"
        if index == stopped_case_index:
            cell_status = "FAILED"
        cells.append({"order": index, "case_id": case["case_id"], "status": cell_status})
    payload = {"status": status, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "completed": completed, "request_starts": starts, "api_calls": starts,
               "gpu_jobs": 0, "training_updates": 0, "scientific_claim_allowed": False,
               "cumulative_attempted_episodes": 31 + starts, "cells": cells,
               "usage_complete": usage_complete if starts else None,
               "known_input_tokens": input_total, "known_output_tokens": output_total,
               "known_elapsed_seconds": elapsed_total,
               "input_tokens": input_total if usage_complete and starts else None,
               "output_tokens": output_total if usage_complete and starts else None}
    if reason is not None:
        payload["reason"] = reason
    if failure_stage is not None:
        payload["failure_stage"] = failure_stage
    save(out / "summary.json", payload)
    return payload


def run_next(card_path: Path, out: Path) -> dict:
    card_path, out = card_path.resolve(), out.resolve()
    card, prepared, _manifest, _gold_path, _gold, cases = _inputs(card_path)
    config = json.loads((out / "config.json").read_text(encoding="utf-8"))
    if config.get("card_sha256") != sha(card_path) or config.get("card") != card:
        raise ValueError("execution card changed")
    if any(sha(Path(path)) != digest for path, digest in config["source_sha256"].items()):
        raise ValueError("execution source pin changed")
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (out / "raw.jsonl").read_text().splitlines()]
    starts = sum(e.get("event_type") == "request_start" for e in events)
    completed = summary["completed"]
    if starts != completed or starts > 4 or summary["status"] in {"STOPPED", "COMPLETE"}:
        raise ValueError("spent, inconsistent or terminal request sequence")
    for index in range(max(0, completed - 1)):
        prior = out / f"case_{index}" / "rationale_review.json"
        previous = out / f"case_{index}" / "judgment_response.sse"
        review = json.loads(prior.read_text(encoding="utf-8")) if prior.is_file() else {}
        if (set(review) != {"case_id", "response_sha256", "status", "evidence"}
                or review["case_id"] != cases[index]["case_id"]
                or review["response_sha256"] != sha(previous)
                or review["status"] != "PASS"
                or not isinstance(review["evidence"], str) or not review["evidence"].strip()):
            raise ValueError("earlier parent rationale review binding changed")
    if summary["status"] == "AWAITING_RATIONALE_REVIEW":
        prior = out / f"case_{completed-1}" / "rationale_review.json"
        if not prior.is_file():
            raise ValueError("parent rationale review required before next call")
        review = json.loads(prior.read_text(encoding="utf-8"))
        previous = out / f"case_{completed-1}" / "judgment_response.sse"
        if (set(review) != {"case_id", "response_sha256", "status", "evidence"}
                or review["case_id"] != cases[completed-1]["case_id"]
                or review["response_sha256"] != sha(previous)
                or review["status"] not in {"PASS", "FAIL"}
                or not isinstance(review["evidence"], str) or not review["evidence"].strip()):
            raise ValueError("parent rationale review binding invalid")
        if review["status"] == "FAIL":
            return _summary(out, "STOPPED", completed, cases,
                            reason="parent rationale review failed", failure_stage="rationale_review",
                            stopped_case_index=completed - 1)
        if completed == 4:
            summary = _summary(out, "COMPLETE", completed, cases)
            log(out, "execution_completed", {"request_starts": 4, "rationale_reviews": 4})
            return summary
    elif summary["status"] != "READY":
        raise ValueError("execution is not ready")
    if starts >= 4:
        raise ValueError("four-call budget exhausted")
    case = cases[completed]
    request = json.loads((prepared / case["request_path"]).read_text(encoding="utf-8"))
    stage_dir = out / f"case_{completed}"
    stage_dir.mkdir(exist_ok=False)
    failure_stage = "transport_or_parse"
    try:
        answer, cost = call_api(out, stage_dir, "judgment", request["messages"][0]["content"], card)
        save(stage_dir / "answer.json", answer)
        failure_stage = "response_metadata"
        if (cost.get("usage_complete") is not True or cost.get("returned_model") != card["model"]
                or cost.get("stop_reason") != "end_turn"):
            raise ValueError("response usage, model or stop reason invalid")
        failure_stage = "structured_judgment"
        _validate_answer(answer, case, request)
        failure_stage = "raw_response_binding"
        response_path = stage_dir / "judgment_response.sse"
        if not response_path.is_file():
            raise ValueError("raw SSE response is missing")
        summary = _summary(out, "AWAITING_RATIONALE_REVIEW", completed + 1, cases)
        summary["case_id"] = case["case_id"]
        summary["response_sha256"] = sha(response_path)
        summary["answer_sha256"] = sha(stage_dir / "answer.json")
        save(out / "summary.json", summary)
        log(out, "structured_pass", {"case_id": case["case_id"], "response_sha256": summary["response_sha256"]})
        return summary
    except Exception as exc:
        safe_detail = (str(exc) if failure_stage in {"response_metadata", "structured_judgment", "raw_response_binding"}
                       and type(exc) is ValueError else type(exc).__name__)
        summary = _summary(out, "STOPPED", completed, cases, reason=safe_detail,
                           failure_stage=failure_stage, stopped_case_index=completed)
        log(out, "execution_stopped", {"case_id": case["case_id"], "failure_stage": failure_stage,
                                        "reason": safe_detail})
        return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run-next"))
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.card, args.out)
        print(json.dumps({"status": "READY", "api_calls": 0}))
    else:
        result = run_next(args.card, args.out)
        print(json.dumps(result))
        sys.exit(0 if result["status"] in {"AWAITING_RATIONALE_REVIEW", "COMPLETE"} else 1)
