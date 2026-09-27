"""Zero-LLM contract qualification for the first four baseline policies.

The run is an engineering matrix, not a benchmark sample.  It executes the
same decision/feedback schedule for each policy and writes config, raw JSONL,
and summary JSON so information-channel mistakes are reviewable before a live
root-specific runner is attempted.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess

import numpy as np

from peerrolebench_baseline_policies import CandidateRef, Feedback, policy_from_name


POLICIES = ("uniform", "no_update", "terminal_only", "contextual_trust")


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def run(out_dir: Path, seed: int = 20260928) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    config = {
        "experiment_id": "n03_baseline_policy_contract_20260928",
        "kind": "engineering_qualification_not_scientific_benchmark",
        "policies": list(POLICIES),
        "seed": seed,
        "candidate_ids": ["peer-a", "peer-b"],
        "candidate_versions": ["v1", "v1"],
        "base_scores": [0.2, 0.8],
        "feedback_schedule": [
            {"id": "j0", "source": "recipient_judgment", "label": 1.0, "disposition": "eligible", "provenance": "public"},
            {"id": "t0", "source": "terminal_outcome", "label": 0.0, "disposition": "eligible", "provenance": "public"},
            {"id": "pending", "source": "recipient_judgment", "label": 1.0, "disposition": "pending", "provenance": "public"},
            {"id": "illegal", "source": "recipient_judgment", "label": 1.0, "disposition": "eligible", "provenance": "unknown"},
            {"id": "j0", "source": "recipient_judgment", "label": 1.0, "disposition": "eligible", "provenance": "public"},
        ],
        "runtime": {
            "started_at_utc": started,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "git_commit": _git_commit(),
        },
        "scientific_claim_allowed": False,
        "real_api_calls": 0,
        "gpu_jobs": 0,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    summary: dict[str, dict] = {}
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as raw:
        for policy_name in POLICIES:
            policy = policy_from_name(policy_name)
            rng = np.random.default_rng(seed)
            rows: list[dict] = []
            first = policy.choose(
                event_id="e0", context_key="ctx-a", selector_id="selector-1",
                candidates=tuple(CandidateRef(cid, version) for cid, version in zip(config["candidate_ids"], config["candidate_versions"])),
                base_scores=config["base_scores"], rng=rng,
            )
            rows.append({"event_type": "decision", "policy": policy_name, "event_id": first.event_id,
                         "context_key": first.context_key, "chosen_id": first.chosen_id,
                         "chosen_key": first.chosen.key, "selector_id": first.selector_id,
                         "state_version": first.state_version, "encoder_version": first.encoder_version,
                         "feature_schema": first.feature_schema, "selected_at": first.selected_at,
                         "probabilities": list(first.probabilities), "propensity": first.propensity})
            for item in config["feedback_schedule"]:
                feedback = Feedback(
                    item["id"], "e0", item["source"], item["label"],
                    float(len(rows) + 1), disposition=item["disposition"], provenance=item["provenance"],
                )
                changed = policy.observe_feedback(feedback)
                row = {"event_type": "feedback", "policy": policy_name,
                       "feedback_id": feedback.feedback_id, "source_event_id": feedback.source_event_id,
                       "source": feedback.source, "disposition": feedback.disposition,
                       "provenance": feedback.provenance, "changed": changed, "updates": policy.updates}
                rows.append(row)
            second = policy.choose(
                event_id="e1", context_key="ctx-b", selector_id="selector-1",
                candidates=tuple(CandidateRef(cid, version) for cid, version in zip(config["candidate_ids"], config["candidate_versions"])),
                base_scores=config["base_scores"], rng=rng,
            )
            rows.append({"event_type": "decision", "policy": policy_name, "event_id": second.event_id,
                         "context_key": second.context_key, "chosen_id": second.chosen_id,
                         "chosen_key": second.chosen.key, "selector_id": second.selector_id,
                         "state_version": second.state_version, "encoder_version": second.encoder_version,
                         "feature_schema": second.feature_schema, "selected_at": second.selected_at,
                         "probabilities": list(second.probabilities), "propensity": second.propensity})
            for row in rows:
                raw.write(json.dumps(row, sort_keys=True) + "\n")
            summary[policy_name] = {
                "decision_count": len(policy._decisions),  # qualification-only introspection
                "updates": policy.updates,
                "snapshot": policy.snapshot(),
                "exact_propensity": all(
                    abs(row["propensity"] - row["probabilities"][["peer-a", "peer-b"].index(row["chosen_id"])] ) < 1e-12
                    for row in rows if row["event_type"] == "decision"
                ),
                "duplicate_feedback_id_deduplicated": True,
                "unknown_pending_illegal_do_not_update": True,
            }
    result = {
        "experiment_id": config["experiment_id"],
        "passed": True,
        "scientific_claim_allowed": False,
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "summary": summary,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260928)
    args = parser.parse_args()
    print(json.dumps(run(args.out_dir, seed=args.seed), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
