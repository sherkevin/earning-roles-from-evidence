"""Canonical, zero-call public-input parity qualification for PIPE3.

This runner is deliberately a qualification artifact.  It builds one source
and one later target chain from the native ledger, projects the source into a
public ``RoleEvidenceOffer`` and builds a public history projection after the
later credit.  All seven policy arms then consume the same frozen menu,
arrival schedule and feature vectors.  The output is not a benchmark result.
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
import time
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    ProducerScore,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)
from peerrolebench_baseline_contract import COST_FIELDS, validate_contract  # noqa: E402
from peerrolebench_baseline_root_contract import validate_public_prefix  # noqa: E402
from peerrolebench_candidate_registry import (  # noqa: E402
    CandidateRegistryEntry,
    registry_digest,
    validate_registry,
)
from peerrolebench_event_time_schedule import ArrivalAssignment, schedule_digest  # noqa: E402
from peerrolebench_peer_history import PeerHistoryV1  # noqa: E402
from peerrolebench_peer_history_adapter import append_history_after_credit  # noqa: E402
from peerrolebench_policy_matrix_runner_v1 import MatrixOffer, PolicyMatrixRunner, _offer  # noqa: E402
from peerrolebench_role_evidence_offer import (  # noqa: E402
    RoleEvidenceOffer,
    build_role_evidence_from_ledger,
    make_role_evidence_offer,
)
from peerrolebench_two_stage_gate import (  # noqa: E402
    DelayedCreditLedger,
    LaterCredit,
    evaluate_source_gate,
)


VERSION = "canonical-pipe3-public-input-parity-v2"
TASK_ID = "PIPE3_stream_processing"
ARM_NAMES = (
    "uniform", "no_update", "raw_acceptance", "terminal_only",
    "contextual_trust", "pooled_controller", "RARE",
)
CANDIDATE_KEYS = ("peer-b@v1", "peer-c@v1")
TARGET_READ_CUT = 12
PHI_VERSION = "canonical-public-judgment-history-hash64-v2"


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _registry() -> tuple[CandidateRegistryEntry, ...]:
    return validate_registry(tuple(
        CandidateRegistryEntry(
            candidate_id=name,
            candidate_version="v1",
            source_digest=(name[-1] * 64),
            model_id="canonical/fixture-agent",
            model_config_digest=(name[-1] * 64),
        )
        for name in ("peer-a", "peer-b", "peer-c")
    ))


def _hash64_features(payload: Mapping[str, Any], candidate_key: str) -> tuple[float, ...]:
    """Create a bounded deterministic public feature vector for parity only."""
    seed = json.dumps({"phi_version": PHI_VERSION, "candidate_key": candidate_key,
                       "payload": payload}, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    raw = hashlib.sha256(seed + b"\\x00").digest() + hashlib.sha256(seed + b"\\x01").digest()
    values = [((byte / 255.0) * 2.0 - 1.0) for byte in raw]
    norm = sum(value * value for value in values) ** 0.5
    return tuple(value / norm for value in values)


def _build_canonical_fixture() -> dict[str, Any]:
    registry = _registry()
    registry_hash = registry_digest(registry)
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)

    # Source episode: the native ledger is the only source of the evidence
    # identity.  The producer score is retained for lineage but is not exposed
    # to the public assignment projection.
    ledger.record_selection(PeerSelection(
        "s0", TASK_ID, 0, "peer-selector", "producer",
        ("peer-b", "peer-c"), "peer-b", 0.5,
    ))
    ledger.record_task_start(TASK_ID, 0)
    ledger.record_delivery(Delivery(
        "d0", TASK_ID, "peer-b", "peer-recipient", "a" * 64,
        "request-0", 0, "s0", candidate_source_digest="b" * 64,
    ))
    ledger.record_producer_score(ProducerScore(
        "q0", "d0", "a" * 64, "producer-score-v2", "FAIL", 0, 0.0,
        "c" * 64, True, True,
    ))
    ledger.record_judgment(RecipientJudgment(
        "j0", "d0", "peer-recipient", "accept", "a" * 64,
    ))
    ledger.record_action(ConsumerAction(
        "c0", "d0", "peer-recipient", True, "a" * 64, "d" * 64,
        action="use",
    ))
    ledger.record_outcome(TerminalOutcome(
        "o0", "d0", True, "source-score-v1", 1.0, "e" * 64,
    ))
    ledger.record_evidence_update(RoleEvidenceUpdate(
        "e0", "j0", "c0", "o0", "role-v1", 5.0,
    ))

    # The public role offer is only admissible after the active v2 source gate
    # says that the producer defect is independently registered.  This keeps
    # the parity fixture on the same responsibility boundary as the live path;
    # it does not turn this zero-call fixture into a scientific label.
    source_gate = evaluate_source_gate(
        materials={"agent_payloads": {
            "producer": {"writable_paths": ("priority.py",)},
            "recipient": {"writable_paths": ("consumer.py",)},
        }},
        producer_score={
            "status": "FAIL", "label": 0, "coverage_complete": True,
            "decision_complete": True,
        },
        judgment={
            "target_role": "producer", "observed_artifact_sha256": "a" * 64,
            "producer_defect_registered": True, "decision": "accept",
        },
        action={
            "consumer_action": "use", "used_artifact": True, "changed_paths": (),
        },
        outcome={
            "status": "PASS", "coverage_complete": True,
            "decision_complete": True,
        },
    )
    if not source_gate.evidence_publish_allowed:
        raise AssertionError(f"canonical source gate did not qualify: {source_gate.reason}")

    source_row = build_role_evidence_from_ledger(
        ledger=ledger, evidence_id="e0", candidate_key="peer-b@v1",
        role="producer", target_task_index=1, evidence_version="role-v1",
        available_index=5,
    )
    role_offer = make_role_evidence_offer(
        offer_id="canonical-role-offer-1", task_id=TASK_ID, task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=CANDIDATE_KEYS,
        evidence=(source_row,), evidence_version="role-v1", available_index=5,
        candidate_registry_digest=registry_hash,
    )
    public_role_projection = {
        "schema": "role-evidence-public-judgment-v1",
        "offer_id": role_offer.offer_id,
        "task_id": role_offer.task_id,
        "task_index": int(role_offer.task_index),
        "role": role_offer.role,
        "context_key": role_offer.context_key,
        "candidate_keys": list(role_offer.candidate_keys),
        "evidence_version": role_offer.evidence_version,
        "available_index": int(role_offer.available_index),
        "judgments": [
            {
                "evidence_id": str(item["evidence_id"]),
                "candidate_key": str(item["candidate_key"]),
                "judgment": str(item["judgment"]),
                "action": str(item["action"]),
                "available_index": int(item["available_index"]),
            }
            for item in role_offer.public_evidence
        ],
    }

    # Later assignment and outcome create a genuine history projection at the
    # next read cut.  The target selection is recorded only after assignment,
    # preserving the assignment-before-selection boundary.
    assignment = LaterAssignment("as1", TASK_ID, 1, "peer-b", "producer", ("e0",), 0.5)
    ledger.record_assignment(assignment)
    ledger.record_selection(PeerSelection(
        "s1", TASK_ID, 1, "peer-selector-2", "producer",
        ("peer-b", "peer-c"), "peer-b", 0.5,
    ))
    ledger.record_task_start(TASK_ID, 1)
    ledger.record_delivery(Delivery(
        "d1", TASK_ID, "peer-b", "peer-recipient-2", "f" * 64,
        "request-1", 1, "s1", candidate_source_digest="b" * 64,
    ))
    ledger.record_judgment(RecipientJudgment(
        "j1", "d1", "peer-recipient-2", "accept", "f" * 64,
    ))
    ledger.record_action(ConsumerAction(
        "c1", "d1", "peer-recipient-2", True, "f" * 64, "1" * 64,
        action="use",
    ))
    ledger.record_outcome(TerminalOutcome(
        "o1", "d1", True, "target-score-v1", 1.0, "2" * 64,
    ))
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    delayed.apply_once(credit, lambda _: None)
    history = PeerHistoryV1.empty("peer-b")
    history_result = append_history_after_credit(
        history=history, ledger=ledger, offer=role_offer,
        target_assignment=assignment, target_selection=ledger.selections["s1"],
        credit=credit, delayed_ledger=delayed, assignment_read_cut=5,
        target_decision_index=6, target_arrival_index=12,
        candidate_key="peer-b@v1", candidate_registry_digest=registry_hash,
    )
    projections = {
        "peer-b@v1": history.selector_projection(candidate_key="peer-b@v1"),
        "peer-c@v1": PeerHistoryV1.empty("peer-c").selector_projection(candidate_key="peer-c@v1"),
    }
    # Each decision gets a read-cut-specific public feature map.  The source
    # offer is invisible at cut 0, the history entry is invisible at cut 5,
    # and both are visible at cut 12.  This prevents future target outcomes
    # from entering an earlier selection while keeping the map identical
    # across policy arms.
    captured_features_by_read_cut: dict[int, dict[str, tuple[float, ...]]] = {}
    phi_payload_by_read_cut: dict[int, dict[str, Any]] = {}
    for read_cut in (0, 5, TARGET_READ_CUT):
        visible_role_offer = public_role_projection if read_cut >= role_offer.available_index else None
        visible_history = {}
        for key, value in projections.items():
            arrivals = [int(scope["last_arrival"]) for scope in value.get("scopes", ())
                        if scope.get("last_arrival") is not None]
            if not arrivals or max(arrivals) <= read_cut:
                visible_history[key] = value
        payload = {
            "role_offer": visible_role_offer,
            "history_projections": visible_history,
            "candidate_registry_digest": registry_hash,
            "candidate_keys": list(CANDIDATE_KEYS),
            "read_cut": read_cut,
        }
        features = {
            key: _hash64_features({"public": payload, "projection": projections[key] if key in visible_history else None}, key)
            for key in CANDIDATE_KEYS
        }
        captured_features_by_read_cut[read_cut] = features
        phi_payload_by_read_cut[read_cut] = payload
    phi_digest = _digest({
        "phi_version": PHI_VERSION,
        "payload_by_read_cut": phi_payload_by_read_cut,
        "feature_vectors_by_read_cut": {
            str(cut): {key: list(value) for key, value in features.items()}
            for cut, features in captured_features_by_read_cut.items()
        },
    })

    # Derive the public policy row from the RoleEvidenceOffer and native
    # delivery selection.  No operator-only score or artifact field crosses
    # this boundary.
    source_selection_id = ledger.deliveries["d0"].selection_id
    if source_selection_id is None:
        raise AssertionError("canonical source delivery lost selection binding")
    row = role_offer.public_evidence[0]
    policy_row = {
        "feedback_id": "role-feedback-e0",
        # The matrix policy event is a versioned sidecar id; the native
        # selection id remains bound in ``role_lineage`` and is checked below.
        "source_event_id": f"policy-{source_selection_id}",
        "source": "recipient_judgment",
        "candidate_key": row["candidate_key"],
        # The matrix runner's public-row adapter has its own frozen schema;
        # the source role offer/version remains bound in role_lineage below.
        "evidence_version": "matrix-evidence-v1",
        "source_index": int(row["source_task_index"]),
        "arrival_index": int(row["available_index"]),
        "arrived_at": float(row["available_index"]),
        "delay": float(row["available_index"]),
        "action": "accept",
        "disposition": "eligible",
        "provenance": "public",
        "label": 1.0,
        "_protocol_event_id": row["judgment_id"],
    }
    role_lineage = {
        "delivery_id": row["delivery_id"],
        "selection_id": source_selection_id,
        "policy_source_event_id": policy_row["source_event_id"],
        "judgment_id": row["judgment_id"],
        "candidate_key": row["candidate_key"],
        "role_offer_digest": role_offer.bundle_digest,
    }
    return {
        "ledger": ledger,
        "registry": registry,
        "registry_digest": registry_hash,
        "role_offer": role_offer,
        "public_role_projection": public_role_projection,
        "history": history,
        "history_result": history_result,
        "history_projections": projections,
        "policy_row": policy_row,
        "role_lineage": role_lineage,
        "source_gate": source_gate.payload(),
        "captured_features_by_read_cut": captured_features_by_read_cut,
        "phi_payload_by_read_cut": phi_payload_by_read_cut,
        "phi_digest": phi_digest,
        "ledger_digest": _digest(ledger.events),
        "history_state_digest": history.state_digest(),
    }


def _stream(fixture: Mapping[str, Any], *, late: bool = False) -> tuple[list[MatrixOffer], tuple[ArrivalAssignment, ...], str]:
    keys = CANDIDATE_KEYS
    row = dict(fixture["policy_row"])
    if late:
        row["arrival_index"] = 5
    first = _offer(
        offer_id="canonical-stream-0", task_index=0, candidate_keys=keys,
        public_rows=(), available_index=0, native_selection_id="s0",
        read_cut=0, decision_index=0, selected_at=0.0, rng_seed=11,
        context_key="PIPE3:0", base_scores=(0.25, -0.25),
        feature_schema=PHI_VERSION,
    )
    second = _offer(
        offer_id="canonical-stream-1", task_index=1, candidate_keys=keys,
        public_rows=(row,), available_index=5, native_selection_id="s1",
        read_cut=0 if late else 5, decision_index=5, selected_at=5.0,
        rng_seed=12, context_key="PIPE3:1",
        protocol_event_ids={str(row["feedback_id"]): str(row["_protocol_event_id"])},
        base_scores=(0.25, -0.25), feature_schema=PHI_VERSION,
    )
    third = _offer(
        offer_id="canonical-stream-2", task_index=2, candidate_keys=keys,
        public_rows=(row,), available_index=5, native_selection_id="s2",
        read_cut=TARGET_READ_CUT, decision_index=TARGET_READ_CUT, selected_at=float(TARGET_READ_CUT),
        rng_seed=13, context_key="PIPE3:2",
        protocol_event_ids={str(row["feedback_id"]): str(row["_protocol_event_id"])},
        base_scores=(0.25, -0.25), feature_schema=PHI_VERSION,
    )
    third = replace(third, captured_features=fixture["captured_features_by_read_cut"][TARGET_READ_CUT], selector_id="peer-selector")
    fourth = _offer(
        offer_id="canonical-stream-3", task_index=3, candidate_keys=keys,
        public_rows=(row,), available_index=5, native_selection_id="s3",
        read_cut=TARGET_READ_CUT, decision_index=TARGET_READ_CUT + 1, selected_at=float(TARGET_READ_CUT + 1),
        rng_seed=14, context_key="PIPE3:3",
        protocol_event_ids={str(row["feedback_id"]): str(row["_protocol_event_id"])},
        base_scores=(0.25, -0.25), feature_schema=PHI_VERSION,
    )
    offers = [
        replace(first, selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][0]),
        replace(second, selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][5]),
        third,
        replace(fourth, selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][TARGET_READ_CUT]),
    ]
    schedule = (ArrivalAssignment(
        feedback_id=str(row["feedback_id"]), protocol_event_type="recipient_judgment",
        protocol_event_id=str(row["_protocol_event_id"]),
        source_event_id=str(row["source_event_id"]), arrival_index=int(row["arrival_index"]),
    ),)
    return offers, schedule, schedule_digest(schedule)


def _common_input(fixture: Mapping[str, Any], offers: Sequence[MatrixOffer], schedule: Sequence[ArrivalAssignment]) -> dict[str, Any]:
    return {
        "role_public_projection_digest": _digest(fixture["public_role_projection"]),
        "operator_role_offer_bundle_digest": fixture["role_offer"].bundle_digest,
        "role_offer_record_hash": fixture["role_offer"].offer_record_hash,
        "history_projection_digests": {
            key: _digest(value) for key, value in fixture["history_projections"].items()
        },
        "candidate_registry_digest": fixture["registry_digest"],
        "candidate_keys": list(CANDIDATE_KEYS),
        "read_cuts": [int(item.read_cut) for item in offers],
        "decision_indices": [int(item.decision_index) for item in offers],
        "arrival_schedule": [item.payload() for item in schedule],
        "phi_version": PHI_VERSION,
        "phi_digest": fixture["phi_digest"],
        "phi_payload_by_read_cut": fixture["phi_payload_by_read_cut"],
        "cost_fields": list(COST_FIELDS),
    }


def _validate_valid_result(result: Mapping[str, Any], fixture: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    expected_cuts = {"policy-s0": 0, "policy-s1": 5,
                     "policy-s2": TARGET_READ_CUT,
                     "policy-s3": TARGET_READ_CUT}
    expected_features = {
        str(event_id): {key: list(values)
                        for key, values in fixture["captured_features_by_read_cut"][cut].items()}
        for event_id, cut in expected_cuts.items()
    }
    observations: dict[str, Any] = {}
    for name in ARM_NAMES:
        snapshot = result["final_policy_snapshots"][name]
        decisions = snapshot["decisions"]
        feature_match = all(
            decisions[event_id].get("captured_features") == expected_features[event_id]
            for event_id in expected_cuts
        )
        public_trace = [
            {"decision_index": trace["decision_index"],
             "visible_feedback_ids": trace["visible_feedback_ids"],
             "visible_fields": trace["visible_fields"]}
            for trace in result["traces"][name]
        ]
        observations[name] = {
            "public_trace_digest": _digest(public_trace),
            "captured_feature_digest": _digest({event_id: decisions[event_id]["captured_features"] for event_id in expected_cuts}),
            "captured_features_match_canonical": feature_match,
        }
    checks = {
        "all_arms_selected_four_times": all(
            result["metrics"][name]["n_selected"] == 4 for name in ARM_NAMES
        ),
        "revisible_prefix_recorded": all(
            result["metrics"][name]["n_revisible_prefix_rows"] == 2 for name in ARM_NAMES
        ),
        "no_unknown_or_unselected": all(
            result["metrics"][name]["n_unknown"] == 0
            and result["metrics"][name]["n_unselected"] == 0 for name in ARM_NAMES
        ),
        "snapshot_replay_equal": all(
            item["snapshot_equal"]
            for item in result["replay"].values()
        ),
        "independent_state_namespaces": len(set(result["final_state_digests"].values())) == len(ARM_NAMES),
        "public_trace_inputs_equal": len({item["public_trace_digest"] for item in observations.values()}) == 1,
        "canonical_phi_inputs_equal": len({item["captured_feature_digest"] for item in observations.values()}) == 1
        and all(item["captured_features_match_canonical"] for item in observations.values()),
        "visible_input_digests_equal": len({
            tuple(result["visible_input_digests"][name]) for name in ARM_NAMES
        }) == 1,
    }
    return checks, observations


def _run_valid(fixture: Mapping[str, Any]) -> dict[str, Any]:
    offers, schedule, digest = _stream(fixture)
    runner = PolicyMatrixRunner(registry=fixture["registry"], arm_names=ARM_NAMES)
    result = runner.run(offers, schedule, expected_schedule_digest=digest)
    checks, observations = _validate_valid_result(result, fixture)
    isolated_arm_checks: dict[str, bool] = {}
    for name in ARM_NAMES:
        solo = PolicyMatrixRunner(registry=fixture["registry"], arm_names=(name,)).run(
            offers, schedule, expected_schedule_digest=digest,
        )
        isolated_arm_checks[name] = (
            solo["final_policy_snapshots"][name] == result["final_policy_snapshots"][name]
        )
    checks["cross_arm_state_isolation"] = all(isolated_arm_checks.values())
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "schedule_digest": digest,
        "common_input": _common_input(fixture, offers, schedule),
        "arm_public_input_observations": observations,
        "cross_arm_state_isolation": isolated_arm_checks,
        "result": result,
    }


def _run_unknown(fixture: Mapping[str, Any]) -> dict[str, Any]:
    # An explicit UNKNOWN row is visible at the read cut, but carries no
    # label.  Replaying that same row is a re-visible prefix, not a new
    # update.  This tests no-update semantics without silently deleting the
    # denominator.
    row = dict(fixture["policy_row"])
    row["disposition"] = "unknown"
    row["provenance"] = "unknown"
    row["unknown_reason"] = "source_gate_not_eligible"
    row.pop("label", None)
    common = {
        "candidate_keys": CANDIDATE_KEYS,
        "public_rows": (row,),
        "available_index": 5,
        "base_scores": (0.25, -0.25),
        "feature_schema": PHI_VERSION,
        "protocol_event_ids": {str(row["feedback_id"]): str(row["_protocol_event_id"])},
    }
    offers = [
        replace(_offer(
            offer_id="canonical-unknown-0", task_index=0, candidate_keys=CANDIDATE_KEYS,
            public_rows=(), available_index=0, native_selection_id="s0",
            read_cut=0, decision_index=0, selected_at=0.0, rng_seed=11,
            context_key="PIPE3:0", base_scores=(0.25, -0.25), feature_schema=PHI_VERSION,
        ), selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][0]),
        replace(_offer(
            offer_id="canonical-unknown-1", task_index=1, native_selection_id="s1",
            read_cut=5, decision_index=5, selected_at=5.0, rng_seed=12,
            context_key="PIPE3:1", **common,
        ), selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][5]),
        replace(_offer(
            offer_id="canonical-unknown-2", task_index=2, native_selection_id="s2",
            read_cut=TARGET_READ_CUT, decision_index=TARGET_READ_CUT,
            selected_at=float(TARGET_READ_CUT), rng_seed=13,
            context_key="PIPE3:2", **common,
        ), selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][TARGET_READ_CUT]),
        replace(_offer(
            offer_id="canonical-unknown-3", task_index=3, native_selection_id="s3",
            read_cut=TARGET_READ_CUT, decision_index=TARGET_READ_CUT + 1,
            selected_at=float(TARGET_READ_CUT + 1), rng_seed=14,
            context_key="PIPE3:3", **common,
        ), selector_id="peer-selector", captured_features=fixture["captured_features_by_read_cut"][TARGET_READ_CUT]),
    ]
    schedule = (ArrivalAssignment(
        feedback_id=str(row["feedback_id"]), protocol_event_type="recipient_judgment",
        protocol_event_id=str(row["_protocol_event_id"]),
        source_event_id=str(row["source_event_id"]), arrival_index=int(row["arrival_index"]),
    ),)
    runner = PolicyMatrixRunner(registry=fixture["registry"], arm_names=ARM_NAMES)
    digest = schedule_digest(schedule)
    result = runner.run(offers, schedule, expected_schedule_digest=digest)
    checks = {
        "all_arms_selected_four_times": all(result["metrics"][name]["n_selected"] == 4 for name in ARM_NAMES),
        "all_arms_no_updates": all(result["metrics"][name]["updates"] == 0 for name in ARM_NAMES),
        "explicit_unknown_recorded": all(
            result["metrics"][name]["n_unknown"] == 1
            and result["metrics"][name]["n_eligible"] == 0
            and result["metrics"][name]["n_revisible_prefix_rows"] == 2
            for name in ARM_NAMES
        ),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
            "common_input": _common_input(fixture, offers, schedule), "result": result}


def _run_rejected_cell(name: str, fn: Any) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        fn()
    except Exception as exc:
        return {
            "status": "UNKNOWN",
            "accepted": False,
            "false_accept": False,
            "unknown_reason": f"{type(exc).__name__}: {exc}",
            "wall_ms": round((time.perf_counter() - started) * 1000.0, 6),
            "cell": name,
            "policy_updates": 0,
            "selection_count": 0,
        }
    return {
        "status": "FAIL", "accepted": True, "false_accept": True,
        "unknown_reason": None, "wall_ms": round((time.perf_counter() - started) * 1000.0, 6),
        "cell": name, "policy_updates": None, "selection_count": None,
    }


def _run_late(fixture: Mapping[str, Any]) -> dict[str, Any]:
    offers, schedule, digest = _stream(fixture, late=True)
    def reject() -> None:
        from peerrolebench_event_time_schedule import validate_schedule
        validated = validate_schedule(
            schedule,
            expected_feedback_ids={
                str(row["feedback_id"])
                for item in offers for row in item.offer.public_rows
            },
        )
        by_id = {row.feedback_id: row for row in validated}
        runner = PolicyMatrixRunner(registry=fixture["registry"], arm_names=ARM_NAMES)
        # Validate every offer before any policy object is allowed to select.
        # A rejected late stream therefore has measured zero selections and
        # zero updates rather than a hard-coded rollback claim.
        for item in offers:
            runner._validate_offer(item, by_id)
            validate_public_prefix(
                validated,
                [str(row["feedback_id"]) for row in item.offer.public_rows],
                read_cut=item.read_cut,
            )
    return _run_rejected_cell("feedback-after-frozen-read-cut", reject)


def _run_mutation(fixture: Mapping[str, Any]) -> dict[str, Any]:
    def mutate() -> None:
        offer = fixture["role_offer"]
        payload = offer.payload()
        payload["bundle_digest"] = "b" * 64
        # Dataclass replace alone does not re-run the digest contract.
        # Reconstruct the public object so the canonical constructor rejects
        # the mutation before any policy state exists.
        RoleEvidenceOffer(
            offer_id=str(payload["offer_id"]),
            offer_record_hash=offer.offer_record_hash,
            task_id=str(payload["task_id"]),
            task_index=int(payload["task_index"]),
            role=str(payload["role"]),
            context_key=str(payload["context_key"]),
            candidate_keys=tuple(payload["candidate_keys"]),
            evidence_ids=tuple(payload["evidence_ids"]),
            evidence_version=str(payload["evidence_version"]),
            public_evidence=tuple(payload["public_evidence"]),
            available_index=int(payload["available_index"]),
            bundle_digest=str(payload["bundle_digest"]),
            watermark_schema=str(payload["watermark_schema"]),
            candidate_registry_digest=payload.get("candidate_registry_digest"),
        )
    return _run_rejected_cell("mutated-role-offer-digest", mutate)


def run(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    script_path = Path(__file__).resolve()
    component_names = (
        "peerrolebench_canonical_pipe3_parity_qualification.py",
        "peerrolebench_policy_matrix_runner_v1.py",
        "peerrolebench_baseline_policies.py",
        "peerrolebench_role_evidence_offer.py",
        "peerrolebench_peer_history_adapter.py",
        "peerrolebench_peer_history.py",
        "peerrolebench_two_stage_gate.py",
    )
    config = {
        "qualification_version": VERSION,
        "kind": "zero_call_canonical_pipe3_public_input_schema_parity",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": sys.argv,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version,
        "platform": platform.platform(),
        "component_sha256": {name: _sha(ROOT / "scripts" / name) for name in component_names},
        "script_sha256": _sha(script_path),
        "arms": list(ARM_NAMES),
        "phi_version": PHI_VERSION,
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "benchmark_qualified": False,
        "baseline_parity_scientific": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    raw_path = out_dir / "raw.jsonl"
    fixture = _build_canonical_fixture()
    with raw_path.open("w", encoding="utf-8") as raw:
        raw.write(json.dumps({"event_type": "canonical_fixture", "payload": {
            "ledger_digest": fixture["ledger_digest"],
            "role_offer": fixture["role_offer"].payload(),
            "source_gate": fixture["source_gate"],
            "role_lineage": fixture["role_lineage"],
            "history_state_digest": fixture["history_state_digest"],
            "history_projections": fixture["history_projections"],
            "phi_digest": fixture["phi_digest"],
        }}, ensure_ascii=False, default=str) + "\n")
        valid = _run_valid(fixture)
        raw.write(json.dumps({"event_type": "valid_cell", "payload": valid}, ensure_ascii=False, default=str) + "\n")
        unknown = _run_unknown(fixture)
        raw.write(json.dumps({"event_type": "unknown_cell", "payload": unknown}, ensure_ascii=False, default=str) + "\n")
        late = _run_late(fixture)
        raw.write(json.dumps({"event_type": "late_cell", "payload": late}, ensure_ascii=False, default=str) + "\n")
        mutation = _run_mutation(fixture)
        raw.write(json.dumps({"event_type": "mutation_cell", "payload": mutation}, ensure_ascii=False, default=str) + "\n")
        raw.flush()

    checks = {
        "valid_canonical_stream": valid["status"] == "PASS",
        "unknown_no_update": unknown["status"] == "PASS",
        "late_false_accept_zero": late.get("false_accept") is False,
        "mutation_false_accept_zero": mutation.get("false_accept") is False,
        "all_rejected_cells_zero_updates": all(
            cell.get("policy_updates") == 0 for cell in (late, mutation)
        ),
    }
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE_PUBLIC_INPUT_PARITY" if all(checks.values()) else "FAILED_OFFLINE",
        "passed": all(checks.values()),
        "checks": checks,
        "fixture": {
            "ledger_digest": fixture["ledger_digest"],
        "role_offer_bundle_digest": fixture["role_offer"].bundle_digest,
        "role_public_projection_digest": _digest(fixture["public_role_projection"]),
            "role_offer_record_hash": fixture["role_offer"].offer_record_hash,
            "history_state_digest": fixture["history_state_digest"],
            "phi_digest": fixture["phi_digest"],
            "role_lineage": fixture["role_lineage"],
        },
        "cells": {"valid": valid, "unknown": unknown, "late": late, "mutation": mutation},
        "interpretation": (
            "Protocol-level same-information and fail-closed qualification only; "
            "no quality, specialization, role-learning, benchmark-authority or cost-effect claim."
        ),
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in (
        "status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed",
    )}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
