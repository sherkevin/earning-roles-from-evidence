"""Score frozen real C1 artifacts, without rerunning agents or changing history.

This diagnostic is post hoc: no label is inserted into past selections, policy
updates, metrics, or confirmation results. The manifest is sealed before any
new scoring, but not before the historical API experiment.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_independent_y_contract_v2 import (
    bind_episode, canonical_digest, make_diagnostic_receipt, validate_independent_y,
)
from peerrolebench_pipe3_terminal_scorer_v2 import (
    MANIFEST, MANIFEST_SHA256, WORKER, SCORER_VERSION, load_manifest, run_terminal_scorer,
)

DATA = ROOT / "experiments/logs/n03_c1_parent_source_live_20261006_v1"
ARMS = ("parent_source", "no_update", "contextual_trust_linear", "RARE")
VERSION = "c1-frozen-real-artifact-terminal-diagnostic-v2"


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_arm(arm):
    parent = DATA / arm
    summary = json.loads((parent / "summary.json").read_text())
    episode = summary.get("target", summary["source"])
    request_file = parent / f"decision_{episode['decision_index']}" / "action/action_request.json"
    request = json.loads(request_file.read_text())
    action_payload = json.loads(request["messages"][0]["content"].split("ACTION PAYLOAD:\n", 1)[1])
    response_file = request_file.with_name("action_parsed_response.json")
    response = json.loads(response_file.read_text())
    text = "".join(c["text"] for c in response["content"] if c.get("type") == "text")
    if json.loads(text)["source_files"] != episode["final_sources"]:
        raise ValueError("saved episode snapshot differs from actual API output")
    return summary, episode, action_payload


def mutation_matrix(receipt, context):
    cases = []
    for name, target, key, value in [
        ("D_relabel", "receipt", "source", "downstream_adoption"),
        ("derived_Y", "receipt", "derived_from", ["D", "recipient"]),
        ("raw_visible", "receipt", "policy_visible", True),
        ("wrong_worker_input", "receipt", "worker_input_sha256", "f" * 64),
        ("wrong_holdout", "receipt", "holdout_digest", "f" * 64),
        ("backdated_posthoc", "receipt", "arrival_index", 2),
        ("missing_feedback_id", "receipt", "feedback_id", ""),
    ]:
        r, c = deepcopy(receipt), deepcopy(context)
        (r if target == "receipt" else c)[key] = value
        cases.append((name, validate_independent_y(r, c)))
    r = deepcopy(receipt); r["binding"]["assignment_id"] = "invented"
    cases.append(("forged_assignment", validate_independent_y(r, context)))
    c = deepcopy(context); c["ledger_events"][0]["record_hash"] = "f" * 64
    cases.append(("wrong_ledger_hash", validate_independent_y(receipt, c)))
    c = deepcopy(context); c["final_sources"]["processor.py"] += "\n# swapped\n"
    cases.append(("wrong_action_output", validate_independent_y(receipt, c)))
    c = deepcopy(context); c["raw_response"]["label"] = 0
    cases.append(("raw_response_mutation", validate_independent_y(receipt, c)))
    c = deepcopy(context); c["scorer_result"]["status"] = "UNKNOWN"
    cases.append(("unknown_scorer", validate_independent_y(receipt, c)))
    cases.append(("duplicate_feedback", validate_independent_y(
        receipt, context, seen_feedback_ids=[receipt["feedback_id"]])))
    r, c = deepcopy(receipt), deepcopy(context)
    r.update(mode="online_diagnostic", arrival_index=2)
    c.update(mode="online_diagnostic", selection_read_cut=1, feedback_read_cut=2)
    online = validate_independent_y(r, c)
    r["arrival_index"] = 1
    cases.append(("target_read_cut_leak", validate_independent_y(r, c)))
    r["arrival_index"] = 3
    cases.append(("after_future_read_cut", validate_independent_y(r, c)))
    return {"positive_diagnostic_clock": online,
            "negative_cases": [{"case": n, "result": v} for n, v in cases],
            "passed": online["valid"] and not online["policy_update_allowed"] and all(
                not v["valid"] and not v["policy_update_allowed"] for _, v in cases),
            "scientific_claim_allowed": False}


def run(out_dir: Path):
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    sources = [Path(__file__), ROOT / "scripts/peerrolebench_independent_y_contract_v2.py",
               ROOT / "scripts/peerrolebench_pipe3_terminal_scorer_v2.py", WORKER, MANIFEST]
    historical = sorted(p for p in DATA.rglob("*") if p.is_file())
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [*sources, *historical]}
    config = {
        "version": VERSION, "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": sys.argv, "python": platform.python_version(), "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_hashes": hashes, "arms": list(ARMS), "new_worker_attempts": 4,
        "new_api_calls": 0, "gpu_jobs": 0, "mode": "posthoc",
        "manifest_sha256": MANIFEST_SHA256, "manifest_case_seed": 0,
        "execution_seed_note": "C1 uses seed0 public materials in all episodes; target task_seed=1 is an execution label, not a second material/root",
        "scientific_claim_allowed": False,
        "success_criterion": "all four raw API snapshots bind, determinate measurement for all arms, mutation controls reject, history unchanged",
        "no_effect_claim": "one structural root with static peers; duplicated artifacts are counted explicitly",
    }
    save(out_dir / "config.json", config)
    source_archive = out_dir / "source"; source_archive.mkdir()
    for path in sources:
        (source_archive / path.name).write_bytes(path.read_bytes())
    raw = out_dir / "raw.jsonl"
    def log(event_type, payload):
        with raw.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "event_type": event_type, "payload": payload}, ensure_ascii=False) + "\n")
            f.flush()

    manifest = load_manifest()
    holdout_digest = canonical_digest(manifest["cases"][0])
    results, contexts, receipts = [], {}, {}
    for arm in ARMS:
        case_dir = out_dir / arm; case_dir.mkdir()
        try:
            summary, ep, payload = load_arm(arm)
            binding = bind_episode(summary["ledger"], ep["delivery_id"], payload, ep["final_sources"])
            save(case_dir / "binding_before_score.json", binding)
            score = run_terminal_scorer(ep["final_sources"], "PIPE3_stream_processing", ep["decision_index"],
                                         case_dir / "terminal_scorer", log, manifest_case_seed=0)
            worker = json.loads((case_dir / "terminal_scorer/response.json").read_text())
            context = {"ledger_events": summary["ledger"], "action_payload": payload,
                       "final_sources": ep["final_sources"], "worker_request": worker["request"],
                       "raw_response": worker["response"], "scorer_result": score,
                       "holdout_digest": holdout_digest, "execution_seed": ep["decision_index"], "mode": "posthoc"}
            receipt = make_diagnostic_receipt(context, delivery_id=ep["delivery_id"], feedback_id=f"posthoc-y-{arm}")
            validated = validate_independent_y(receipt, context)
            save(case_dir / "terminal_receipt.json", receipt)
            save(case_dir / "validation.json", validated)
            contexts[arm], receipts[arm] = context, receipt
            item = {"arm": arm, "episode_index": ep["decision_index"], "J": ep["judgment"]["decision"],
                    "Qp": ep["producer_score"]["status"], "recipient": ep["recipient_score"]["status"],
                    "D_composite": ep["adoption_score"]["status"], "legacy_outcome": ep["outcome"],
                    "new_terminal": score, "binding": binding, "validation": validated}
        except Exception as exc:
            item = {"arm": arm, "status": "UNKNOWN", "error_type": type(exc).__name__, "error": str(exc)}
        results.append(item); log("case_result", item)
    mutations = mutation_matrix(receipts["RARE"], contexts["RARE"]) if "RARE" in contexts else {"passed": False}
    save(out_dir / "mutation_results.json", mutations)
    unchanged = all(hashlib.sha256(p.read_bytes()).hexdigest() == hashes[str(p.relative_to(ROOT))] for p in historical)
    passed = (len(results) == 4 and all(r.get("validation", {}).get("valid") is True for r in results)
              and mutations["passed"] and unchanged)
    result = {
        "version": VERSION, "status": "DIAGNOSTIC_COMPLETE" if passed else "UNKNOWN", "passed": passed,
        "results": results, "new_api_calls": 0, "gpu_jobs": 0, "policy_updates": 0,
        "mutation_controls_passed": mutations["passed"], "historical_files_unchanged": unchanged,
        "unique_output_artifacts": len({r["binding"]["target_snapshot_sha256"] for r in results if "binding" in r}),
        "new_diagnostic_scorer_wall_seconds": sum(r.get("new_terminal", {}).get("scorer_wall_seconds", 0) for r in results),
        "cost_scope": "new retrospective CPU diagnostics only; historical live cost untouched; CPU time/RSS not separately measured",
        "scientific_claim_allowed": False, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save(out_dir / "summary.json", result)
    log("summary", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    result = run(parser.parse_args().output)
    print(json.dumps({k: result[k] for k in ("status", "passed", "unique_output_artifacts", "historical_files_unchanged")}, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
