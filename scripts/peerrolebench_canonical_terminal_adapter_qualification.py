"""Zero-call qualification for the canonical terminal-only PIPE3 channel.

The positive cell feeds one native ``TerminalOutcome`` through the independent
terminal projection and then replays the frozen offer stream through all seven
policy arms.  Negative cells are preflight mutations.  They must fail before a
``MatrixOffer`` is constructed or a policy runner starts.  This is an adapter
qualification artifact, not a benchmark result.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_canonical_pipe3_parity_qualification import (  # noqa: E402
    ARM_NAMES, CANDIDATE_KEYS, PHI_VERSION, TARGET_READ_CUT,
    _build_canonical_fixture, _offer, _digest,
)
from peerrolebench_policy_sidecar import DecisionSidecar  # noqa: E402
from peerrolebench_terminal_outcome_projection import (  # noqa: E402
    TERMINAL_LABEL_MAPPING_DIGEST, TERMINAL_LABEL_MAPPING_VERSION,
    TerminalOutcomeProjection, TerminalOutcomeSidecar,
    project_terminal_outcome,
)
from peerrolebench_policy_matrix_runner_v1 import MatrixOffer, PolicyMatrixRunner  # noqa: E402


VERSION = "canonical-terminal-only-public-input-v1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(fixture: Mapping[str, Any], event_type: str, event_id: str | None = None) -> dict[str, Any]:
    for event in fixture["ledger"].events:
        if event["event_type"] != event_type:
            continue
        if event_id is None or event["payload"].get({
            "peer_selection": "selection_id", "producer_delivery": "delivery_id",
            "terminal_outcome": "outcome_id",
        }.get(event_type, "")) == event_id:
            return event
    raise AssertionError(f"missing native ledger event {event_type} {event_id}")


def _selection_sidecar(fixture: Mapping[str, Any]) -> tuple[DecisionSidecar, dict[str, Any]]:
    record = _record(fixture, "peer_selection", "s0")
    selection = DecisionSidecar(
        ledger_record_hash=record["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id="s0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", event_id="policy-s0", selector_id="peer-selector",
        context_key="PIPE3:0",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(0.25, -0.25), chosen_index=0, probabilities=(0.5, 0.5),
        propensity=0.5, state_version="state-0", encoder_version="enc-terminal-v1",
        feature_schema=PHI_VERSION, policy_name="fixture", policy_version="v1",
        base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0,
    )
    return selection, record


def _terminal_sidecar(
    fixture: Mapping[str, Any], selection: DecisionSidecar,
    *, success: bool | None = True,
    **overrides: Any,
) -> tuple[TerminalOutcomeSidecar, dict[str, Any], dict[str, Any]]:
    outcome_record = _record(fixture, "terminal_outcome", "o0")
    delivery_record = _record(fixture, "producer_delivery", "d0")
    values: dict[str, Any] = {
        "ledger_record_hash": outcome_record["record_hash"],
        "protocol_event_type": "terminal_outcome", "protocol_event_id": "o0",
        "feedback_id": "terminal-feedback-o0", "source_event_id": selection.event_id,
        "selection_event_id": selection.protocol_event_id, "delivery_id": "d0",
        "delivery_record_hash": delivery_record["record_hash"],
        "producer_id": "peer-b", "producer_version": "v1", "success": success,
        "label_mapping_version": TERMINAL_LABEL_MAPPING_VERSION,
        "mapping_digest": TERMINAL_LABEL_MAPPING_DIGEST,
        "source_index": 0, "arrived_at": 5.0, "delay": 5.0,
        "disposition": "eligible", "provenance": "public", "action": "use",
        "arrival_index": 5,
    }
    values.update(overrides)
    return TerminalOutcomeSidecar(**values), outcome_record, delivery_record


def _public_row(projection: TerminalOutcomeProjection, protocol_event_id: str) -> dict[str, Any]:
    row = projection.public_payload()
    row.update({
        # MatrixOffer has its own frozen public row schema.  The terminal
        # mapping remains bound in the sidecar/projection evidence_version;
        # this adapter field only satisfies the downstream offer envelope.
        "evidence_version": "matrix-evidence-v1",
        "source_index": int(projection.source_index),
        "_protocol_event_id": protocol_event_id,
    })
    return row


def _terminal_stream(
    fixture: Mapping[str, Any], row: Mapping[str, Any],
) -> tuple[list[MatrixOffer], tuple[Any, ...], str]:
    common = {
        "candidate_keys": CANDIDATE_KEYS,
        "public_rows": (dict(row),), "available_index": 5,
        "base_scores": (0.25, -0.25), "feature_schema": PHI_VERSION,
        "protocol_event_ids": {str(row["feedback_id"]): str(row["_protocol_event_id"])},
    }
    first = _offer(
        offer_id="terminal-stream-0", task_index=0, candidate_keys=CANDIDATE_KEYS,
        public_rows=(), available_index=0, native_selection_id="s0", read_cut=0,
        decision_index=0, selected_at=0.0, rng_seed=11, context_key="PIPE3:0",
        base_scores=(0.25, -0.25), feature_schema=PHI_VERSION,
    )
    second = _offer(
        offer_id="terminal-stream-1", task_index=1, native_selection_id="s1",
        read_cut=5, decision_index=5, selected_at=5.0, rng_seed=12,
        context_key="PIPE3:1", **common,
    )
    third = _offer(
        offer_id="terminal-stream-2", task_index=2, native_selection_id="s2",
        read_cut=TARGET_READ_CUT, decision_index=TARGET_READ_CUT,
        selected_at=float(TARGET_READ_CUT), rng_seed=13, context_key="PIPE3:2",
        **common,
    )
    fourth = _offer(
        offer_id="terminal-stream-3", task_index=3, native_selection_id="s3",
        read_cut=TARGET_READ_CUT, decision_index=TARGET_READ_CUT + 1,
        selected_at=float(TARGET_READ_CUT + 1), rng_seed=14, context_key="PIPE3:3",
        **common,
    )
    offers = [
        replace(first, selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][0]),
        replace(second, selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][5]),
        replace(third, selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][TARGET_READ_CUT]),
        replace(fourth, selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][TARGET_READ_CUT]),
    ]
    from peerrolebench_event_time_schedule import ArrivalAssignment, schedule_digest
    schedule = (ArrivalAssignment(
        feedback_id=str(row["feedback_id"]), protocol_event_type="terminal_outcome",
        protocol_event_id=str(row["_protocol_event_id"]), source_event_id=str(row["source_event_id"]),
        arrival_index=int(row["arrival_index"]),
    ),)
    return offers, schedule, schedule_digest(schedule)


class TerminalOnlyAdapter:
    """Preflight terminal sidecars before constructing any MatrixOffer."""

    def __init__(self) -> None:
        self._seen_feedback: set[str] = set()
        self.runner_started = False

    def preflight(
        self,
        entries: Sequence[tuple[TerminalOutcomeSidecar, Mapping[str, Any], Mapping[str, Any]]],
        *, selection: DecisionSidecar, read_cut: int,
    ) -> list[TerminalOutcomeProjection]:
        projections: list[TerminalOutcomeProjection] = []
        local_seen: set[str] = set()
        for sidecar, outcome_record, delivery_record in entries:
            if sidecar.feedback_id in self._seen_feedback or sidecar.feedback_id in local_seen:
                raise ValueError("duplicate terminal feedback id")
            projection = project_terminal_outcome(
                sidecar, selection=selection, outcome_record=outcome_record,
                delivery_record=delivery_record, read_cut=read_cut,
            )
            local_seen.add(sidecar.feedback_id)
            projections.append(projection)
        self._seen_feedback.update(local_seen)
        return projections


def _positive(fixture: Mapping[str, Any]) -> dict[str, Any]:
    selection, _ = _selection_sidecar(fixture)
    sidecar, outcome, delivery = _terminal_sidecar(fixture, selection)
    adapter = TerminalOnlyAdapter()
    projection = adapter.preflight(((sidecar, outcome, delivery),), selection=selection, read_cut=5)[0]
    row = _public_row(projection, sidecar.protocol_event_id)
    offers, schedule, digest = _terminal_stream(fixture, row)
    # The adapter's preflight has completed before the runner is marked as
    # started and receives its first MatrixOffer.
    adapter.runner_started = True
    result = PolicyMatrixRunner(registry=fixture["registry"], arm_names=ARM_NAMES).run(
        offers, schedule, expected_schedule_digest=digest,
    )
    metrics = result["metrics"]
    checks = {
        "terminal_only_one_eligible": metrics["terminal_only"]["n_eligible"] == 1,
        "terminal_only_one_update": metrics["terminal_only"]["updates"] == 1,
        "other_arms_ignore_terminal": all(
            metrics[name]["n_ignored"] == 1 and metrics[name]["updates"] == 0
            for name in ARM_NAMES if name != "terminal_only"
        ),
        "seven_arm_public_input_digests_equal": len({
            tuple(result["visible_input_digests"][name]) for name in ARM_NAMES
        }) == 1,
        "snapshot_replay_equal": all(item["snapshot_equal"] for item in result["replay"].values()),
        "no_private_terminal_fields": not ({"scorer_version", "score_payload_sha256", "success"}
            & set(projection.public_payload())),
        "runner_started_after_preflight": adapter.runner_started is True,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
        "projection": projection.public_payload(), "sidecar": sidecar.payload(),
        "result": result,
    }


def _negative_case(
    name: str, fixture: Mapping[str, Any], selection: DecisionSidecar,
    sidecar: TerminalOutcomeSidecar, outcome: Mapping[str, Any], delivery: Mapping[str, Any],
    *, read_cut: int = 5, second: TerminalOutcomeSidecar | None = None,
) -> dict[str, Any]:
    adapter = TerminalOnlyAdapter()
    entries = [(sidecar, outcome, delivery)]
    if second is not None:
        entries.append((second, outcome, delivery))
    try:
        adapter.preflight(entries, selection=selection, read_cut=read_cut)
    except Exception as exc:
        return {
            "case": name, "status": "PASS", "accepted": False,
            "error_type": type(exc).__name__, "error": str(exc),
            "runner_started": adapter.runner_started, "selection_count": 0,
            "policy_update_count": 0,
        }
    return {
        "case": name, "status": "FAIL", "accepted": True,
        "error_type": None, "error": None,
        "runner_started": adapter.runner_started, "selection_count": None,
        "policy_update_count": None,
    }


def run(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    script_path = Path(__file__).resolve()
    component_names = (
        "peerrolebench_canonical_terminal_adapter_qualification.py",
        "peerrolebench_terminal_outcome_projection.py",
        "peerrolebench_canonical_pipe3_parity_qualification.py",
        "peerrolebench_policy_matrix_runner_v1.py",
    )
    config = {
        "qualification_version": VERSION,
        "kind": "zero_call_canonical_terminal_only_adapter",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": sys.argv, "git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        ).strip(),
        "python": sys.version, "platform": platform.platform(),
        "component_sha256": {name: _sha(ROOT / "scripts" / name) for name in component_names},
        "arms": list(ARM_NAMES), "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "benchmark_qualified": False,
        "baseline_parity_scientific": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fixture = _build_canonical_fixture()
    selection, _ = _selection_sidecar(fixture)
    valid_sidecar, outcome, delivery = _terminal_sidecar(fixture, selection)
    negatives: list[dict[str, Any]] = []
    mutations = {
        "wrong_outcome_hash": ("replace", {"ledger_record_hash": "f" * 64}, {}),
        "wrong_delivery": ("replace", {"delivery_id": "d1"}, {}),
        "wrong_delivery_hash": ("replace", {"delivery_record_hash": "f" * 64}, {}),
        "wrong_selection": ("replace", {"selection_event_id": "s1"}, {}),
        "wrong_candidate": ("replace", {"producer_id": "peer-c"}, {}),
        # This mapping is rejected by the sidecar constructor itself.  Keep
        # that failure in the negative cell instead of constructing an
        # invalid object and accidentally calling the matrix runner.
        "wrong_label_mapping": ("replace", {
            "label_mapping_version": "terminal-success-v2", "mapping_digest": "a" * 64,
        }, {}),
        "unknown": ("replace", {"success": None, "disposition": "unknown", "provenance": "unknown"}, {}),
        "late": ("replace", {"arrival_index": 99}, {"read_cut": 5}),
    }
    for name, (operation, changes, kwargs) in mutations.items():
        try:
            sidecar = replace(valid_sidecar, **changes) if operation == "replace" else valid_sidecar
            negatives.append(_negative_case(
                name, fixture, selection, sidecar, outcome, delivery, **kwargs,
            ))
        except Exception as exc:
            negatives.append({
                "case": name, "status": "PASS", "accepted": False,
                "error_type": type(exc).__name__, "error": str(exc),
                "runner_started": False, "selection_count": 0, "policy_update_count": 0,
            })
    duplicate = replace(valid_sidecar, feedback_id=valid_sidecar.feedback_id)
    negatives.append(_negative_case(
        "duplicate", fixture, selection, valid_sidecar, outcome, delivery, second=duplicate,
    ))
    positive = _positive(fixture)
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as raw:
        raw.write(json.dumps({"event_type": "terminal_fixture", "payload": {
            "ledger_digest": fixture["ledger_digest"],
            "selection": selection.payload(), "delivery": delivery,
            "outcome": outcome,
        }}, ensure_ascii=False, default=str) + "\n")
        raw.write(json.dumps({"event_type": "positive", "payload": positive}, ensure_ascii=False, default=str) + "\n")
        for case in negatives:
            raw.write(json.dumps({"event_type": "negative", "payload": case}, ensure_ascii=False, default=str) + "\n")
    passed = positive["status"] == "PASS" and all(
        case["status"] == "PASS" and case["accepted"] is False
        and case["runner_started"] is False and case["selection_count"] == 0
        and case["policy_update_count"] == 0 for case in negatives
    )
    summary = {
        **config, "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed, "positive": {
            "status": positive["status"], "checks": positive["checks"],
        }, "negative": negatives, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
