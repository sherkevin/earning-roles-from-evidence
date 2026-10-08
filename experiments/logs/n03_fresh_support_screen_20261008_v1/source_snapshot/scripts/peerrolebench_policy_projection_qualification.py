"""Zero-call qualification for the operator-to-policy projection seam.

This records an engineering boundary only. It does not qualify a scorer,
runner, benchmark, or scientific effect: all objects are hand-authored and no
LLM, GPU, or remote service is used.
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

from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, _digest, project_feedback  # noqa: E402
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar  # noqa: E402


DIGEST = "a" * 64


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sidecar(**overrides) -> FeedbackSidecar:
    values = {
        "ledger_record_hash": DIGEST,
        "protocol_event_type": "recipient_judgment",
        "protocol_event_id": "j0",
        "feedback_id": "f0",
        "source_event_id": "e0",
        "selection_event_id": "s0",
        "delivery_id": "d0",
        "producer_id": "peer-b",
        "producer_version": "v1",
        "recipient_id": "peer-a",
        "source": "recipient_judgment",
        "arrived_at": 12.0,
        "delay": 2.0,
        "action": "repair",
        "disposition": "eligible",
        "provenance": "public",
        "label_mapping_version": "judgment-v1",
        "mapping_digest": DIGEST,
        "responsibility_status": "attributed",
        "attribution_basis": "producer-contract-v1",
        "raw_value": "accept_with_rework",
        "label": 0.5,
    }
    values.update(overrides)
    return FeedbackSidecar(**values)


def _selection() -> DecisionSidecar:
    return DecisionSidecar(
        ledger_record_hash=DIGEST, protocol_event_type="peer_selection", protocol_event_id="s0",
        task_id="task", task_index=0, role="producer", event_id="e0", selector_id="selector",
        context_key="ctx", candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(0.2, 0.8), chosen_index=1, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="state", encoder_version="enc", feature_schema="phi",
        policy_name="no_update", policy_version="v1", base_score_version="base",
        rng_algorithm="rng", rng_draw=0, selected_at=1.0,
    )


def _gate(*, sidecar_obj=None, **overrides) -> AttributionGate:
    bound = sidecar_obj or _sidecar()
    values = {
        "gate_version": "gate-v1",
        "ledger_record_hash": bound.ledger_record_hash,
        "sidecar_digest": bound.sidecar_digest,
        "protocol_event_type": bound.protocol_event_type,
        "protocol_event_id": bound.protocol_event_id,
        "source_event_id": bound.source_event_id,
        "delivery_id": bound.delivery_id,
        "producer_id": bound.producer_id,
        "producer_version": bound.producer_version,
        "recipient_id": bound.recipient_id,
        "selection_event_id": bound.selection_event_id,
        "eligible": True,
        "weight": 1.0,
        "label": bound.label,
        "label_mapping_version": bound.label_mapping_version,
        "evidence_version": "evidence-v1",
        "source_index": 5,
    }
    values.update(overrides)
    payload = {key: values[key] for key in (
        "gate_version", "ledger_record_hash", "sidecar_digest", "protocol_event_type",
        "protocol_event_id", "source_event_id", "delivery_id", "producer_id",
        "producer_version", "recipient_id", "selection_event_id", "eligible", "weight",
        "label", "label_mapping_version", "evidence_version", "source_index",
    )}
    values["gate_digest"] = _digest(payload)
    return AttributionGate(**values)


def _reject(rows: list[dict], case: str, fn, expected: str | None = None) -> None:
    try:
        fn()
    except ValueError as exc:
        rows.append({"case": case, "passed": expected is None or expected in str(exc), "error": str(exc)})
    else:
        rows.append({"case": case, "passed": False, "error": "accepted mutation"})


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    config = {
        "experiment_id": "n03_policy_projection_qualification_20260928_v6",
        "kind": "zero_call_typed_operator_to_policy_projection",
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "git_commit": commit,
                    "source_sha256": {
                        "projection": _sha256(ROOT / "scripts/peerrolebench_policy_projection.py"),
                        "qualification": _sha256(Path(__file__)),
                    }},
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "mutation_cases": ["eligible_minimal", "ineligible_unknown", "non_public_promotion",
                            "delivery_mismatch", "producer_mismatch", "mapping_mismatch",
                            "label_mismatch", "cross_event_identity", "unchosen_candidate",
                            "private_label", "missing_eligible_label", "non_finite_time"],
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    rows: list[dict] = []
    chosen = _selection()
    public = _sidecar()
    eligible = project_feedback(public, _gate(), selection=chosen)
    public_payload = eligible.public_payload()
    rows.append({"case": "eligible_minimal", "passed": eligible.to_feedback() is not None,
                 "public_keys": sorted(public_payload),
                 "private_keys_absent": all(name not in public_payload for name in (
                     "raw_value", "responsibility_status", "attribution_basis", "mapping_digest",
                     "gate_digest", "producer_score_status", "weight"))})

    unknown = _sidecar(disposition="unknown", provenance="unknown", raw_value=None, label=None)
    unknown_projection = project_feedback(unknown, _gate(sidecar_obj=unknown, eligible=False, weight=None, label=None), selection=chosen)
    rows.append({"case": "ineligible_unknown", "passed": unknown_projection.to_feedback() is None,
                 "disposition": unknown_projection.disposition})

    _reject(rows, "non_public_promotion", lambda: project_feedback(unknown, _gate(sidecar_obj=unknown, label=0.5), selection=chosen), "non-public sidecar")
    for case, changes, message in (
        ("delivery_mismatch", {"delivery_id": "other"}, "delivery mismatch"),
        ("producer_mismatch", {"producer_id": "peer-c"}, "producer mismatch"),
        ("producer_version_mismatch", {"producer_version": "v2"}, "producer mismatch"),
    ):
        _reject(rows, case, lambda changes=changes: project_feedback(public, _gate(**changes), selection=chosen), message)
    _reject(rows, "mapping_mismatch", lambda: project_feedback(public, _gate(label_mapping_version="judgment-v2"), selection=chosen), "label mapping mismatch")
    _reject(rows, "label_mismatch", lambda: project_feedback(public, _gate(label=1.0), selection=chosen), "label mismatch")

    for field in ("protocol_event_type", "protocol_event_id", "source_event_id", "recipient_id",
                  "ledger_record_hash", "selection_event_id"):
        mutation = {"protocol_event_type": "terminal_outcome", "ledger_record_hash": "c" * 64}.get(field, "other")
        mutated = _sidecar(**{field: mutation})
        _reject(rows, f"cross_event_identity:{field}", lambda mutated=mutated: project_feedback(mutated, _gate(), selection=chosen))
    unchosen = _sidecar(producer_id="peer-a")
    _reject(rows, "unchosen_candidate", lambda: project_feedback(unchosen, _gate(sidecar_obj=unchosen, producer_id="peer-a"), selection=chosen), "selected candidate")
    _reject(rows, "private_label", lambda: _gate(eligible=False, weight=1.0, label=None), "cannot carry policy label")
    _reject(rows, "missing_eligible_label", lambda: _gate(label=None), "eligible gate requires label")
    _reject(rows, "non_finite_time", lambda: project_feedback(_sidecar(arrived_at=float("nan")), _gate(), selection=chosen), "finite")

    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    passed = all(row["passed"] for row in rows) and len(rows) == 18
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
    print(json.dumps({"passed": result["passed"], "status": result["status"],
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
