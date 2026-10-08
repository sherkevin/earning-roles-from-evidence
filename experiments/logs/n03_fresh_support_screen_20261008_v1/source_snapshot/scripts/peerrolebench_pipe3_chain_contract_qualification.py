"""Zero-call contract qualification for the PIPE3 source-to-target card.

This checks the executable experiment card before any API or GPU work.  It is a
schema/lineage gate only: a passing receipt is not a benchmark or scientific
result, and it deliberately refuses to execute candidate code or call a model.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CARD = ROOT / "configs/aamas2027/n03_pipe3_real_smoke_v7.json"
VERSION = "pipe3-source-target-contract-v1"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def _check(condition: bool, name: str, details: str = "") -> dict[str, Any]:
    return {"name": name, "status": "PASS" if condition else "FAIL", "details": details}


def qualify(card_path: Path, out_dir: Path) -> dict[str, Any]:
    card_path = card_path.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    try:
        card_display = str(card_path.relative_to(ROOT))
    except ValueError:
        card_display = str(card_path)
    config = {
        "qualification_version": VERSION,
        "card_path": card_display,
        "card_sha256": hashlib.sha256(card_path.read_bytes()).hexdigest(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw = out_dir / "raw.jsonl"
    checks = [
        _check(card.get("primary_track") == "ArtifactRole", "primary_track"),
        _check(card.get("split") == "development/qualification", "split"),
        _check(card.get("source_episode") == 0 and card.get("target_episode") == 1, "source_target_episode"),
        _check(card.get("maximum_episode_attempts") == 2, "bounded_two_episode_chain"),
        _check(card.get("maximum_task_requests_per_episode") == 3, "bounded_api_calls"),
        _check(card.get("real_api_runs_allowed") is False, "zero_call_only"),
        _check(card.get("gpu_jobs_allowed") is False, "no_gpu"),
        _check(card.get("scientific_claim_allowed") is False, "claim_closed"),
    ]
    keys = card.get("lineage_keys", {})
    expected_keys = {
        "source_to_offer": {"delivery_id", "producer_score_id", "judgment_id", "action_id", "outcome_id", "evidence_id", "offer_id"},
        "offer_to_target": {"offer_id", "read_cut", "assignment_id", "selection_id", "task_start_id"},
        "target_credit": {"assignment_id", "selection_id", "task_start_id", "target_delivery_id", "later_use_outcome_id"},
    }
    for name, required in expected_keys.items():
        actual = set(keys.get(name, []))
        checks.append(_check(required <= actual, f"lineage_{name}", f"missing={sorted(required - actual)}"))
    ownership = card.get("ownership_registry", {})
    producer = set(ownership.get("producer_owned", []))
    recipient = set(ownership.get("recipient_owned", []))
    readonly = set(ownership.get("read_only", []))
    checks.extend([
        _check(bool(producer) and bool(recipient) and not producer & recipient, "disjoint_ownership"),
        _check(not (producer | recipient) & readonly, "readonly_disjoint"),
    ])
    cases = card.get("responsibility_cases", {})
    checks.extend([
        _check(cases.get("producer_owned_fail", {}).get("status") == "ELIGIBLE", "producer_fail_gate"),
        _check(cases.get("recipient_only", {}).get("producer_label_allowed") is False, "recipient_no_label"),
        _check(cases.get("mixed", {}).get("producer_label_allowed") is False, "mixed_no_label"),
        _check(cases.get("outside_contract", {}).get("producer_label_allowed") is False, "outside_no_label"),
        _check(cases.get("producer_pass_without_registered_defect", {}).get("producer_label_allowed") is False,
               "pass_without_defect_no_label"),
    ])
    registry = card.get("candidate_registry", [])
    selection = card.get("selection_contract", {})
    checks.extend([
        _check(len(registry) >= selection.get("minimum_menu_size", 2), "candidate_menu_size"),
        _check(selection.get("requires_registry_digest") is True, "registry_digest_required"),
        _check(selection.get("requires_menu_order") is True, "menu_order_required"),
        _check(selection.get("requires_propensity") is True, "propensity_required"),
        _check(selection.get("requires_read_cut") is True, "read_cut_required"),
    ])
    credit = card.get("credit_contract", {})
    checks.extend([
        _check(credit.get("publish_updates_policy") is False, "publish_no_update"),
        _check(credit.get("assignment_credit_once") is True, "credit_once"),
        _check(credit.get("target_outcome_required") is True, "target_outcome_required"),
        _check(credit.get("source_adoption_is_later_use") is False, "source_not_later_use"),
    ])
    for check in checks:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"event_type": "contract_check", "payload": check}, ensure_ascii=False) + "\n")
    passed = all(row["status"] == "PASS" for row in checks)
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed,
        "checks": checks,
        "check_count": len(checks),
        "card_digest": digest(card),
        "interpretation": "zero-call schema/lineage qualification only; no API, GPU, benchmark, baseline, or efficacy claim",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", type=Path, default=DEFAULT_CARD)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.card, args.out_dir)
    print(json.dumps({k: result[k] for k in ("status", "passed", "check_count", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
