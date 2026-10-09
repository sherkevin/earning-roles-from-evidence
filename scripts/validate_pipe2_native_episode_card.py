"""Zero-call validator for the single-episode PIPE2 native-event card."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CARD = ROOT / "configs/aamas2027/n03_pipe2_native_episode_card_v1.json"
RUNNER_VERSION = "pipe2-native-episode-card-validator-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(card: dict) -> list[str]:
    errors: list[str] = []
    if card.get("schema") != "peerrolebench-native-episode-card-v1":
        errors.append("schema")
    if card.get("status") != "DESIGN_ONLY":
        errors.append("status must remain DESIGN_ONLY before activation")
    for key in ("api_runs_allowed", "gpu_runs_allowed", "policy_update_allowed", "scientific_claim_allowed"):
        if card.get(key) is not False:
            errors.append(f"{key} must be false")
    if card.get("episode_count") != 1 or card.get("seed") != 0:
        errors.append("card must contain exactly one fixed seed-0 episode")
    ledger = card.get("native_ledger", {})
    required = ["producer_delivery", "recipient_judgment", "consumer_action", "terminal_outcome"]
    if ledger.get("required_events") != required or ledger.get("event_order") != required:
        errors.append("native event order")
    for event in required:
        if not ledger.get("required_event_fields", {}).get(event):
            errors.append(f"fields:{event}")
    if not ledger.get("judgment_is_sealed_before_action"):
        errors.append("judgment must be sealed before action")
    if not ledger.get("judgment_may_disagree_with_action"):
        errors.append("J/A mismatch must be retained")
    if not ledger.get("terminal_outcome_is_independent"):
        errors.append("terminal outcome must be independent")
    if not ledger.get("canonical_replay_required"):
        errors.append("canonical replay")
    controls = {row.get("name") for row in card.get("same_information_controls", [])}
    if not {"no_update", "j_masked_count_only"}.issubset(controls):
        errors.append("same-information controls")
    if card.get("cost_contract", {}).get("maximum_episode_attempts") != 1:
        errors.append("maximum_episode_attempts")
    if card.get("cost_contract", {}).get("maximum_retries") != 0:
        errors.append("maximum_retries")
    stops = set(card.get("stop_rules", []))
    for phrase in (
        "missing_event_or_event_hash: UNKNOWN and no update",
        "non_independent_terminal_outcome: UNKNOWN and no update",
        "read_cut_or_future_outcome_leakage: UNKNOWN and stop episode",
        "no_retry_no_manual_label_repair_no_task_substitution",
    ):
        if phrase not in stops:
            errors.append(f"stop:{phrase}")
    return errors


def run(card_path: Path, output_dir: Path) -> dict:
    card_path = card_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    config = {
        "runner_version": RUNNER_VERSION,
        "card_path": str(card_path.relative_to(ROOT)),
        "card_sha256": _sha256(card_path),
        "fixture_mode": "zero-call-design-card-validation",
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "benchmark_qualified": False,
        "scientific_claim_allowed": False,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version,
        "platform": platform.platform(),
        "started_at_utc": _now(),
    }
    (output_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    errors = validate(card)
    result = {
        **config,
        "status": "QUALIFIED_OFFLINE" if not errors else "FAILED_OFFLINE",
        "errors": errors,
        "required_event_count": len(card["native_ledger"]["required_events"]),
        "same_information_control_count": len(card["same_information_controls"]),
        "promotion_open": False,
        "interpretation": (
            "The card is structurally complete for one future real episode, but it "
            "does not authorize API/GPU execution or make a scientific claim."
        ),
        "ended_at_utc": _now(),
    }
    (output_dir / "raw.jsonl").write_text(
        json.dumps({"timestamp_utc": _now(), "event_type": "card_validation", "payload": result}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", type=Path, default=DEFAULT_CARD)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.card, args.output)
    print(json.dumps({key: result[key] for key in ("status", "errors", "promotion_open")}, indent=2))
