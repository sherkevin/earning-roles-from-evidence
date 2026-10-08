"""Zero-call qualification for the feature-aware same-information control.

This receipt checks the public-input contract needed before a live RARE versus
contextual comparison.  It does not claim a benchmark result, an efficacy
gain, or a frozen baseline.  The existing Beta ``contextual_trust`` remains a
context-only diagnostic; this script qualifies the separate
``contextual_trust_linear`` candidate against RARE's public feature boundary.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import (  # noqa: E402
    CandidateRef,
    FeatureContextualTrustPolicy,
    Feedback,
    RarePolicy,
    ContextualTrustPolicy,
)


FEATURES: dict[str, tuple[float, ...]] = {
    "agent-a@v1": tuple([1.0] + [0.0] * 63),
    "agent-b@v1": tuple([0.0, 1.0] + [0.0] * 62),
}
CANDIDATES = (CandidateRef("agent-a", "v1"), CandidateRef("agent-b", "v1"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _choose(policy: Any, event_id: str, features: Mapping[str, tuple[float, ...]] = FEATURES,
            *, base: tuple[float, float] = (0.0, 0.0), seed: int = 7):
    return policy.choose(
        event_id=event_id,
        context_key="qualification-context",
        selector_id="qualification-selector",
        candidates=CANDIDATES,
        base_scores=base,
        rng=np.random.default_rng(seed),
        state_version="qualification-state-v1",
        encoder_version="hash64-v1",
        feature_schema="hash64-v1-public",
        selected_at=float(seed),
        captured_features=features,
    )


def _feedback(event_id: str, *, label: float, feedback_id: str = "f0",
              arrival_index: int = 1, supersedes: str | None = None,
              disposition: str = "eligible") -> Feedback:
    return Feedback(
        feedback_id=feedback_id, source_event_id=event_id,
        source="recipient_judgment", label=label, arrived_at=float(arrival_index),
        delay=0.0, action="accept", disposition=disposition, provenance="public",
        arrival_index=arrival_index, supersedes=supersedes,
    )


def _by_key(selection: Any) -> dict[str, float]:
    return {
        candidate.key: float(probability)
        for candidate, probability in zip(selection.candidates, selection.probabilities)
    }


def _assert_close(left: Any, right: Any, tolerance: float = 1e-12) -> None:
    left_values = tuple(float(item) for item in left)
    right_values = tuple(float(item) for item in right)
    assert len(left_values) == len(right_values)
    assert all(abs(a - b) <= tolerance for a, b in zip(left_values, right_values))


def _record(records: list[dict[str, Any]], case: str, fn) -> None:
    try:
        payload = fn()
    except Exception as exc:  # pragma: no cover - receipt failure path
        records.append({
            "case": case, "status": "FAIL", "false_accept": False,
            "error": f"{type(exc).__name__}: {exc}",
        })
    else:
        records.append({"case": case, "status": "PASS", **payload})


def _run_cases() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def input_contract() -> dict[str, Any]:
        linear = FeatureContextualTrustPolicy(dimension=64, exploration=0.0)
        rare = RarePolicy(dimension=64, exploration=0.0)
        left = _choose(linear, "linear-e0", seed=3)
        right = _choose(rare, "rare-e0", seed=3)
        assert tuple(left.candidates) == tuple(right.candidates)
        assert left.base_scores == right.base_scores
        assert left.encoder_version == right.encoder_version == "hash64-v1"
        assert left.feature_schema == right.feature_schema == "hash64-v1-public"
        assert left.captured_features == right.captured_features
        return {
            "candidate_menu_digest": _digest([item.key for item in left.candidates]),
            "base_scores_digest": _digest(left.base_scores),
            "feature_digest": _digest(left.captured_features),
            "same_public_input": True,
        }

    _record(records, "same_public_menu_features_and_base_scores", input_contract)

    def feature_sensitive_update() -> dict[str, Any]:
        rows: dict[str, Any] = {}
        for name, factory in (
            ("contextual_trust_linear", lambda: FeatureContextualTrustPolicy(dimension=64, exploration=0.0)),
            ("RARE", lambda: RarePolicy(dimension=64, exploration=0.0)),
        ):
            policy = factory()
            first = _choose(policy, f"{name}-e0", seed=7)
            assert policy.observe_feedback(_feedback(first.event_id, label=1.0)) is True
            learned_key = first.chosen.key
            other_key = next(item.key for item in first.candidates if item.key != learned_key)
            original = _choose(policy, f"{name}-e1", FEATURES, seed=11)
            swapped_features = {
                learned_key: FEATURES[other_key], other_key: FEATURES[learned_key],
            }
            swapped = _choose(policy, f"{name}-e2", swapped_features, seed=11)
            original_by_key = _by_key(original)
            swapped_by_key = _by_key(swapped)
            assert original_by_key[learned_key] > original_by_key[other_key]
            assert swapped_by_key[other_key] > swapped_by_key[learned_key]
            rows[name] = {
                "learned_key": learned_key,
                "original_feature_digest": _digest(FEATURES),
                "swapped_feature_digest": _digest(swapped_features),
                "updates": policy.updates,
            }
        return {"policies": rows}

    _record(records, "feature_mutation_changes_assignment_scores", feature_sensitive_update)

    def context_only_diagnostic() -> dict[str, Any]:
        left = ContextualTrustPolicy()
        right = ContextualTrustPolicy()
        first = _choose(left, "ctx-e0", FEATURES, seed=2, base=(0.3, 0.3))
        second = _choose(right, "ctx-e0", {
            "agent-a@v1": FEATURES["agent-b@v1"],
            "agent-b@v1": FEATURES["agent-a@v1"],
        }, seed=2, base=(0.3, 0.3))
        _assert_close(first.probabilities, second.probabilities)
        return {"feature_mutation_ignored_by_context_only": True}

    _record(records, "context_only_control_ignores_feature_mutation", context_only_diagnostic)

    def base_score_term() -> dict[str, Any]:
        values: dict[str, Any] = {}
        for name, factory in (
            ("contextual_trust_linear", lambda: FeatureContextualTrustPolicy(dimension=64, exploration=0.0)),
            ("RARE", lambda: RarePolicy(dimension=64, exploration=0.0)),
        ):
            policy = factory()
            low = _choose(policy, f"{name}-low", base=(0.0, 0.0), seed=4)
            high = _choose(policy, f"{name}-high", base=(0.0, 2.0), seed=4)
            assert high.probabilities[1] > low.probabilities[1]
            values[name] = {
                "low_probability_b": low.probabilities[1],
                "high_probability_b": high.probabilities[1],
            }
        return {"policies": values, "shared_base_score_term": True}

    _record(records, "base_scores_are_consumed_by_both_policies", base_score_term)

    def boundaries_and_restore() -> dict[str, Any]:
        values: dict[str, Any] = {}
        for name, factory in (
            ("contextual_trust_linear", lambda: FeatureContextualTrustPolicy(dimension=64, exploration=0.0)),
            ("RARE", lambda: RarePolicy(dimension=64, exploration=0.0)),
        ):
            policy = factory()
            first = _choose(policy, f"{name}-e0", seed=5)
            assert policy.observe_feedback(_feedback(first.event_id, label=1.0)) is True
            assert policy.observe_feedback(_feedback(first.event_id, label=0.0, feedback_id="f0-correction",
                                                     arrival_index=2, supersedes="f0")) is (name == "RARE")
            restored = type(policy).restore(policy.snapshot())
            left = _choose(policy, f"{name}-e1", seed=13)
            right = _choose(restored, f"{name}-e1", seed=13)
            _assert_close(left.probabilities, right.probabilities)
            values[name] = {
                "updates": policy.updates,
                "restore_exact": True,
                "correction_updates": name == "RARE",
            }
        return {"policies": values, "correction_behavior_is_explicit": True}

    _record(records, "snapshot_restore_and_correction_boundary", boundaries_and_restore)

    def invalid_feature_is_rejected() -> dict[str, Any]:
        linear = FeatureContextualTrustPolicy(dimension=64)
        try:
            _choose(linear, "invalid", {"agent-a@v1": (1.0,) * 64, "agent-b@v1": FEATURES["agent-b@v1"]})
        except ValueError:
            pass
        else:
            raise AssertionError("unbounded feature vector was accepted")
        return {"invalid_feature_status": "rejected"}

    _record(records, "bounded_feature_contract_fail_closed", invalid_feature_is_rejected)
    return records


def run(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    component_names = (
        "scripts/peerrolebench_baseline_policies.py",
        "scripts/peerrolebench_feature_contextual_qualification.py",
        "tests/test_peerrolebench_baseline_policies.py",
    )
    config = {
        "experiment_id": out_dir.name,
        "kind": "zero_call_feature_contextual_same_information_qualification",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "component_sha256": {name: _sha(ROOT / name) for name in component_names},
        "candidate_policy": "contextual_trust_linear",
        "reference_policy": "RARE",
        "representation": {"encoder_version": "hash64-v1", "dimension": 64,
                            "feature_schema": "hash64-v1-public", "l2_norm_max": 1.0},
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "baseline_frozen": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    records = _run_cases()
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    passed = sum(record["status"] == "PASS" for record in records)
    summary = {
        "experiment_id": out_dir.name,
        "qualification_status": "QUALIFIED_OFFLINE" if passed == len(records) else "FAILED_OFFLINE",
        "cases": len(records), "passed": passed,
        "failed": len(records) - passed,
        "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "baseline_frozen": False,
        "records": records,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 scripts/peerrolebench_feature_contextual_qualification.py OUTPUT_DIR")
    result = run(Path(sys.argv[1]))
    print(json.dumps({key: result[key] for key in ("qualification_status", "cases", "passed", "failed")}, ensure_ascii=False))
