"""Qualify the canonical ``raw_acceptance`` channel adapter.

This is an offline adapter qualification.  It first checks the native PIPE3
selection, delivery, judgment and candidate registry identities, then projects
the canonical ``j0`` judgment through :func:`project_raw_acceptance` and only
after that constructs the shared ``MatrixOffer`` stream.  No API, model or GPU
is used.  The result is a protocol gate, not a benchmark result.
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
import time
from dataclasses import replace
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_canonical_pipe3_parity_qualification import (  # noqa: E402
    ARM_NAMES,
    CANDIDATE_KEYS,
    _build_canonical_fixture,
    _digest,
    _registry,
    _run_rejected_cell,
    _stream,
)
from peerrolebench_candidate_registry import registry_digest  # noqa: E402
from peerrolebench_event_time_schedule import schedule_digest  # noqa: E402
from peerrolebench_policy_matrix_runner_v1 import MatrixOffer, PolicyMatrixRunner  # noqa: E402
from peerrolebench_policy_projection import (  # noqa: E402
    RAW_ACCEPTANCE_MAPPING_VERSION,
    RawAcceptanceSidecar,
    project_raw_acceptance,
)
from peerrolebench_policy_sidecar import DecisionSidecar  # noqa: E402


VERSION = "canonical-raw-positive-adapter-v1"
TASK_ID = "PIPE3_stream_processing"
NATIVE_SELECTION_ID = "s0"
POLICY_SELECTION_ID = "policy-s0"
RAW_FEEDBACK_ID = "raw-j0"
ARM_EXPECTED_UPDATE = "raw_acceptance"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _event(fixture: Mapping[str, Any], event_type: str, event_id: str) -> Mapping[str, Any]:
    for event in fixture["ledger"].events:
        if event["event_type"] != event_type:
            continue
        payload = event["payload"]
        id_field = {
            "peer_selection": "selection_id",
            "producer_delivery": "delivery_id",
            "recipient_judgment": "judgment_id",
        }.get(event_type)
        if id_field and str(payload.get(id_field)) == event_id:
            return event
    raise ValueError(f"native event not found: {event_type}/{event_id}")


def _native_preflight(
    fixture: Mapping[str, Any], sidecar: RawAcceptanceSidecar,
    *, expected_registry_digest: str | None = None,
) -> dict[str, Any]:
    """Validate native lineage before any MatrixOffer is constructed."""
    registry = tuple(fixture["registry"])
    actual_registry_digest = registry_digest(registry)
    expected_registry_digest = expected_registry_digest or str(fixture["registry_digest"])
    if actual_registry_digest != expected_registry_digest:
        raise ValueError("candidate registry digest mismatch")
    if actual_registry_digest != str(fixture["role_offer"].candidate_registry_digest):
        raise ValueError("role offer candidate registry digest mismatch")

    selection = _event(fixture, "peer_selection", NATIVE_SELECTION_ID)
    delivery = _event(fixture, "producer_delivery", "d0")
    judgment = _event(fixture, "recipient_judgment", "j0")
    sp, dp, jp = selection["payload"], delivery["payload"], judgment["payload"]
    if tuple(sp["candidate_ids"]) != ("peer-b", "peer-c"):
        raise ValueError("native selection candidate menu mismatch")
    if sp["chosen_peer_id"] != "peer-b":
        raise ValueError("native selection chosen candidate mismatch")
    if dp["selection_id"] != NATIVE_SELECTION_ID or dp["producer_id"] != "peer-b":
        raise ValueError("native delivery selection/producer binding mismatch")
    if jp["delivery_id"] != "d0" or jp["decision"] not in {"accept", "reject"}:
        raise ValueError("native judgment delivery/decision mismatch")
    if jp["observed_artifact_sha256"] != dp["artifact_sha256"]:
        raise ValueError("native judgment artifact digest mismatch")
    if sidecar.protocol_event_id != "j0" or sidecar.delivery_id != "d0":
        raise ValueError("raw sidecar is not bound to native j0/d0")
    if sidecar.ledger_record_hash != judgment["record_hash"]:
        raise ValueError("raw sidecar ledger record digest mismatch")
    if sidecar.producer_id != dp["producer_id"] or sidecar.producer_version != "v1":
        raise ValueError("raw sidecar producer binding mismatch")
    if sidecar.selection_event_id != NATIVE_SELECTION_ID:
        raise ValueError("raw sidecar native selection mismatch")
    if sidecar.source_event_id != POLICY_SELECTION_ID:
        raise ValueError("raw sidecar policy selection binding mismatch")
    candidate_key = f"{sidecar.producer_id}@{sidecar.producer_version}"
    if candidate_key not in CANDIDATE_KEYS:
        raise ValueError("raw sidecar candidate is outside canonical menu")
    return {
        "selection_record_hash": selection["record_hash"],
        "delivery_record_hash": delivery["record_hash"],
        "judgment_record_hash": judgment["record_hash"],
        "candidate_key": candidate_key,
        "registry_digest": actual_registry_digest,
    }


def _selection_sidecar(fixture: Mapping[str, Any]) -> DecisionSidecar:
    selection = _event(fixture, "peer_selection", NATIVE_SELECTION_ID)
    return DecisionSidecar(
        ledger_record_hash=str(selection["record_hash"]),
        protocol_event_type="peer_selection", protocol_event_id=NATIVE_SELECTION_ID,
        task_id=TASK_ID, task_index=0, role="producer", event_id=POLICY_SELECTION_ID,
        selector_id=str(selection["payload"]["selector_id"]), context_key="PIPE3:0",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(0.25, -0.25), chosen_index=0, probabilities=(0.5, 0.5),
        propensity=0.5, state_version="canonical-state-0", encoder_version="canonical-encoder-v1",
        feature_schema="canonical-public-judgment-history-hash64-v2",
        policy_name="raw_acceptance", policy_version="raw-v1", base_score_version="canonical-base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=0.0,
    )


def _raw_sidecar(fixture: Mapping[str, Any], *, decision: str = "accept", **changes: Any) -> RawAcceptanceSidecar:
    judgment = _event(fixture, "recipient_judgment", "j0")
    payload = judgment["payload"]
    values = {
        "ledger_record_hash": str(judgment["record_hash"]),
        "protocol_event_type": "recipient_judgment", "protocol_event_id": "j0",
        "feedback_id": RAW_FEEDBACK_ID, "source_event_id": POLICY_SELECTION_ID,
        "selection_event_id": NATIVE_SELECTION_ID, "delivery_id": "d0",
        "producer_id": "peer-b", "producer_version": "v1",
        "recipient_id": str(payload["consumer_id"]), "decision": decision,
        "label_mapping_version": RAW_ACCEPTANCE_MAPPING_VERSION,
        "mapping_digest": hashlib.sha256(RAW_ACCEPTANCE_MAPPING_VERSION.encode()).hexdigest(),
        "source_index": 5, "arrived_at": 5.0, "delay": 5.0, "arrival_index": 5,
    }
    values.update(changes)
    return RawAcceptanceSidecar(**values)


def _raw_projection_row(fixture: Mapping[str, Any], sidecar: RawAcceptanceSidecar) -> dict[str, Any]:
    selection = _selection_sidecar(fixture)
    judgment = _event(fixture, "recipient_judgment", "j0")
    projected = project_raw_acceptance(sidecar, selection=selection, ledger_record=judgment)
    payload = projected.public_payload()
    payload["_protocol_event_id"] = sidecar.protocol_event_id
    # The projection's mapping version identifies the source channel.  The
    # shared AssignmentEvidenceOffer additionally requires one matrix row
    # schema version across all channels; retain the mapping in the adapter
    # receipt and normalize only this public row field before make_offer.
    payload["evidence_version"] = "matrix-evidence-v1"
    if payload["feedback_id"] != RAW_FEEDBACK_ID or payload["source"] != "raw_acceptance":
        raise ValueError("raw projection identity/source mismatch")
    return payload


def _build_raw_stream(fixture: Mapping[str, Any], sidecars: Sequence[RawAcceptanceSidecar] = (), *, late: bool = False,
                      expected_registry_digest: str | None = None) -> tuple[list[MatrixOffer], tuple[Any, ...], str, dict[str, Any]]:
    if not sidecars:
        sidecars = (_raw_sidecar(fixture),)
    feedback_ids = [item.feedback_id for item in sidecars]
    if len(feedback_ids) != len(set(feedback_ids)):
        raise ValueError("duplicate raw acceptance feedback id")
    native = [_native_preflight(fixture, item, expected_registry_digest=expected_registry_digest) for item in sidecars]
    if len(native) != 1:
        raise ValueError("raw adapter requires exactly one canonical source sidecar")
    if sidecars[0].decision not in {"accept", "reject"}:
        raise ValueError("raw acceptance UNKNOWN has no policy label")
    raw_fixture = dict(fixture)
    raw_fixture["policy_row"] = _raw_projection_row(fixture, sidecars[0])
    offers, schedule, digest = _stream(raw_fixture, late=late)
    runner = PolicyMatrixRunner(registry=fixture["registry"], arm_names=ARM_NAMES)
    by_id = {item.feedback_id: item for item in schedule}
    # Adapter preflight happens before entering PolicyMatrixRunner.run.  This
    # is what gives rejection cells runner_started=false semantics.
    for offer in offers:
        runner._validate_offer(offer, by_id)
    return offers, schedule, digest, native[0]


def _run_positive(fixture: Mapping[str, Any]) -> dict[str, Any]:
    offers, schedule, digest, native = _build_raw_stream(fixture)
    result = PolicyMatrixRunner(registry=fixture["registry"], arm_names=ARM_NAMES).run(
        offers, schedule, expected_schedule_digest=digest,
    )
    metrics = result["metrics"]
    checks = {
        "runner_started": True,
        "raw_one_eligible": metrics[ARM_EXPECTED_UPDATE]["n_eligible"] == 1,
        "raw_one_update": metrics[ARM_EXPECTED_UPDATE]["updates"] == 1,
        "other_arms_ignore_raw": all(
            metrics[name]["n_ignored"] == 1 and metrics[name]["updates"] == 0
            for name in ARM_NAMES if name != ARM_EXPECTED_UPDATE
        ),
        "selected_only": all(metrics[name]["n_unselected"] == 0 for name in ARM_NAMES),
        "revisible_prefix_not_update": all(metrics[name]["n_revisible_prefix_rows"] == 2 for name in ARM_NAMES),
        "same_visible_input_digest": len({
            tuple(result["visible_input_digests"][name]) for name in ARM_NAMES
        }) == 1,
        "state_replay_equal": all(item["snapshot_equal"] for item in result["replay"].values()),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
            "native_preflight": native, "result": result, "schedule_digest": digest}


def _reject(name: str, fn: Any) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        fn()
    except Exception as exc:
        return {
            "cell": name, "status": "INVALID", "runner_started": False,
            "accepted": False, "false_accept": False, "selection_count": 0,
            "policy_update_count": 0, "unknown_reason": f"{type(exc).__name__}: {exc}",
            "wall_ms": round((time.perf_counter() - started) * 1000.0, 6),
        }
    return {
        "cell": name, "status": "FAIL", "runner_started": True,
        "accepted": True, "false_accept": True, "selection_count": None,
        "policy_update_count": None, "unknown_reason": None,
        "wall_ms": round((time.perf_counter() - started) * 1000.0, 6),
    }


def run(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    component_names = (
        "peerrolebench_canonical_raw_adapter_qualification.py",
        "peerrolebench_canonical_pipe3_parity_qualification.py",
        "peerrolebench_policy_matrix_runner_v1.py",
        "peerrolebench_policy_projection.py",
        "peerrolebench_baseline_policies.py",
        "peerrolebench_candidate_registry.py",
    )
    config = {
        "qualification_version": VERSION,
        "kind": "zero_call_canonical_raw_acceptance_source_adapter",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": sys.argv, "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version, "platform": platform.platform(),
        "component_sha256": {name: _sha(ROOT / "scripts" / name) for name in component_names},
        "arms": list(ARM_NAMES), "mapping_version": RAW_ACCEPTANCE_MAPPING_VERSION,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "benchmark_qualified": False, "baseline_parity_scientific": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    fixture = _build_canonical_fixture()
    rows: list[dict[str, Any]] = []
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as raw:
        raw.write(json.dumps({"event_type": "native_preflight_fixture", "payload": {
            "ledger_digest": fixture["ledger_digest"], "registry_digest": fixture["registry_digest"],
            "judgment_id": "j0", "selection_id": NATIVE_SELECTION_ID,
        }}, sort_keys=True) + "\n")
        positive = _run_positive(fixture)
        rows.append({"event_type": "raw_positive", "payload": positive})
        raw.write(json.dumps(rows[-1], default=str, sort_keys=True) + "\n")

        good = _raw_sidecar(fixture)
        cells = [
            # ``reject`` is a valid raw label, but it must still agree with
            # canonical j0 (which is ``accept``); this exercises the ledger
            # binding rather than only the sidecar enum validator.
            ("wrong-decision", lambda: _build_raw_stream(fixture, (_raw_sidecar(fixture, decision="reject"),))),
            ("wrong-producer", lambda: _build_raw_stream(fixture, (_raw_sidecar(fixture, producer_id="peer-c"),))),
            ("wrong-ledger-digest", lambda: _build_raw_stream(fixture, (_raw_sidecar(fixture, ledger_record_hash="0" * 64),))),
            ("wrong-registry-digest", lambda: _build_raw_stream(fixture, (good,), expected_registry_digest="0" * 64)),
            ("duplicate", lambda: _build_raw_stream(fixture, (good, replace(good)))),
            ("unknown", lambda: _build_raw_stream(fixture, (_raw_sidecar(fixture, decision="unknown"),))),
            ("late-after-read-cut", lambda: _build_raw_stream(fixture, (good,), late=True)),
        ]
        for name, fn in cells:
            result = _reject(name, fn)
            rows.append({"event_type": "rejected_cell", "payload": result})
            raw.write(json.dumps(rows[-1], default=str, sort_keys=True) + "\n")
        raw.flush()

    rejected = [item["payload"] for item in rows if item["event_type"] == "rejected_cell"]
    checks = {
        "raw_positive": positive["status"] == "PASS",
        "seven_rejected_cells": len(rejected) == 7,
        "all_rejected_fail_closed": all(
            row["status"] == "INVALID" and row["runner_started"] is False
            and row["selection_count"] == 0 and row["policy_update_count"] == 0
            and row["false_accept"] is False for row in rejected
        ),
    }
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE_SOURCE_ADAPTERS" if all(checks.values()) else "FAILED_OFFLINE",
        "passed": all(checks.values()), "checks": checks,
        "positive": positive, "rejected_cells": rejected,
        "interpretation": (
            "Raw acceptance source adapter and rejection contracts only; zero-call evidence, "
            "with no benchmark, quality, role-learning, cost or scientific effect claim."
        ),
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
