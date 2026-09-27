"""Log a zero-LLM sidecar schema qualification run."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess

from peerrolebench_baseline_policies import CandidateRef
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar, bind_to_ledger_record


DIGEST = "a" * 64


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": "n03_policy_sidecar_qualification_20260928",
        "kind": "engineering_qualification_not_scientific_benchmark",
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "git_commit": commit},
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    decision = DecisionSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="peer_selection", protocol_event_id="s0",
        task_id="task", task_index=0, role="producer", event_id="e0", selector_id="selector-1", context_key="ctx",
        candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(0.2, 0.8), chosen_index=1, probabilities=(0.3, 0.7), propensity=0.7,
        state_version="state-0", encoder_version="enc-0", feature_schema="phi-0",
        policy_name="no_update", policy_version="v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=1.0,
    )
    feedback = FeedbackSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="recipient_judgment", protocol_event_id="j0",
        feedback_id="f0", source_event_id="e0", selection_event_id="s0",
        delivery_id="d0", producer_id="peer-b", producer_version="v1", recipient_id="peer-a",
        source="recipient_judgment", arrived_at=3.0, delay=2.0, action="repair",
        disposition="eligible", provenance="public", label_mapping_version="judgment-v1",
        mapping_digest=DIGEST, responsibility_status="attributed", attribution_basis="producer-contract-v1",
        raw_value="accept_with_rework", label=0.5,
    )
    unknown = FeedbackSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="terminal_outcome", protocol_event_id="o0",
        feedback_id="f1", source_event_id="e0", selection_event_id="s0", delivery_id="d0",
        producer_id="peer-b", producer_version="v1", recipient_id="peer-a",
        source="terminal_outcome", arrived_at=4.0, delay=3.0, action="redo",
        disposition="unknown", provenance="unknown", label_mapping_version="", mapping_digest="",
        responsibility_status="unknown", attribution_basis="", raw_value=None, label=None,
    )
    bind_to_ledger_record(decision.payload(), {
        "event_type": "peer_selection", "payload": {
            "selection_id": "s0", "task_id": "task", "task_index": 0,
        }, "record_hash": DIGEST,
    })
    bind_to_ledger_record(feedback.payload(), {
        "event_type": "recipient_judgment", "payload": {
            "judgment_id": "j0", "task_id": "task", "task_index": 0,
        }, "record_hash": DIGEST,
    })
    bind_to_ledger_record(unknown.payload(), {
        "event_type": "terminal_outcome", "payload": {
            "outcome_id": "o0", "task_id": "task", "task_index": 0,
        }, "record_hash": DIGEST,
    })
    rows = [
        {"event_type": "decision_sidecar", "payload": decision.payload(), "sidecar_digest": decision.sidecar_digest},
        {"event_type": "feedback_sidecar", "payload": feedback.payload(), "sidecar_digest": feedback.sidecar_digest, "policy_feedback": feedback.to_feedback().__dict__},
        {"event_type": "feedback_sidecar", "payload": unknown.payload(), "sidecar_digest": unknown.sidecar_digest, "policy_feedback": None},
    ]
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    result = {
        "experiment_id": config["experiment_id"], "passed": True,
        "sidecar_version": decision.sidecar_version, "decision_bound": True,
        "eligible_feedback_converted": feedback.to_feedback() is not None,
        "unknown_feedback_converted": unknown.to_feedback() is not None,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.out_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
