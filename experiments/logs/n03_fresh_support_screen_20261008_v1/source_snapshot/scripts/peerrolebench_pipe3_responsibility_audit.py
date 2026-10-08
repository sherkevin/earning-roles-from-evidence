"""Post-hoc responsibility audit for one frozen PIPE3 episode.

This audit is deliberately separate from the scorer and the runner.  It uses
only operator-held public materials plus the validated action snapshot to
decide whether a producer role update is eligible.  A recipient-owned-only
repair is descriptive evidence of integration work, not a producer label.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_task_contract import classify_consumer_changes  # noqa: E402


def audit(run_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=False, exist_ok=False)
    materials = json.loads((run_dir / "public_materials.json").read_text(encoding="utf-8"))
    action = json.loads((run_dir / "episode_0/action.json").read_text(encoding="utf-8"))
    producer_score = json.loads((run_dir / "episode_0/producer_score.json").read_text(encoding="utf-8"))
    judgment = json.loads((run_dir / "episode_0/judgment.json").read_text(encoding="utf-8"))
    adoption = json.loads((run_dir / "episode_0/adoption_score.json").read_text(encoding="utf-8"))
    change = classify_consumer_changes({"agent_payloads": materials}, action)
    producer_score_complete = (producer_score.get("status") in {"PASS", "FAIL"}
                               and producer_score.get("coverage_complete") is True
                               and producer_score.get("decision_complete") is True)
    adoption_complete = (adoption.get("status") in {"PASS", "FAIL"}
                         and adoption.get("coverage_complete") is True
                         and adoption.get("decision_complete") is True)
    producer_owned_change = bool(change["producer_owned_paths_changed"])
    eligible = (producer_score_complete and adoption_complete and producer_owned_change
                and change["observed_upstream_revision"]
                and not change["observed_consumer_integration"])
    result = {
        "audit_version": "pipe3-responsibility-audit-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "producer_score": {key: producer_score.get(key) for key in
                            ("status", "label", "quality_score", "coverage_complete", "decision_complete", "scorer_version")},
        "adoption_score": {key: adoption.get(key) for key in
                            ("status", "label", "quality_score", "coverage_complete", "decision_complete", "scorer_version")},
        "judgment": {key: judgment.get(key) for key in
                      ("decision", "observed_artifact_sha256", "repair_plan")},
        "change_classification": change,
        "producer_feedback_eligible": eligible,
        "producer_feedback_status": "ELIGIBLE" if eligible else "PENDING_ATTRIBUTION",
        "reason": ("producer-owned change is observed with complete downstream outcome"
                   if eligible else
                   "recipient-owned-only integration repair cannot label the producer"),
        "policy_update_allowed": False,
        "scientific_claim_allowed": False,
    }
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    with (output_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": result["created_at_utc"],
                                 "event_type": "responsibility_audit", "payload": result},
                                ensure_ascii=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run.resolve(), args.output.resolve())
    print(json.dumps({key: result[key] for key in
                      ("producer_feedback_status", "producer_feedback_eligible",
                       "policy_update_allowed", "scientific_claim_allowed")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
