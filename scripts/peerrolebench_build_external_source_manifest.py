#!/usr/bin/env python3
"""Build an external shared-source manifest from one completed source episode.

This utility is deliberately a preparation step, not a benchmark scorer.  It
reads one already recorded episode, constructs a source-only receipt outside
the policy-arm loop, computes the canonical digest, and immediately validates
the receipt with the shared-source v2 contract.  A future live runner must run
this parent-owned phase before any arm policy executes and must pass the
resulting digest into each arm; this script does not reclassify the historical
run as scientific evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_shared_source_v2 import (
    canonical_source_digest,
    freeze_source_receipt,
    validate_selection_binding,
)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def _file_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sorted(x for x in path.rglob("*") if x.is_file()):
        data = item.read_bytes()
        rows.append({
            "path": str(item.relative_to(path)),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
    return rows


def _json_digest(path: Path) -> str:
    return _digest(json.loads(path.read_text(encoding="utf-8")))


def _response_digest(decision_dir: Path, patterns: tuple[str, ...]) -> str:
    files = []
    for pattern in patterns:
        files.extend(decision_dir.rglob(pattern))
    manifest = []
    for item in sorted(set(files)):
        if item.is_file():
            data = item.read_bytes()
            manifest.append({
                "path": str(item.relative_to(decision_dir)),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            })
    return _digest(manifest)


def _api_cost(api: Mapping[str, Any] | None) -> dict[str, Any]:
    api = api if isinstance(api, Mapping) else {}
    usage = api.get("usage") if isinstance(api.get("usage"), Mapping) else {}
    return {
        "input_tokens": int(usage.get("input_tokens", 0) or 0),
        "output_tokens": int(usage.get("output_tokens", 0) or 0),
        "wall_seconds": float(api.get("elapsed_seconds", 0.0) or 0.0),
        "usage_complete": bool(api.get("usage_complete", False)),
        "http_status": api.get("http_status"),
    }


def _measured_api(meta: Mapping[str, Any]) -> bool:
    """Whether one API receipt has enough metadata to count as observed cost."""
    return (
        bool(meta.get("usage_complete"))
        and isinstance(meta.get("http_status"), (int, str))
        and str(meta.get("http_status")) == "200"
        and math.isfinite(float(meta.get("wall_seconds", 0.0)))
        and float(meta.get("wall_seconds", 0.0)) >= 0.0
    )


def build_source_receipt(run_dir: Path, arm: str, decision_index: int, manifest_id: str) -> dict[str, Any]:
    if int(decision_index) != 0:
        raise ValueError("external source manifests may only be built from decision_index=0")
    arm_dir = run_dir / arm
    summary = json.loads((arm_dir / "summary.json").read_text(encoding="utf-8"))
    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    registry = json.loads((arm_dir / "candidate_registry.json").read_text(encoding="utf-8"))
    selection_bindings = json.loads((arm_dir / "selection_bindings.json").read_text(encoding="utf-8"))
    source_key = "source" if decision_index == 0 else "target"
    source = summary[source_key]
    decision_dir = arm_dir / f"decision_{decision_index}"
    if not decision_dir.is_dir():
        raise FileNotFoundError(f"missing decision directory: {decision_dir}")

    material_manifest = arm_dir / "material_manifest.json"
    raw_path = arm_dir / "raw.jsonl"
    contract_digest = _json_digest(material_manifest)
    registry_digest = registry.get("digest")
    if not isinstance(registry_digest, str):
        raise ValueError("candidate registry has no digest")
    source_binding = next(
        (row for row in selection_bindings if row.get("native_selection_id") == source["selection_id"]),
        None,
    )
    if source_binding is None:
        raise ValueError("source selection binding is missing")
    validate_selection_binding(source_binding)
    if source_binding["chosen_candidate"] != source["selected_key"]:
        raise ValueError("source selection binding chose a different candidate")
    if source_binding["candidate_registry_digest"] != registry_digest:
        raise ValueError("source selection binding registry digest disagrees")

    producer_score = source["producer_score"]
    recipient_score = source.get("recipient_score", {})
    adoption_score = source.get("adoption_score", {})
    scorer_digest = _digest({
        "producer": producer_score,
        "recipient": recipient_score,
        "adoption": adoption_score,
        "outcome": source["outcome"],
    })
    prompt_digest = _response_digest(decision_dir, ("*_request.json",))
    raw_response_digest = _response_digest(
        decision_dir, ("*_response.sse", "*_parsed_response.json", "response.json")
    )
    artifact_digest = source["artifact_digest"]
    provenance = {
        "policy_invariant": True,
        "artifact_digest": artifact_digest,
        "contract_digest": contract_digest,
        "registry_digest": registry_digest,
        "scorer_digest": scorer_digest,
        "prompt_digest": prompt_digest,
        "raw_response_digest": raw_response_digest,
        "provenance_scope": "source-only decision directory and immutable parent material manifest",
    }

    judgment_api = _api_cost(source.get("judgment_api"))
    action_api = _api_cost(source.get("action_api"))
    producer_scorer_seconds = float(producer_score.get("scorer_wall_seconds", 0.0) or 0.0)
    recipient_scorer_seconds = float(recipient_score.get("scorer_wall_seconds", 0.0) or 0.0)
    adoption_scorer_seconds = float(adoption_score.get("scorer_wall_seconds", 0.0) or 0.0)
    outcome_scorer_seconds = float(source.get("outcome", {}).get("scorer_wall_seconds", 0.0) or 0.0)
    action_seconds = float(source.get("action", {}).get("action_wall_seconds", 0.0) or 0.0)
    source_cost_units = (
        judgment_api["wall_seconds"] + action_api["wall_seconds"] + action_seconds
        + producer_scorer_seconds + (
            outcome_scorer_seconds
            if outcome_scorer_seconds > 0.0 or "scorer_wall_seconds" in source.get("outcome", {})
            else recipient_scorer_seconds + adoption_scorer_seconds
        )
    )
    producer_wall_complete = (
        isinstance(producer_score, Mapping)
        and isinstance(producer_score.get("scorer_wall_seconds"), (int, float))
        and math.isfinite(float(producer_score.get("scorer_wall_seconds")))
        and float(producer_score.get("scorer_wall_seconds")) >= 0.0
    )
    outcome_total_complete = (
        isinstance(source.get("outcome"), Mapping)
        and isinstance(source["outcome"].get("scorer_wall_seconds"), (int, float))
        and math.isfinite(float(source["outcome"].get("scorer_wall_seconds")))
        and float(source["outcome"].get("scorer_wall_seconds")) >= 0.0
    )
    independent_outcome_complete = all(
        isinstance(score, Mapping)
        and isinstance(score.get("scorer_wall_seconds"), (int, float))
        and math.isfinite(float(score.get("scorer_wall_seconds")))
        and float(score.get("scorer_wall_seconds")) >= 0.0
        for score in (recipient_score, adoption_score)
    )
    score_labels_complete = all(
        isinstance(score, Mapping) and score.get("status") in {"PASS", "FAIL"}
        for score in (producer_score, recipient_score, adoption_score)
    )
    scorer_complete = score_labels_complete and producer_wall_complete and (
        outcome_total_complete or independent_outcome_complete
    )
    action_complete = (
        isinstance(source.get("action"), Mapping)
        and isinstance(source["action"].get("action_wall_seconds"), (int, float))
        and math.isfinite(float(source["action"].get("action_wall_seconds")))
        and float(source["action"].get("action_wall_seconds")) >= 0.0
    )
    cost_status = "COMPLETE" if (
        _measured_api(judgment_api) and _measured_api(action_api)
        and scorer_complete and action_complete
    ) else "UNKNOWN"
    source_event_id = f"{source['selection_id']}:source"
    cost = {
        "source_cost_id": source_event_id,
        "source_cost_units": source_cost_units,
        "target_cost_units": 0.0,
        "unit": "wall_seconds_sum_source_only_with_explicit_measurement_status",
        "api": {"judgment": judgment_api, "action": action_api},
        "scorer_wall_seconds": {
            "producer": producer_scorer_seconds,
            "recipient": recipient_scorer_seconds,
            "adoption": adoption_scorer_seconds,
            "outcome_total": outcome_scorer_seconds,
        },
        "action_wall_seconds": action_seconds,
        "cost_status": cost_status,
        "source_cost_units_observed": cost_status == "COMPLETE",
        "source_cost_units_semantics": (
            "measured_wall_seconds_sum_for_source_only_receipt"
            if cost_status == "COMPLETE"
            else "lower_bound_wall_seconds_sum_missing_usage_or_stage_receipt"
        ),
    }

    raw_gate_status = source["source_gate"].get("status")
    if raw_gate_status == "ELIGIBLE":
        gate_status = "ELIGIBLE"
        episode_status = "SOURCE_COMPLETE"
        source_complete = True
        estimand_inclusion = "ITT_AND_ELIGIBLE"
    elif raw_gate_status == "PENDING_ATTRIBUTION":
        gate_status = "PENDING_ATTRIBUTION"
        episode_status = "STOPPED_PRE_TARGET"
        source_complete = True
        estimand_inclusion = "ITT_ONLY"
    else:
        # An incomplete scorer/transport event is the only source state that
        # can enter v2 as UNKNOWN.  A complete but unattributable event should
        # remain PENDING_ATTRIBUTION; callers must not turn it into a missing
        # observation by inspecting only evidence_publish_allowed.
        gate_status = "UNKNOWN"
        episode_status = "SOURCE_INCOMPLETE"
        source_complete = False
        estimand_inclusion = "ITT_ONLY"
    source_payload: dict[str, Any] = {
        "source_event_id": source_event_id,
        "task_id": config.get("task_id", source.get("task_id", "PIPE3_stream_processing")),
        "root": config.get("task_id", "PIPE3_stream_processing"),
        "seed": int(config.get("seed", 0)),
        "source_lineage": {
            "selection_id": source["selection_id"],
            "delivery_id": source["delivery_id"],
            "selected_candidate": source["selected_key"],
            "decision_index": int(source.get("decision_index", decision_index)),
            "candidate_registry_digest": registry_digest,
            "selection_binding_digest": source_binding["binding_digest"],
            "card_sha256": config.get("card_sha256"),
            "source_commit": config.get("source_commit"),
            "runner_version": config.get("version"),
            "source_root": config.get("task_id", "PIPE3_stream_processing"),
        },
        "source_selection_binding": source_binding,
        "delivery_digest": artifact_digest,
        "judgment": source["judgment"],
        "action": source["action"],
        "producer_score": producer_score,
        "outcome": source["outcome"],
        "gate": source["source_gate"],
        "cost": cost,
        "episode_status": episode_status,
        "gate_status": gate_status,
        "estimand_inclusion": estimand_inclusion,
        "source_complete": source_complete,
        "target_started": False,
        "target_status": "NOT_STARTED",
        "provenance": provenance,
        "source_seal": {
            "manifest_id": manifest_id,
            "source_digest": "",
            "parent_run": str(run_dir),
            "arm_observed": arm,
            "decision_index": decision_index,
        },
        "source_receipt_digest": "",
    }
    digest = canonical_source_digest(source_payload)
    source_payload["source_seal"]["source_digest"] = digest
    source_payload["source_receipt_digest"] = digest
    return source_payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--arm", required=True)
    parser.add_argument("--decision-index", type=int, default=0)
    parser.add_argument("--manifest-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_source_receipt(args.run_dir.resolve(), args.arm, args.decision_index, args.manifest_id)
    expected = receipt["source_receipt_digest"]
    validated = freeze_source_receipt(receipt, expected)
    out = args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "manifest_version": "peerrolebench-external-source-manifest-v1",
        "manifest_id": args.manifest_id,
        "expected_source_digest": expected,
        "source_receipt": validated,
        "scientific_claim_allowed": False,
        "historical_conversion": True,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "source_digest": expected, "validated": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
