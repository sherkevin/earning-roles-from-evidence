"""C0 zero-call preflight for the feature-aware RARE comparator pair.

The active seven-arm canonical manifest deliberately remains unchanged.  This
candidate preflight reuses its concrete MatrixOffer/schedule projection while
running only ``contextual_trust_linear`` and ``RARE`` in isolated policy
namespaces.  It verifies that both arms consume identical public inputs and
that a chosen candidate would be routed to an arm-specific outcome namespace.
The outcome rows are namespace receipts, not quality labels or benchmark
results; no LLM API, GPU, or native grader is called.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import (  # noqa: E402
    BaselinePolicy,
    CandidateRef,
    FeatureContextualTrustPolicy,
    Feedback,
    RarePolicy,
)
from peerrolebench_canonical_manifest import (  # noqa: E402
    build_runtime_stream_values,
    digest,
)
from peerrolebench_candidate_registry import registry_digest  # noqa: E402
from peerrolebench_event_time_schedule import schedule_digest  # noqa: E402
from peerrolebench_policy_matrix_runner_v1 import (  # noqa: E402
    fixture_case,
    rng_schedule_digest,
    _registry,
)


ARM_NAMES = ("contextual_trust_linear", "RARE")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _offer_input_digest(item: Any) -> str:
    return digest({
        "offer_id": str(item.offer.offer_id),
        "candidate_keys": [str(key) for key in item.offer.candidate_keys],
        "context_key": str(item.offer.context_key),
        "base_scores": list(item.base_scores),
        "captured_features": {
            str(key): list(values) for key, values in sorted(item.captured_features.items())
        },
        "encoder_version": str(item.encoder_version),
        "feature_schema": str(item.feature_schema),
        "read_cut": int(item.read_cut),
        "decision_index": int(item.decision_index),
        "selected_at": float(item.selected_at),
    })


def _run_policy(name: str, policy: BaselinePolicy, offers: list[Any]) -> dict[str, Any]:
    traces: list[dict[str, Any]] = []
    outcomes: list[dict[str, Any]] = []
    for item in offers:
        feedback_rows: list[dict[str, Any]] = []
        for row in item.offer.public_rows:
            source_event_id = str(row["source_event_id"])
            source_selection = policy._decisions.get(source_event_id)
            if source_selection is None:
                raise ValueError(f"{name} feedback references unknown selection {source_event_id}")
            if str(row["candidate_key"]) != source_selection.chosen.key:
                feedback_rows.append({"feedback_id": str(row["feedback_id"]), "status": "unselected"})
                continue
            feedback = Feedback(
                feedback_id=str(row["feedback_id"]), source_event_id=source_event_id,
                source=str(row["source"]), label=float(row["label"]),
                arrived_at=float(row["arrived_at"]), delay=float(row["delay"]),
                action=str(row["action"]), disposition=str(row["disposition"]),
                provenance=str(row["provenance"]), arrival_index=int(row["arrival_index"]),
                supersedes=row.get("supersedes"),
            )
            changed = policy.observe_feedback(feedback)
            feedback_rows.append({"feedback_id": str(row["feedback_id"]), "status": "eligible",
                                  "changed": bool(changed)})
        refs = tuple(CandidateRef(*str(key).rsplit("@", 1)) for key in item.offer.candidate_keys)
        selection = policy.choose(
            event_id=f"policy-{item.native_selection_id}",
            context_key=str(item.offer.context_key), selector_id=str(item.selector_id),
            candidates=refs, base_scores=item.base_scores,
            rng=np.random.default_rng(item.rng_seed), state_version=f"state-{item.decision_index}",
            encoder_version=str(item.encoder_version), feature_schema=str(item.feature_schema),
            selected_at=float(item.selected_at), captured_features=item.captured_features,
        )
        outcome = {
            "policy_namespace": name,
            "offer_id": str(item.offer.offer_id),
            "selected_key": selection.chosen.key,
            "outcome_id": f"{name}/{item.offer.offer_id}/{selection.chosen.key}",
        }
        outcome["outcome_digest"] = digest(outcome)
        outcomes.append(outcome)
        traces.append({
            "offer_id": str(item.offer.offer_id),
            "input_digest": _offer_input_digest(item),
            "chosen_key": selection.chosen.key,
            "probabilities": list(selection.probabilities),
            "propensity": float(selection.propensity),
            "feedback": feedback_rows,
        })
    snapshot = policy.snapshot()
    restored = BaselinePolicy.restore(snapshot)
    return {
        "traces": traces, "outcomes": outcomes, "updates": policy.updates,
        "state_digest": digest(snapshot), "snapshot_equal": restored.snapshot() == snapshot,
    }


def run(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    component_names = (
        "scripts/peerrolebench_baseline_policies.py",
        "scripts/peerrolebench_canonical_manifest.py",
        "scripts/peerrolebench_policy_matrix_runner_v1.py",
        "scripts/peerrolebench_c0_candidate_parity_qualification.py",
    )
    offers, schedule, schedule_hash = fixture_case("recipient_only")
    registry = _registry()
    config = {
        "experiment_id": out_dir.name,
        "kind": "zero_call_c0_candidate_parity_preflight",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "component_sha256": {name: _sha(ROOT / name) for name in component_names},
        "candidate_arms": list(ARM_NAMES),
        "root": "PIPE3_stream_processing_development_fixture",
        "registry_digest": registry_digest(registry),
        "schedule_digest": schedule_digest(schedule),
        "rng_schedule_digest": rng_schedule_digest(offers),
        "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "baseline_frozen": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    stream = build_runtime_stream_values(
        offers, schedule, registry, arm_names=ARM_NAMES, exploration=0.0,
    )
    policies = {
        "contextual_trust_linear": FeatureContextualTrustPolicy(dimension=64, exploration=0.0),
        "RARE": RarePolicy(dimension=64, exploration=0.0),
    }
    results = {name: _run_policy(name, policy, offers) for name, policy in policies.items()}
    input_digests = {name: [row["input_digest"] for row in result["traces"]]
                     for name, result in results.items()}
    if input_digests[ARM_NAMES[0]] != input_digests[ARM_NAMES[1]]:
        raise AssertionError("candidate policies did not consume identical public inputs")
    outcome_ids = [outcome["outcome_id"] for result in results.values() for outcome in result["outcomes"]]
    if len(outcome_ids) != len(set(outcome_ids)):
        raise AssertionError("candidate outcome namespaces are not independent")
    if stream["propensity"]["arm_names"] != list(ARM_NAMES):
        raise AssertionError("candidate arm order was not sealed in the public stream")
    summary = {
        "experiment_id": out_dir.name,
        "qualification_status": "QUALIFIED_OFFLINE",
        "cases": 1, "passed": 1, "failed": 0,
        "input_digest_equal": True,
        "independent_outcome_namespace": True,
        "snapshot_restore_equal": all(result["snapshot_equal"] for result in results.values()),
        "policy_results": results,
        "stream_digests": {key: digest(value) for key, value in stream.items()},
        "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "baseline_frozen": False,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for name, result in results.items():
            handle.write(json.dumps({"policy": name, **result}, ensure_ascii=False, sort_keys=True) + "\n")
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 scripts/peerrolebench_c0_candidate_parity_qualification.py OUTPUT_DIR")
    result = run(Path(sys.argv[1]))
    print(json.dumps({key: result[key] for key in (
        "qualification_status", "cases", "passed", "failed", "input_digest_equal",
        "independent_outcome_namespace", "snapshot_restore_equal",
    )}, ensure_ascii=False))
