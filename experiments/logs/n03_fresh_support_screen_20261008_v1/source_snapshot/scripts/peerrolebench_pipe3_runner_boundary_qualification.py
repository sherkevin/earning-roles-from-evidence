"""Zero-call qualification for the versioned PIPE3 selection boundary."""

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

from peerrolebench_baseline_policies import ContextualTrustPolicy  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary,
    auxiliary_manifest_root,
    make_offer,
)


DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _registry():
    return [
        CandidateRegistryEntry("agent-a", "v1", DIGEST_A, "internal/model", DIGEST_B),
        CandidateRegistryEntry("agent-b", "v1", DIGEST_B, "internal/model", DIGEST_B),
        CandidateRegistryEntry("agent-c", "v1", DIGEST_C, "internal/model", DIGEST_B),
    ]


def _select(boundary, offer, native_id, selector, seed, state, index, consume=True):
    return boundary.choose_and_seal(
        offer=offer, native_selection_id=native_id, selector_id=selector, role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(seed), state_version=state,
        encoder_version="pipe3-encoder-v1", feature_schema="pipe3-features-v1",
        policy_version="contextual-trust-contract-v1", base_score_version="base-zero-v1",
        rng_algorithm="numpy-pcg64", rng_draw=index, selected_at=float(index),
        read_cut=index, decision_index=index, consume_evidence=consume,
    )


def _valid_case():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), _registry())
    offer0 = make_offer(
        offer_id="offer-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="PIPE3:0", candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(), evidence_version="pipe3-evidence-v1", available_index=0,
    )
    first = _select(boundary, offer0, "selection-0", "agent-a", 3, "state-0", 0)
    row = {
        "feedback_id": "feedback-0", "source_event_id": first.policy_selection.event_id,
        "source": "recipient_judgment", "candidate_key": first.policy_selection.chosen.key,
        "evidence_version": "pipe3-evidence-v1", "source_index": 0, "arrival_index": 1,
        "arrived_at": 1.0, "delay": 1.0, "action": "accept", "disposition": "eligible",
        "provenance": "public", "label": 1.0,
    }
    offer1 = make_offer(
        offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(row,), evidence_version="pipe3-evidence-v1", available_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    _select(boundary, offer1, "selection-1", "agent-a", 4, "state-1", 1)
    native_root, auxiliary_root = boundary.validate_selection_manifests()
    return {
        "status": "PASS",
        "policy_updates": boundary.policy.updates,
        "ledger_event_count": len(boundary.ledger.events),
        "native_manifest_rows": len(boundary.native_manifest_rows),
        "auxiliary_manifest_rows": len(boundary.auxiliary_manifest_rows),
        "native_manifest_root": native_root,
        "auxiliary_manifest_root": auxiliary_root,
        "selection_ids": [row["protocol_event_id"] for row in boundary.native_manifest_rows],
    }


def _mutation_case():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), _registry())
    offer0 = make_offer(
        offer_id="mutation-offer-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="PIPE3:0", candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(), evidence_version="pipe3-evidence-v1", available_index=0,
    )
    first = _select(boundary, offer0, "mutation-selection-0", "agent-a", 3, "state-0", 0)
    wrong = "agent-c@v1" if first.policy_selection.chosen.key == "agent-b@v1" else "agent-b@v1"
    row = {
        "feedback_id": "mutation-feedback-0", "source_event_id": first.policy_selection.event_id,
        "source": "recipient_judgment", "candidate_key": wrong, "evidence_version": "pipe3-evidence-v1",
        "source_index": 0, "arrival_index": 1, "arrived_at": 1.0, "delay": 1.0,
        "action": "accept", "disposition": "eligible", "provenance": "public", "label": 1.0,
    }
    offer1 = make_offer(
        offer_id="mutation-offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(row,), evidence_version="pipe3-evidence-v1", available_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    try:
        _select(boundary, offer1, "mutation-selection-1", "agent-a", 4, "state-1", 1)
    except ValueError as exc:
        return {
            "status": "EXPECTED_REJECTION", "error": str(exc),
            "policy_updates": boundary.policy.updates,
            "native_selection_count": len(boundary.ledger.selections),
        }
    raise AssertionError("unselected candidate evidence was accepted")


def run(out_dir: Path, experiment_id: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=False)
    config = {
        "experiment_id": experiment_id,
        "qualification_version": "pipe3-runner-boundary-v1",
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": {
                name: _sha(ROOT / name) for name in (
                    "scripts/peerrolebench_pipe3_runner_v1.py",
                    "scripts/peerrolebench_candidate_registry.py",
                    "scripts/peerrolebench_event_time_schedule.py",
                    "scripts/peerrolebench_assignment_manifest.py",
                    "scripts/peerrolebench_assignment_attestation.py",
                    "scripts/peerrolebench_policy_sidecar_manifest.py",
                    "scripts/peerrolebench_baseline_policies.py",
                )
            },
        },
        "candidate_registry": "inline-three-candidate-contract-fixture",
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    valid = _valid_case()
    mutation = _mutation_case()
    raw = [
        {"event_type": "valid_selection_boundary", "timestamp_utc": datetime.now(timezone.utc).isoformat(), "payload": valid},
        {"event_type": "unselected_candidate_mutation", "timestamp_utc": datetime.now(timezone.utc).isoformat(), "payload": mutation},
    ]
    (out_dir / "raw.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in raw), encoding="utf-8")
    summary = {
        **config, "status": "QUALIFIED_OFFLINE",
        "passed": valid["status"] == "PASS" and valid["policy_updates"] == 1 and mutation["status"] == "EXPECTED_REJECTION",
        "valid": valid, "mutation": mutation,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "canonical PIPE3 selection/attestation boundary only; no API, scorer, benchmark, or learning claim",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--experiment-id", default="n03_pipe3_runner_boundary_20260928_v1")
    args = parser.parse_args()
    result = run(args.out_dir, args.experiment_id)
    print(json.dumps({"status": result["status"], "passed": result["passed"], "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
