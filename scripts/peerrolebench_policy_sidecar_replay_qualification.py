"""Qualify delayed sidecar replay into a baseline policy without LLM/GPU."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import CandidateRef, TerminalOnlyPolicy  # noqa: E402
from peerrolebench_policy_sidecar import (  # noqa: E402
    DecisionSidecar,
    FeedbackSidecar,
    PolicySidecarBridge,
)


DIGEST = "a" * 64


def record(event_type: str, event_id: str) -> dict:
    field = {
        "peer_selection": "selection_id",
        "recipient_judgment": "judgment_id",
        "terminal_outcome": "outcome_id",
    }[event_type]
    return {
        "event_type": event_type,
        "payload": {field: event_id, "task_id": "task", "task_index": 0},
        "record_hash": DIGEST,
    }


def decision() -> DecisionSidecar:
    return DecisionSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="peer_selection", protocol_event_id="s0",
        task_id="task", task_index=0, role="producer", event_id="e0", selector_id="selector-1",
        context_key="ctx", candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(0.2, 0.8), chosen_index=1, probabilities=(0.3, 0.7), propensity=0.7,
        state_version="state-0", encoder_version="enc-0", feature_schema="phi-0",
        policy_name="terminal_only", policy_version="v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=1.0,
    )


def feedback(*, event_type: str, event_id: str, disposition: str, provenance: str,
             label: float | None, action: str) -> FeedbackSidecar:
    eligible = disposition == "eligible" and provenance == "public"
    return FeedbackSidecar(
        ledger_record_hash=DIGEST, protocol_event_type=event_type, protocol_event_id=event_id,
        feedback_id=f"feedback-{event_id}", source_event_id="e0", selection_event_id="s0",
        delivery_id="d0", producer_id="peer-b", producer_version="v1", recipient_id="peer-a", source=event_type,
        arrived_at=3.0 if event_type == "recipient_judgment" else 4.0,
        delay=2.0 if event_type == "recipient_judgment" else 3.0,
        action=action, disposition=disposition, provenance=provenance,
        label_mapping_version="mapping-v1" if eligible else "",
        mapping_digest=DIGEST if eligible else "",
        responsibility_status="attributed" if eligible else "unknown",
        attribution_basis="contract-v1" if eligible else "",
        raw_value="accept_with_rework" if label is not None else None,
        label=label,
    )


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": "n03_policy_sidecar_replay_qualification_20260928",
        "kind": "engineering_replay_qualification_not_scientific_benchmark",
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "git_commit": commit},
        "policy": "terminal_only",
        "cases": ["feedback_before_selection", "delayed_unknown_then_terminal", "duplicate_terminal_channel"],
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw_path = out_dir / "raw.jsonl"
    rows: list[dict] = []

    def log(kind: str, payload: dict) -> None:
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": kind, "payload": payload}, sort_keys=True) + "\n")
            handle.flush()

    bridge = PolicySidecarBridge(TerminalOnlyPolicy())
    terminal = feedback(event_type="terminal_outcome", event_id="o0", disposition="eligible",
                        provenance="public", label=1.0, action="use")
    try:
        bridge.ingest_feedback(terminal, record("terminal_outcome", "o0"))
        rows.append({"case": "feedback_before_selection", "observed": "accepted", "expectation_met": False})
    except ValueError as exc:
        rows.append({"case": "feedback_before_selection", "observed": "rejected",
                     "error": str(exc), "expectation_met": "unknown protocol selection" in str(exc)})
    log("case_result", rows[-1])

    selected = bridge.ingest_selection(decision(), record("peer_selection", "s0"))
    log("selection_registered", {"event_id": selected.event_id, "chosen": selected.chosen.key})
    unknown = feedback(event_type="recipient_judgment", event_id="j0", disposition="unknown",
                       provenance="unknown", label=None, action="repair")
    unknown_changed = bridge.ingest_feedback(unknown, record("recipient_judgment", "j0"))
    rows.append({"case": "delayed_unknown_then_terminal", "stage": "unknown_judgment",
                 "changed": unknown_changed, "updates": bridge.policy.updates,
                 "expectation_met": unknown_changed is False and bridge.policy.updates == 0})
    log("case_result", rows[-1])
    terminal_changed = bridge.ingest_feedback(terminal, record("terminal_outcome", "o0"))
    rows.append({"case": "delayed_unknown_then_terminal", "stage": "terminal_outcome",
                 "changed": terminal_changed, "updates": bridge.policy.updates,
                 "expectation_met": terminal_changed is True and bridge.policy.updates == 1})
    log("case_result", rows[-1])
    duplicate = feedback(event_type="terminal_outcome", event_id="o1", disposition="eligible",
                         provenance="public", label=0.0, action="use")
    duplicate_changed = bridge.ingest_feedback(duplicate, record("terminal_outcome", "o1"))
    rows.append({"case": "duplicate_terminal_channel", "changed": duplicate_changed,
                 "updates": bridge.policy.updates,
                 "expectation_met": duplicate_changed is False and bridge.policy.updates == 1})
    log("case_result", rows[-1])

    summary = {
        "experiment_id": config["experiment_id"],
        "passed": all(row["expectation_met"] for row in rows),
        "case_count": len(rows), "updates": bridge.policy.updates,
        "final_policy_snapshot": bridge.policy.snapshot(),
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    log("summary", summary)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({key: result[key] for key in ("passed", "case_count", "updates",
                                                   "real_api_calls", "gpu_jobs",
                                                   "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
