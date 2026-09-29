"""Offline root-level parity runner for the candidate policy matrix.

This runner deliberately uses hand-authored offers and no model calls.  It is
the smallest executable contract for checking that every policy arm receives
the same menu, RNG seed, event-time schedule and selected-only evidence before
the real PIPE3 runner is attempted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Mapping, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import (  # noqa: E402
    BaselinePolicy,
    CandidateRef,
    Feedback,
    Selection,
    policy_from_name,
)
from peerrolebench_candidate_registry import (  # noqa: E402
    CandidateRegistryEntry,
    registry_digest,
    validate_registry,
)
from peerrolebench_event_time_schedule import (  # noqa: E402
    ArrivalAssignment,
    schedule_digest,
    validate_schedule,
)
from peerrolebench_pipe3_runner_v1 import make_offer  # noqa: E402


ARM_NAMES = (
    "uniform", "no_update", "raw_acceptance", "terminal_only",
    "contextual_trust", "pooled_controller", "RARE",
)
COST_FIELDS = (
    "producer", "recipient", "judge", "scorer", "retry",
    "communication", "repair", "replay",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class MatrixOffer:
    offer: Any
    native_selection_id: str
    selector_id: str
    role: str
    base_scores: tuple[float, ...]
    captured_features: Mapping[str, Sequence[float]]
    read_cut: int
    decision_index: int
    selected_at: float
    rng_seed: int
    protocol_event_ids: Mapping[str, str]


def _registry() -> tuple[CandidateRegistryEntry, ...]:
    return tuple(
        CandidateRegistryEntry(
            candidate_id=name, candidate_version="v1", source_digest=name[0] * 64,
            model_id="internal/model", model_config_digest="c" * 64,
        )
        for name in ("agent-a", "agent-b", "agent-c")
    )


def _features(candidate_keys: Sequence[str]) -> dict[str, tuple[float, ...]]:
    values: dict[str, tuple[float, ...]] = {}
    for index, key in enumerate(candidate_keys):
        vector = [0.0] * 64
        vector[index % 64] = 1.0
        values[str(key)] = tuple(vector)
    return values


def _row(
    *, feedback_id: str, source_event_id: str, protocol_event_id: str,
    source: str, candidate_key: str, arrival_index: int,
    label: float | None, disposition: str = "eligible",
    provenance: str = "public", action: str = "accept",
    supersedes: str | None = None, unknown_reason: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "feedback_id": feedback_id, "source_event_id": source_event_id,
        "source": source, "candidate_key": candidate_key,
        "evidence_version": "matrix-evidence-v1", "source_index": arrival_index - 1,
        "arrival_index": arrival_index, "arrived_at": float(arrival_index),
        "delay": float(arrival_index), "action": action,
        "disposition": disposition, "provenance": provenance,
    }
    if label is not None:
        row["label"] = float(label)
    if supersedes is not None:
        row["supersedes"] = supersedes
    if unknown_reason is not None:
        row["unknown_reason"] = unknown_reason
    # Operator-side schedule identity.  It is removed before the row enters
    # the public offer and retained only in MatrixOffer for schedule binding.
    row["_protocol_event_id"] = protocol_event_id
    return row


def _offer(
    *, offer_id: str, task_index: int, candidate_keys: tuple[str, ...],
    public_rows: Sequence[Mapping[str, Any]], available_index: int,
    native_selection_id: str, read_cut: int, decision_index: int,
    selected_at: float, rng_seed: int,
    protocol_event_ids: Mapping[str, str] | None = None,
) -> MatrixOffer:
    raw_rows = [dict(row) for row in public_rows]
    derived_event_ids = {
        str(row["feedback_id"]): str(row.pop("_protocol_event_id"))
        for row in raw_rows if "_protocol_event_id" in row
    }
    event_ids_input = dict(protocol_event_ids or {})
    if derived_event_ids:
        if event_ids_input and event_ids_input != derived_event_ids:
            raise ValueError("protocol event IDs disagree between row and offer binding")
        event_ids_input = derived_event_ids
    offer = make_offer(
        offer_id=offer_id, task_id="PIPE3_stream_processing", task_index=task_index,
        role="producer", context_key=f"PIPE3:{task_index}",
        candidate_keys=candidate_keys, public_rows=raw_rows,
        evidence_version="matrix-evidence-v1", available_index=available_index,
    )
    row_ids = {str(row["feedback_id"]) for row in raw_rows}
    event_ids = {str(key): str(value) for key, value in event_ids_input.items()}
    if set(event_ids) != row_ids:
        raise ValueError("protocol event IDs must cover exactly the public feedback rows")
    return MatrixOffer(
        offer=offer, native_selection_id=native_selection_id, selector_id="agent-a",
        role="producer", base_scores=(0.0,) * len(candidate_keys),
        captured_features=_features(candidate_keys), read_cut=read_cut,
        decision_index=decision_index, selected_at=selected_at, rng_seed=rng_seed,
        protocol_event_ids=event_ids,
    )


class PolicyMatrixRunner:
    """Run all policy arms over one frozen, selected-only offer stream."""

    def __init__(self, *, registry: Sequence[CandidateRegistryEntry], arm_names: Sequence[str] = ARM_NAMES):
        self.registry = validate_registry(registry)
        self.arm_names = tuple(arm_names)
        unknown = set(self.arm_names) - set(ARM_NAMES)
        if unknown:
            raise ValueError(f"unsupported matrix arms={sorted(unknown)}")

    @staticmethod
    def _validate_offer(offer: MatrixOffer, schedule: Mapping[str, ArrivalAssignment]) -> None:
        if offer.read_cut > offer.decision_index:
            raise ValueError("read_cut is after decision_index")
        if offer.offer.available_index > offer.read_cut:
            raise ValueError("offer is unavailable at read_cut")
        for row in offer.offer.public_rows:
            feedback_id = str(row["feedback_id"])
            assignment = schedule.get(feedback_id)
            if assignment is None:
                raise ValueError(f"offer contains feedback outside frozen schedule: {feedback_id}")
            if int(row["arrival_index"]) != assignment.arrival_index:
                raise ValueError(f"offer arrival index disagrees with schedule: {feedback_id}")
            if offer.protocol_event_ids.get(feedback_id) != assignment.protocol_event_id:
                raise ValueError(f"offer protocol event disagrees with schedule: {feedback_id}")
            if str(row["source"]) != assignment.protocol_event_type:
                raise ValueError(f"offer protocol event type disagrees with schedule: {feedback_id}")
            if str(row["source_event_id"]) != assignment.source_event_id:
                raise ValueError(f"offer source event disagrees with schedule: {feedback_id}")
            if assignment.arrival_index > offer.read_cut:
                raise ValueError("future feedback was offered before the decision read cut")
            if row.get("disposition") != "eligible" or row.get("provenance") != "public":
                if not row.get("unknown_reason"):
                    raise ValueError("UNKNOWN evidence must carry an explicit reason")

    @staticmethod
    def _cost_ledger() -> dict[str, dict[str, Any]]:
        return {
            field: {"value": 0.0, "measured": False, "source": "offline_fixture"}
            for field in COST_FIELDS
        }

    def run(
        self,
        offers: Sequence[MatrixOffer],
        schedule_rows: Sequence[ArrivalAssignment | Mapping[str, Any]],
        *,
        expected_schedule_digest: str,
        expected_registry_digest: str | None = None,
    ) -> dict[str, Any]:
        actual_registry_digest = registry_digest(self.registry)
        if expected_registry_digest is not None and actual_registry_digest != expected_registry_digest:
            raise ValueError("frozen candidate registry digest mismatch")
        feedback_ids = [str(row["feedback_id"]) for item in offers for row in item.offer.public_rows]
        schedule = validate_schedule(schedule_rows, expected_feedback_ids=set(feedback_ids))
        if schedule_digest(schedule) != expected_schedule_digest:
            raise ValueError("frozen arrival schedule digest mismatch")
        schedule_by_id = {row.feedback_id: row for row in schedule}
        registered_keys = {entry.key for entry in self.registry}
        policies = {name: policy_from_name(name, exploration=0.10) for name in self.arm_names}
        traces: dict[str, list[dict[str, Any]]] = {name: [] for name in self.arm_names}
        metrics = {
            name: {"n_selected": 0, "n_eligible": 0, "n_unknown": 0,
                   "n_duplicate": 0, "n_ignored": 0, "n_unsupported_correction": 0,
                   "n_unselected": 0,
                   "updates": 0, "unknown_reasons": {}}
            for name in self.arm_names
        }
        seen_offer_ids: set[str] = set()
        seen_selection_ids: set[str] = set()
        seen_decision_indices: set[int] = set()
        previous_decision_index = -1
        previous_read_cut = -1
        previous_selected_at = float("-inf")
        for item in offers:
            self._validate_offer(item, schedule_by_id)
            unknown_keys = set(item.offer.candidate_keys) - registered_keys
            if unknown_keys:
                raise ValueError(f"offer contains unregistered candidate keys: {sorted(unknown_keys)}")
            if item.offer.offer_id in seen_offer_ids:
                raise ValueError(f"duplicate offer_id={item.offer.offer_id}")
            seen_offer_ids.add(item.offer.offer_id)
            if item.native_selection_id in seen_selection_ids:
                raise ValueError(f"duplicate native selection id={item.native_selection_id}")
            if item.decision_index in seen_decision_indices:
                raise ValueError(f"duplicate decision index={item.decision_index}")
            if item.decision_index <= previous_decision_index:
                raise ValueError("decision indices must be strictly increasing")
            if item.read_cut < previous_read_cut:
                raise ValueError("read cuts must be non-decreasing")
            if float(item.selected_at) < previous_selected_at:
                raise ValueError("selected_at must be non-decreasing")
            seen_selection_ids.add(item.native_selection_id)
            seen_decision_indices.add(item.decision_index)
            previous_decision_index = item.decision_index
            previous_read_cut = item.read_cut
            previous_selected_at = float(item.selected_at)
            refs = tuple(CandidateRef(*key.rsplit("@", 1)) for key in item.offer.candidate_keys)
            for name, policy in policies.items():
                before_seen = set(policy._seen_feedback)
                before_updates = policy.updates
                selection = policy.choose(
                    event_id=f"policy-{item.native_selection_id}",
                    context_key=item.offer.context_key, selector_id=item.selector_id,
                    candidates=refs, base_scores=item.base_scores,
                    rng=np.random.default_rng(item.rng_seed), state_version=f"state-{item.decision_index}",
                    encoder_version="hash64-v1", feature_schema="matrix-features-v1",
                    selected_at=item.selected_at, captured_features=item.captured_features,
                )
                metrics[name]["n_selected"] += 1
                trace = {
                    "offer_id": item.offer.offer_id,
                    "decision_index": item.decision_index,
                    "visible_fields": [
                        "context_key", "candidate_menu", "base_scores", "state_version",
                        "encoder_version", "feature_schema", "captured_features",
                        "public_feedback_rows_at_read_cut",
                    ],
                    "chosen_key": selection.chosen.key,
                    "probabilities": list(selection.probabilities),
                    "propensity": selection.propensity,
                    "feedback": [],
                }
                for row in item.offer.public_rows:
                    feedback_id = str(row["feedback_id"])
                    source_selection = policy._decisions.get(str(row["source_event_id"]))
                    if source_selection is None:
                        raise ValueError("feedback references an unknown source selection")
                    if row["candidate_key"] != source_selection.chosen.key:
                        metrics[name]["n_unselected"] += 1
                        trace["feedback"].append({
                            "feedback_id": feedback_id, "disposition": "unselected",
                            "selected_key": source_selection.chosen.key,
                        })
                        continue
                    if feedback_id in before_seen:
                        metrics[name]["n_duplicate"] += 1
                        trace["feedback"].append({"feedback_id": feedback_id, "disposition": "duplicate"})
                        continue
                    if row["disposition"] != "eligible" or row["provenance"] != "public":
                        metrics[name]["n_unknown"] += 1
                        reason = str(row.get("unknown_reason", "unspecified"))
                        reasons = metrics[name]["unknown_reasons"]
                        reasons[reason] = int(reasons.get(reason, 0)) + 1
                        trace["feedback"].append({"feedback_id": feedback_id, "disposition": "unknown", "reason": reason})
                        continue
                    source = str(row["source"])
                    if source not in policy.accepted_sources:
                        metrics[name]["n_ignored"] += 1
                        trace["feedback"].append({"feedback_id": feedback_id, "disposition": "ignored", "source": source})
                        continue
                    supersedes = row.get("supersedes")
                    if supersedes is not None and name != "RARE":
                        metrics[name]["n_unsupported_correction"] += 1
                    feedback = Feedback(
                        feedback_id=feedback_id, source_event_id=str(row["source_event_id"]),
                        source=source, label=float(row["label"]), arrived_at=float(row["arrived_at"]),
                        delay=float(row["delay"]), action=str(row["action"]),
                        disposition="eligible", provenance="public",
                        arrival_index=int(row["arrival_index"]),
                        supersedes=None if supersedes is None else str(supersedes),
                    )
                    changed = policy.observe_feedback(feedback)
                    metrics[name]["n_eligible"] += 1
                    trace["feedback"].append({
                        "feedback_id": feedback_id, "disposition": "eligible",
                        "changed": bool(changed), "source": source,
                    })
                metrics[name]["updates"] += policy.updates - before_updates
                traces[name].append(trace)
        replay = {}
        for name, policy in policies.items():
            snapshot = policy.snapshot()
            restored = BaselinePolicy.restore(snapshot)
            replay[name] = {"snapshot_equal": restored.snapshot() == snapshot}
        return {
            "status": "PASS", "arms": list(self.arm_names),
            "registry_digest": actual_registry_digest,
            "schedule_digest": expected_schedule_digest,
            "metrics": metrics, "traces": traces,
            "replay": replay, "cost_ledger": self._cost_ledger(),
            "scientific_claim_allowed": False,
        }


def fixture_case(case: str) -> tuple[list[MatrixOffer], tuple[ArrivalAssignment, ...], str]:
    """Return a diagnostic stream; labels are fixture annotations only."""
    candidate_keys = ("agent-b@v1", "agent-c@v1")
    first = _offer(
        offer_id=f"{case}-offer-0", task_index=0, candidate_keys=candidate_keys,
        public_rows=(), available_index=0, native_selection_id="selection-0",
        read_cut=0, decision_index=0, selected_at=0.0, rng_seed=11,
    )
    chosen = candidate_keys[0]
    rows: list[dict[str, Any]] = []
    if case == "recipient_only":
        rows = [_row(feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="j0",
                     source="recipient_judgment", candidate_key=chosen, arrival_index=1, label=1.0)]
    elif case == "producer_defect":
        rows = [_row(feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="j0",
                     source="recipient_judgment", candidate_key=chosen, arrival_index=1, label=0.0,
                     action="repair")]
    elif case == "terminal":
        rows = [_row(feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="o0",
                     source="terminal_outcome", candidate_key=chosen, arrival_index=1, label=1.0,
                     action="use")]
    elif case == "unknown_late_correction":
        rows = [
            _row(feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="j0",
                 source="recipient_judgment", candidate_key=chosen, arrival_index=1, label=1.0),
            _row(feedback_id="f0-correction", source_event_id="policy-selection-0", protocol_event_id="j1",
                 source="recipient_judgment", candidate_key=chosen, arrival_index=3, label=0.0,
                 action="reject", supersedes="f0"),
        ]
    elif case == "unknown":
        rows = [_row(feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="j0",
                     source="recipient_judgment", candidate_key=chosen, arrival_index=1, label=None,
                     disposition="unknown", provenance="unknown", unknown_reason="scorer_timeout")]
    elif case == "unselected":
        rows = [_row(feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="j0",
                     source="recipient_judgment", candidate_key="agent-c@v1", arrival_index=1, label=1.0)]
    else:
        raise ValueError(f"unknown fixture case={case!r}")
    offers = [first]
    if rows:
        offers.append(_offer(
            offer_id=f"{case}-offer-1", task_index=1, candidate_keys=candidate_keys,
        public_rows=(rows[0],), available_index=int(rows[0]["arrival_index"]),
        native_selection_id="selection-1", read_cut=int(rows[0]["arrival_index"]),
            decision_index=1, selected_at=1.0, rng_seed=12,
            protocol_event_ids={str(rows[0]["feedback_id"]): str(rows[0]["_protocol_event_id"])},
        ))
    if len(rows) > 1:
        offers.append(_offer(
            offer_id=f"{case}-offer-2", task_index=2, candidate_keys=candidate_keys,
            public_rows=(rows[1],), available_index=int(rows[1]["arrival_index"]),
            native_selection_id="selection-2", read_cut=int(rows[1]["arrival_index"]),
            decision_index=3, selected_at=3.0, rng_seed=13,
            protocol_event_ids={str(rows[1]["feedback_id"]): str(rows[1]["_protocol_event_id"])},
        ))
    schedule_rows = tuple(
        ArrivalAssignment(
            feedback_id=str(row["feedback_id"]), protocol_event_type=str(row["source"]),
            protocol_event_id=str(row["_protocol_event_id"]), source_event_id=str(row["source_event_id"]),
            arrival_index=int(row["arrival_index"]),
        ) for row in rows
    )
    return offers, schedule_rows, schedule_digest(schedule_rows)


def _semantic_pass(case: str, result: Mapping[str, Any]) -> bool:
    metrics = result["metrics"]
    if case in {"recipient_only", "producer_defect"}:
        return (
            metrics["contextual_trust"]["n_eligible"] == 1
            and metrics["pooled_controller"]["n_eligible"] == 1
            and metrics["RARE"]["n_eligible"] == 1
            and all(metrics[name]["n_ignored"] == 1 for name in ("uniform", "no_update", "raw_acceptance", "terminal_only"))
        )
    if case == "terminal":
        return (
            metrics["terminal_only"]["n_eligible"] == 1
            and metrics["terminal_only"]["updates"] == 1
            and all(metrics[name]["n_ignored"] == 1 for name in ("uniform", "no_update", "raw_acceptance", "contextual_trust", "pooled_controller", "RARE"))
        )
    if case == "unknown_late_correction":
        return (
            metrics["RARE"]["n_eligible"] == 2
            and metrics["RARE"]["updates"] == 2
            and metrics["contextual_trust"]["n_unsupported_correction"] == 1
            and metrics["pooled_controller"]["n_unsupported_correction"] == 1
        )
    if case == "unknown":
        return all(
            metrics[name]["n_unknown"] == 1 and metrics[name]["updates"] == 0
            for name in ARM_NAMES
        )
    if case == "unselected":
        return all(
            metrics[name]["n_unselected"] == 1
            and metrics[name]["n_eligible"] == 0
            and metrics[name]["updates"] == 0
            for name in ARM_NAMES
        )
    return False


def run_fixture_suite(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=False)
    case_names = ["recipient_only", "producer_defect", "terminal", "unknown_late_correction", "unknown", "unselected"]
    fixture_specs = {case: fixture_case(case) for case in case_names}
    config = {
        "experiment_id": out_dir.name,
        "kind": "zero_llm_root_policy_matrix_parity_qualification",
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": {name: _sha(ROOT / name) for name in (
                "scripts/peerrolebench_policy_matrix_runner_v1.py",
                "scripts/peerrolebench_baseline_policies.py",
                "scripts/peerrolebench_event_time_schedule.py",
                "scripts/peerrolebench_assignment_attestation.py",
            )},
        },
        "cases": case_names,
        "arrival_schedules": {
            case: {
                "rows": [row.payload() for row in schedule],
                "digest": digest,
            }
            for case, (_, schedule, digest) in fixture_specs.items()
        },
        "candidate_registry": [entry.payload() for entry in _registry()],
        "registry_digest": registry_digest(_registry()),
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    cases = {}
    try:
        registry = _registry()
        for case in config["cases"]:
            offers, schedule, digest = fixture_specs[case]
            cases[case] = PolicyMatrixRunner(registry=registry).run(
                offers, schedule, expected_schedule_digest=digest,
                expected_registry_digest=config["registry_digest"],
            )
    except Exception as exc:
        failure = {
            "experiment_id": config["experiment_id"], "status": "FAILED_OFFLINE",
            "passed": False, "error_type": type(exc).__name__, "error": str(exc),
            "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
            "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        (out_dir / "failure.json").write_text(json.dumps(failure, indent=2) + "\n")
        (out_dir / "summary.json").write_text(json.dumps(failure, indent=2) + "\n")
        return failure
    (out_dir / "raw_output.json").write_text(json.dumps(cases, indent=2) + "\n")
    passed = all(
        result["status"] == "PASS"
        and all(item["snapshot_equal"] for item in result["replay"].values())
        and _semantic_pass(case, result)
        and all(result["metrics"][name]["n_selected"] == len(fixture_case(case)[0])
                for name in ARM_NAMES)
        for case, result in cases.items()
    )
    summary = {
        "experiment_id": config["experiment_id"], "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed, "case_count": len(cases), "results": {
            case: {"status": result["status"], "metrics": result["metrics"], "replay": result["replay"]}
            for case, result in cases.items()
        }, "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run_fixture_suite(args.out_dir)
    print(json.dumps({"status": result["status"], "passed": result["passed"],
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
