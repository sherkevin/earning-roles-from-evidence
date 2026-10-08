"""Zero-call qualification for pre-selection evidence consumption."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import math

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_assignment_attestation import (  # noqa: E402
    AssignmentEvidenceOffer,
    _digest,
    build_consumption_attestation,
    verify_consumption_attestation,
)
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_policy_sidecar import DecisionSidecar  # noqa: E402


DIGEST = "a" * 64


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _decision(**overrides) -> DecisionSidecar:
    values = {
        "ledger_record_hash": DIGEST, "protocol_event_type": "peer_selection",
        "protocol_event_id": "s0", "task_id": "task", "task_index": 0,
        "role": "producer", "event_id": "e0", "selector_id": "selector",
        "context_key": "ctx",
        "candidates": (CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        "base_scores": (0.2, 0.8), "chosen_index": 1,
        "probabilities": (0.5, 0.5), "propensity": 0.5,
        "state_version": "state-1", "encoder_version": "enc-1",
        "feature_schema": "phi-1", "policy_name": "contextual_trust",
        "policy_version": "v1", "base_score_version": "base-1",
        "rng_algorithm": "rng", "rng_draw": 0, "selected_at": 10.0,
        "state_digest": "b" * 64,
    }
    values.update(overrides)
    return DecisionSidecar(**values)


def _offer(**overrides) -> AssignmentEvidenceOffer:
    row = {
        "feedback_id": "f0", "source_event_id": "e0", "source": "recipient_judgment",
        "candidate_key": "peer-b@v1", "evidence_version": "ev-v1", "source_index": 0,
        "arrival_index": 2, "arrived_at": 4.0, "delay": 1.0, "action": "repair",
        "disposition": "eligible", "provenance": "public", "label": 1.0,
    }
    values = {
        "offer_id": "offer-0", "offer_record_hash": DIGEST, "task_id": "task", "task_index": 0,
        "role": "producer", "context_key": "ctx", "candidate_keys": ("peer-a@v1", "peer-b@v1"),
        "evidence_ids": ("e0",), "evidence_version": "ev-v1", "public_rows": (row,),
        "available_index": 2, "watermark_schema": "global-event-index-v1",
    }
    values.update(overrides)
    payload = {
        "offer_id": values["offer_id"], "task_id": values["task_id"],
        "task_index": values["task_index"], "role": values["role"],
        "context_key": values["context_key"], "candidate_keys": list(values["candidate_keys"]),
        "evidence_ids": list(values["evidence_ids"]), "evidence_version": values["evidence_version"],
        "public_rows": [dict(item) for item in values["public_rows"]],
        "available_index": values["available_index"], "watermark_schema": values["watermark_schema"],
    }
    values["bundle_digest"] = _digest(payload)
    return AssignmentEvidenceOffer(**values)


def _reject(rows: list[dict], case: str, fn, expected: str | None = None) -> None:
    try:
        fn()
    except ValueError as exc:
        rows.append({"case": case, "passed": expected is None or expected in str(exc), "error": str(exc)})
    else:
        rows.append({"case": case, "passed": False, "error": "accepted mutation"})


def _toy_policy_output(offer: AssignmentEvidenceOffer, *, consumed: bool) -> tuple[float, float]:
    """Fixed-menu, fixed-temperature adapter used only for seam sensitivity."""
    signal = 0.0
    if consumed:
        signal = sum(float(row["label"]) for row in offer.public_rows
                     if row["candidate_key"] == "peer-b@v1" and row["disposition"] == "eligible"
                     and row["provenance"] == "public")
    score = max(-30.0, min(30.0, signal))
    exp_score = math.exp(score)
    return (1.0 / (1.0 + exp_score), exp_score / (1.0 + exp_score))


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "experiment_id": "n03_assignment_attestation_qualification_20260928_v2",
        "kind": "zero_call_assignment_evidence_consumption_attestation",
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(),
                    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    "source_sha256": {
                        "attestation": _sha256(ROOT / "scripts/peerrolebench_assignment_attestation.py"),
                        "qualification": _sha256(Path(__file__)),
                    }},
        "watermark_schema": "global-event-index-v1",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    ev, dec = _offer(), _decision()
    rows: list[dict] = []
    att = build_consumption_attestation(ev, dec, consumed=True, read_cut=2, decision_index=3)
    rows.append({"case": "consumed_before_selection", "passed": verify_consumption_attestation(att, ev, dec),
                 "public_digest": ev.public_bundle_digest, "decision_state_digest": dec.state_digest})
    changed = _offer(public_rows=({**ev.public_rows[0], "label": 0.0},))
    f0 = build_consumption_attestation(ev, dec, consumed=False, read_cut=2, decision_index=3)
    f0_changed = build_consumption_attestation(changed, dec, consumed=False, read_cut=2, decision_index=3)
    f1 = build_consumption_attestation(ev, dec, consumed=True, read_cut=2, decision_index=3)
    f1_changed = build_consumption_attestation(changed, dec, consumed=True, read_cut=2, decision_index=3)
    rows.append({"case": "f0_invariance", "passed": verify_consumption_attestation(f0, ev, dec) is False
                 and verify_consumption_attestation(f0_changed, changed, dec) is False
                 and f0.policy_input_digest == f0_changed.policy_input_digest
                 and _toy_policy_output(ev, consumed=False) == _toy_policy_output(changed, consumed=False)})
    rows.append({"case": "f1_public_sensitivity", "passed": f1.policy_input_digest != f1_changed.policy_input_digest
                 and _toy_policy_output(ev, consumed=True) != _toy_policy_output(changed, consumed=True)})
    rows.append({"case": "operator_hash_noninterference", "passed": _offer(offer_record_hash="d" * 64).bundle_digest == ev.bundle_digest})
    empty = _offer(evidence_ids=(), public_rows=())
    empty_att = build_consumption_attestation(empty, dec, consumed=True, read_cut=2, decision_index=3)
    rows.append({"case": "empty_cold_start_offer", "passed": verify_consumption_attestation(empty_att, empty, dec)})

    _reject(rows, "private_row", lambda: _offer(public_rows=({**ev.public_rows[0], "raw_value": "secret"},)), "private or unknown")
    _reject(rows, "future_offer", lambda: build_consumption_attestation(_offer(available_index=4), dec, consumed=True, read_cut=2, decision_index=3), "unavailable")
    _reject(rows, "menu_mismatch", lambda: build_consumption_attestation(_offer(candidate_keys=("peer-b@v1", "peer-a@v1")), dec, consumed=True, read_cut=2, decision_index=3), "candidate menu")
    _reject(rows, "context_mismatch", lambda: build_consumption_attestation(_offer(context_key="other"), dec, consumed=True, read_cut=2, decision_index=3), "context")
    _reject(rows, "missing_state_digest", lambda: build_consumption_attestation(ev, _decision(state_digest=None), consumed=True, read_cut=2, decision_index=3), "state digest")
    _reject(rows, "decision_mismatch", lambda: verify_consumption_attestation(att, ev, _decision(event_id="other")), "decision mismatch")
    _reject(rows, "late_feedback_unknown", lambda: build_consumption_attestation(_offer(available_index=5), dec, consumed=True, read_cut=3, decision_index=3), "unavailable")

    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    passed = all(row["passed"] for row in rows) and len(rows) == 12
    summary = {
        "experiment_id": config["experiment_id"], "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed, "case_count": len(rows), "cases": rows,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "interpretation": "schema_and_behavioral_sensitivity_only",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"passed": result["passed"], "status": result["status"],
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
