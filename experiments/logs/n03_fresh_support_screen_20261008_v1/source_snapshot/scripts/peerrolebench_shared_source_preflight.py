#!/usr/bin/env python3
"""Parent-side shared-source preflight for future live policy arms.

The preflight is intentionally separate from the policy runner.  It verifies a
source manifest once, projects the exact receipt into independent arm
namespaces, and emits a cost ledger in which source acquisition is counted once.
It does not execute an agent, scorer, selector, or GPU job.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_shared_source_v2 import (  # noqa: E402
    ARM_NAMES,
    freeze_source_receipt,
    project_source_to_arms,
    validate_arm_projections,
    validate_selection_binding,
)


VERSION = "shared-source-parent-preflight-v1"


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def load_manifest(path: Path, expected_source_digest: str) -> tuple[dict[str, Any], str]:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    if bundle.get("manifest_version") != "peerrolebench-external-source-manifest-v1":
        raise ValueError("unsupported external source manifest version")
    expected = expected_source_digest
    receipt = bundle.get("source_receipt")
    if not isinstance(expected, str) or not isinstance(receipt, Mapping):
        raise ValueError("external expected_source_digest and source_receipt are required")
    if bundle.get("expected_source_digest") not in {None, expected}:
        raise ValueError("manifest co-located digest disagrees with external digest")
    if bundle.get("scientific_claim_allowed") is not False:
        raise ValueError("source preflight cannot enable scientific claims")
    lineage = receipt.get("source_lineage", {})
    binding = receipt.get("source_selection_binding")
    if lineage.get("candidate_registry_digest") != receipt.get("provenance", {}).get("registry_digest"):
        raise ValueError("source lineage registry digest disagrees with provenance")
    if not isinstance(binding, Mapping):
        raise ValueError("source selection binding is required")
    validate_selection_binding(binding)
    if binding.get("binding_digest") != lineage.get("selection_binding_digest"):
        raise ValueError("source selection binding digest is not bound to lineage")
    if binding.get("native_selection_id") != lineage.get("selection_id"):
        raise ValueError("source selection binding does not match source lineage")
    if binding.get("chosen_candidate") != lineage.get("selected_candidate"):
        raise ValueError("source selection binding candidate disagrees with lineage")
    frozen = freeze_source_receipt(receipt, expected)
    return frozen, expected


def prepare_shared_source(
    path: Path,
    expected_source_digest: str,
    arms: Iterable[str] = ARM_NAMES,
) -> dict[str, Any]:
    receipt, expected = load_manifest(path, expected_source_digest)
    projections = project_source_to_arms(receipt, expected, arms)
    validation = validate_arm_projections(projections, expected)
    lineage = receipt["source_lineage"]
    if receipt["source_event_id"] != f"{lineage['selection_id']}:source":
        raise ValueError("source_event_id must exactly retain selection lineage")
    return {
        "preflight_version": VERSION,
        "manifest_path": str(path),
        "source_receipt_digest": expected,
        "source_event_id": receipt["source_event_id"],
        "source_lineage": lineage,
        "arms": list(validation["arms"]),
        "projections": projections,
        "validation": validation,
        "cost_ledger": validation["cost_ledger"],
        "scientific_claim_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-source-digest", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepared = prepare_shared_source(args.manifest.resolve(), args.expected_source_digest)
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)
    config = {
        "version": VERSION,
        "manifest": str(args.manifest.resolve()),
        "arms": prepared["arms"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    (output / "projections.json").write_text(json.dumps(prepared, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "raw.jsonl").write_text(json.dumps({"event_type": "shared_source_preflight", "payload": {
        "source_receipt_digest": prepared["source_receipt_digest"],
        "arms": prepared["arms"],
        "cost_ledger": prepared["cost_ledger"],
    }}, sort_keys=True) + "\n", encoding="utf-8")
    cost_status = prepared["cost_ledger"].get("source_cost_status")
    summary = {
        "version": VERSION,
        "status": (
            "QUALIFIED_OFFLINE"
            if cost_status == "COMPLETE"
            else "QUALIFIED_OFFLINE_COST_UNKNOWN"
        ),
        "cost_measurement_status": cost_status,
        "source_receipt_digest": prepared["source_receipt_digest"],
        "projection_digest": _digest(prepared["projections"]),
        "cost_ledger": prepared["cost_ledger"],
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
