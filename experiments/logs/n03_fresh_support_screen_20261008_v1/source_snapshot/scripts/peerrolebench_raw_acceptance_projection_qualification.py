"""Zero-call qualification of the independent raw-acceptance projection.

This checks only the public projection seam.  The hand-authored judgment
records are not a benchmark sample, and no LLM, GPU, scorer, or live runner is
used.  A later PIPE3 runner must replace these records with canonical runtime
events and retain the same rejection cases.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import CandidateRef, RawAcceptancePolicy  # noqa: E402
from peerrolebench_policy_projection import (  # noqa: E402
    RAW_ACCEPTANCE_MAPPING_VERSION,
    RawAcceptanceSidecar,
    project_raw_acceptance,
)
from peerrolebench_policy_sidecar import DecisionSidecar  # noqa: E402


DIGEST = "a" * 64


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selection() -> DecisionSidecar:
    return DecisionSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="peer_selection", protocol_event_id="s0",
        task_id="PIPE3_stream_processing", task_index=0, role="producer", event_id="e0",
        selector_id="selector", context_key="ctx", candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(0.2, 0.8), chosen_index=1, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="state", encoder_version="enc", feature_schema="phi",
        policy_name="raw_acceptance", policy_version="raw-v1", base_score_version="base",
        rng_algorithm="rng", rng_draw=0, selected_at=1.0,
    )


def _sidecar(decision: str = "accept", *, producer_id: str = "peer-b") -> RawAcceptanceSidecar:
    return RawAcceptanceSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="recipient_judgment", protocol_event_id="j0",
        feedback_id=f"raw-{decision}", source_event_id="e0", selection_event_id="s0",
        delivery_id="d0", producer_id=producer_id, producer_version="v1", recipient_id="peer-a",
        decision=decision, label_mapping_version=RAW_ACCEPTANCE_MAPPING_VERSION,
        mapping_digest=DIGEST, source_index=5, arrived_at=12.0, delay=2.0,
    )


def _record(decision: str = "accept") -> dict:
    return {
        "record_hash": DIGEST,
        "event_type": "recipient_judgment",
        "payload": {"judgment_id": "j0", "delivery_id": "d0", "consumer_id": "peer-a", "decision": decision},
    }


def _case(rows: list[dict], name: str, fn, *, expect_error: str | None = None) -> None:
    try:
        result = fn()
    except ValueError as exc:
        rows.append({"case": name, "passed": expect_error is not None and expect_error in str(exc), "error": str(exc)})
    else:
        rows.append({"case": name, "passed": expect_error is None, "result": result})


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "experiment_id": "n03_raw_acceptance_projection_20260929_v1",
        "kind": "zero_call_public_projection_contract_not_scientific_benchmark",
        "mapping_version": RAW_ACCEPTANCE_MAPPING_VERSION,
        "cases": ["accept", "reject", "canonical_label_mutation", "rework_rejected", "unchosen_candidate", "public_boundary"],
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "projection_sha256": _sha256(ROOT / "scripts/peerrolebench_policy_projection.py"),
            "qualification_sha256": _sha256(Path(__file__).resolve()),
        },
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    chosen = _selection()
    rows: list[dict] = []
    for decision in ("accept", "reject"):
        projection = project_raw_acceptance(_sidecar(decision), selection=chosen, ledger_record=_record(decision))
        policy = RawAcceptancePolicy()
        policy.ingest_selection(chosen.to_selection())
        changed = policy.observe_feedback(projection.to_feedback())
        payload = projection.public_payload()
        rows.append({
            "case": decision, "passed": changed and projection.source == "raw_acceptance"
            and projection.to_feedback().label == (1.0 if decision == "accept" else 0.0)
            and all(key not in payload for key in ("responsibility_status", "attribution_basis", "gate_digest", "weight")),
            "label": projection.to_feedback().label, "policy_updates": policy.updates,
            "public_keys": sorted(payload),
        })

    _case(rows, "canonical_label_mutation", lambda: project_raw_acceptance(
        _sidecar("accept"), selection=chosen, ledger_record=_record("reject")), expect_error="canonical judgment")
    _case(rows, "rework_rejected", lambda: _sidecar("rework"), expect_error="accept or reject")
    _case(rows, "unchosen_candidate", lambda: project_raw_acceptance(
        _sidecar("accept", producer_id="peer-a"), selection=chosen, ledger_record=_record("accept")), expect_error="selected candidate")
    _case(rows, "selection_binding", lambda: project_raw_acceptance(
        _sidecar("accept"), selection=DecisionSidecar(
            ledger_record_hash=DIGEST, protocol_event_type="peer_selection", protocol_event_id="other",
            task_id="task", task_index=0, role="producer", event_id="e0", selector_id="selector",
            context_key="ctx", candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
            base_scores=(0.2, 0.8), chosen_index=1, probabilities=(0.5, 0.5), propensity=0.5,
            state_version="state", encoder_version="enc", feature_schema="phi", policy_name="raw_acceptance",
            policy_version="raw-v1", base_score_version="base", rng_algorithm="rng", rng_draw=0, selected_at=1.0,
        ), ledger_record=_record("accept")), expect_error="selection does not match")

    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    passed = len(rows) == 6 and all(row["passed"] for row in rows)
    summary = {
        "experiment_id": config["experiment_id"], "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed, "case_count": len(rows), "cases": rows,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"passed": result["passed"], "status": result["status"], "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
