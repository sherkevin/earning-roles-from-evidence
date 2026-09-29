"""Zero-call qualification for the RARE selection adapter and PIPE3 seam.

This checks that the candidate state can be replayed through the common
selection/feedback contract.  It is an implementation qualification only:
there are no LLM calls, no benchmark tasks, and no efficacy claim.
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

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import CandidateRef, Feedback, RarePolicy  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary,
    auxiliary_manifest_root,
    make_offer,
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _registry():
    return [
        CandidateRegistryEntry("agent-a", "v1", "a" * 64, "internal/model", "b" * 64),
        CandidateRegistryEntry("agent-b", "v1", "b" * 64, "internal/model", "b" * 64),
        CandidateRegistryEntry("agent-c", "v1", "c" * 64, "internal/model", "b" * 64),
    ]


def _direct_trace() -> dict:
    refs = (CandidateRef("a", "v1"), CandidateRef("b", "v1"))
    features = {"a@v1": (1.0, 0.0), "b@v1": (0.0, 1.0)}
    policy = RarePolicy(dimension=2)
    first = policy.choose(
        event_id="e0", context_key="ctx", selector_id="selector", candidates=refs,
        base_scores=(0.0, 0.0), rng=np.random.default_rng(4), state_version="s0",
        encoder_version="hash64-v1", feature_schema="phi2", captured_features=features,
    )
    unknown = policy.observe_feedback(Feedback(
        "unknown", "e0", "recipient_judgment", None, 1.0,
        disposition="unknown", provenance="unknown", arrival_index=0,
    ))
    update = policy.observe_feedback(Feedback(
        "f0", "e0", "recipient_judgment", 1.0, 2.0,
        action="accept", arrival_index=1,
    ))
    before_correction = policy.state.digest()
    correction = policy.observe_feedback(Feedback(
        "f0-correction", "e0", "recipient_judgment", 0.0, 3.0,
        action="reject", arrival_index=3, supersedes="f0",
    ))
    after_correction = policy.state.digest()
    restored = RarePolicy.restore(policy.snapshot())
    return {
        "unknown_update": unknown,
        "eligible_update": update,
        "correction_update": correction,
        "correction_changed_state": before_correction != after_correction,
        "restore_equal": restored.snapshot() == policy.snapshot(),
        "updates": policy.updates,
        "state_updates": policy.state.updates,
        "selection_probability_sum": sum(first.probabilities),
    }


def _runner_trace() -> dict:
    features = {"agent-b@v1": (1.0, 0.0), "agent-c@v1": (0.0, 1.0)}
    boundary = Pipe3SelectionBoundary(RarePolicy(dimension=2), _registry())
    offer0 = make_offer(
        offer_id="offer-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="PIPE3:0", candidate_keys=tuple(features),
        public_rows=(), evidence_version="pipe3-evidence-v1", available_index=0,
    )
    first = boundary.choose_and_seal(
        offer=offer0, native_selection_id="selection-0", selector_id="agent-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(3), state_version="state-0",
        encoder_version="hash64-v1", feature_schema="features-0", policy_version="rare-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=True,
        captured_features=features,
    )
    row = {
        "feedback_id": "feedback-0", "source_event_id": first.policy_selection.event_id,
        "source": "recipient_judgment", "candidate_key": first.policy_selection.chosen.key,
        "evidence_version": "pipe3-evidence-v1", "source_index": 0, "arrival_index": 1,
        "arrived_at": 1.0, "delay": 1.0, "action": "accept", "disposition": "eligible",
        "provenance": "public", "label": 1.0,
    }
    offer1 = make_offer(
        offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=tuple(features),
        public_rows=(row,), evidence_version="pipe3-evidence-v1", available_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    second = boundary.choose_and_seal(
        offer=offer1, native_selection_id="selection-1", selector_id="agent-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(4), state_version="state-1",
        encoder_version="hash64-v1", feature_schema="features-0", policy_version="rare-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=1,
        selected_at=1.0, read_cut=1, decision_index=1, consume_evidence=True,
        captured_features=features,
    )
    native_root, auxiliary_root_value = boundary.validate_selection_manifests()
    return {
        "policy_updates": boundary.policy.updates,
        "features_sealed": bool(first.policy_selection.captured_features),
        "probabilities_separate_after_feedback": second.policy_selection.probabilities[0] != second.policy_selection.probabilities[1],
        "native_manifest_root": native_root,
        "auxiliary_manifest_root": auxiliary_root_value,
    }


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=False)
    config = {
        "experiment_id": out_dir.name,
        "kind": "zero_llm_selection_adapter_qualification",
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": {
                name: _hash(ROOT / name) for name in (
                    "scripts/peerrolebench_baseline_policies.py",
                    "scripts/peerrolebench_raresafe_candidate.py",
                    "scripts/peerrolebench_pipe3_runner_v1.py",
                    "scripts/peerrolebench_policy_sidecar.py",
                    "scripts/peerrolebench_policy_sidecar_replay.py",
                    "scripts/peerrolebench_policy_projection.py",
                    "scripts/peerrolebench_assignment_attestation.py",
                )
            },
        },
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    raw = {"direct": _direct_trace(), "runner": _runner_trace()}
    (out_dir / "raw_output.json").write_text(json.dumps(raw, indent=2) + "\n")
    passed = (
        raw["direct"]["unknown_update"] is False
        and raw["direct"]["eligible_update"] is True
        and raw["direct"]["correction_update"] is True
        and raw["direct"]["correction_changed_state"]
        and raw["direct"]["restore_equal"]
        and raw["runner"]["policy_updates"] == 1
        and raw["runner"]["features_sealed"]
        and raw["runner"]["probabilities_separate_after_feedback"]
        and raw["runner"]["native_manifest_root"] != "GENESIS"
        and raw["runner"]["auxiliary_manifest_root"] != "GENESIS"
    )
    summary = {
        "experiment_id": config["experiment_id"],
        "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed,
        "results": raw,
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"status": result["status"], "passed": result["passed"], "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
