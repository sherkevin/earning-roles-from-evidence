"""Zero-call qualification for the feature-aware PIPE3 two-stage seam.

The runner uses the existing CPU composition with a deliberately injected
deterministic scorer.  It checks that ``contextual_trust_linear`` reaches the
canonical preview -> assignment -> commit path with the same versioned
feature map used by the RARE comparator.  It is an engineering qualification,
not a benchmark or an efficacy experiment; no API, model, or GPU is called.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import FeatureContextualTrustPolicy  # noqa: E402
from peerrolebench_pipe3_two_stage_composition import (  # noqa: E402
    PUBLIC_ENCODER_VERSION, PUBLIC_FEATURE_DIMENSION, PUBLIC_FEATURE_SCHEMA, run,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_status() -> tuple[bool, str]:
    status = subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=ROOT, text=True)
    return not bool(status), hashlib.sha256(status.encode("utf-8")).hexdigest()


def _unit_scorer(kind: str, sources: dict[str, str], info: dict[str, str],
                 out: Path, log: Path, seed: int) -> dict[str, Any]:
    """Deterministic scorer fixture; intentionally not a scientific result."""
    out.mkdir(parents=True, exist_ok=True)
    return {
        "status": "FAIL" if kind == "producer" else "PASS",
        "label": 0 if kind == "producer" else 1,
        "quality_score": 0.0 if kind == "producer" else 0.8,
        "coverage_complete": True,
        "decision_complete": True,
        "scorer_version": "unit-injected-scorer",
        "response_digest": "a" * 64,
    }


def _feature_policy_factory(name: str) -> FeatureContextualTrustPolicy:
    if name != "contextual_trust_linear":
        raise ValueError(f"unexpected policy name={name!r}")
    return FeatureContextualTrustPolicy(
        dimension=PUBLIC_FEATURE_DIMENSION, ridge=1.0, trust_scale=2.0,
        temperature=1.0, exploration=0.0,
        encoder_version=PUBLIC_ENCODER_VERSION, feature_schema=PUBLIC_FEATURE_SCHEMA,
    )


def run_qualification(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    worktree_clean, status_digest = _git_status()
    config = {
        "experiment_id": out_dir.name,
        "kind": "zero_call_pipe3_feature_aware_two_stage_qualification",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_worktree_clean_before": worktree_clean,
        "git_status_porcelain_sha256_before": status_digest,
        "python": platform.python_version(),
        "component_sha256": {
            name: _sha(ROOT / name) for name in (
                "scripts/peerrolebench_pipe3_two_stage_composition.py",
                "scripts/peerrolebench_role_evidence_selection.py",
                "scripts/peerrolebench_pipe3_runner_v1.py",
                "scripts/peerrolebench_baseline_policies.py",
            )
        },
        "candidate_policy": "contextual_trust_linear",
        "reference_policy": "RARE",
        "composition_version": "pipe3-two-stage-composition-v1.8",
        "public_feature_contract": {
            "encoder_version": PUBLIC_ENCODER_VERSION,
            "feature_schema": PUBLIC_FEATURE_SCHEMA,
            "dimension": PUBLIC_FEATURE_DIMENSION,
            "representation": "bounded_one_hot_qualification_only",
        },
        "assignment_contract": "preview->assignment->commit",
        "injected_scorer": "unit_fixture_only",
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "baseline_frozen": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = run(
        out_dir / "composition", scorer=_unit_scorer,
        policy_factory=_feature_policy_factory,
        policy_name="contextual_trust_linear",
    )
    producer = next(case for case in result["cases"] if case.get("control") == "producer_owned")
    raw_rows = [json.loads(line) for line in
                (out_dir / "composition" / "producer_owned" / "raw.jsonl").read_text(encoding="utf-8").splitlines()]
    feature_receipts = [row["payload"] for row in raw_rows if row["event"] == "selection_feature_contract"]
    sidecar_receipts = [row["payload"] for row in raw_rows
                        if row["event"] in {"source_selection_sidecar", "target_selection_sidecar"}]
    feature_digest = feature_receipts[0].get("feature_digest") if feature_receipts else None
    summary = {
        **config,
        "qualification_status": "QUALIFIED_OFFLINE" if result.get("status") == "QUALIFIED_OFFLINE" else "UNKNOWN",
        "composition_status": result.get("status"),
        "controls": len(result.get("cases", [])),
        "contract_passed": result.get("contract_passed") is True,
        "producer_policy_updates": producer.get("policy_updates"),
        "producer_feedback_contract_ok": producer.get("feedback_contract_ok"),
        "feature_receipt_count": len(feature_receipts),
        "selection_sidecar_receipt_count": len(sidecar_receipts),
        "feature_contract_complete": bool(
            len(feature_receipts) == 1
            and feature_receipts[0].get("encoder_version") == PUBLIC_ENCODER_VERSION
            and feature_receipts[0].get("feature_schema") == PUBLIC_FEATURE_SCHEMA
            and all(len(values) == PUBLIC_FEATURE_DIMENSION
                    for values in feature_receipts[0].get("captured_features", {}).values())
        ),
        "selection_sidecar_contract_complete": bool(
            len(sidecar_receipts) == 2
            and all(row.get("feature_digest") == feature_digest
                    and row.get("payload", {}).get("encoder_version") == PUBLIC_ENCODER_VERSION
                    and row.get("payload", {}).get("feature_schema") == PUBLIC_FEATURE_SCHEMA
                    and row.get("payload", {}).get("captured_features") == feature_receipts[0].get("captured_features")
                    and row.get("sidecar_digest")
                    for row in sidecar_receipts)
        ),
        "raw_composition_summary": result,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 scripts/peerrolebench_pipe3_feature_composition_qualification.py OUTPUT_DIR")
    receipt = run_qualification(Path(sys.argv[1]))
    print(json.dumps({key: receipt[key] for key in (
        "qualification_status", "composition_status", "contract_passed",
        "feature_contract_complete", "real_api_calls", "gpu_jobs",
    )}, ensure_ascii=False))
