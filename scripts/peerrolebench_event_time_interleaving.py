"""Event-time interleaving qualification for evidence-aware peer selection.

This module is an offline protocol seam, not a scientific result.  It runs a
small deterministic schedule with the same candidate menu, seed, and public
feedback for two latency conditions.  Feedback is flushed before a decision
only when its ``arrival_index`` is at or before that decision's read cut.
Consequently, a late label cannot change a decision that has already happened.

The runner deliberately uses the existing ContextualTrustPolicy and
NoUpdatePolicy as comparators.  It does not select a paper method or claim
that a toy label is a benchmark outcome.  Its purpose is to make the temporal
causal seam executable before a real runner is allowed to call an LLM.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from peerrolebench_assignment_attestation import (  # noqa: E402
    AssignmentEvidenceOffer,
    build_consumption_attestation,
    verify_consumption_attestation,
)
from peerrolebench_baseline_policies import (  # noqa: E402
    CandidateRef,
    ContextualTrustPolicy,
    Feedback,
    NoUpdatePolicy,
)
from peerrolebench_policy_sidecar import DecisionSidecar  # noqa: E402
from peerrolebench_policy_sidecar_manifest import (  # noqa: E402
    build_manifest,
    validate_manifest,
)


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class DecisionTrace:
    policy: str
    decision_index: int
    event_id: str
    offer_id: str
    offer_available_index: int
    evidence_ids: tuple[str, ...]
    consumed: bool
    feedback_updates: int
    state_digest: str
    probabilities: tuple[float, ...]
    chosen_key: str
    attestation_digest: str


@dataclass(frozen=True)
class InterleavingRun:
    policy: str
    arrival_index: int
    traces: tuple[DecisionTrace, ...]
    manifest_root: str

    def jsonable(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "arrival_index": self.arrival_index,
            "manifest_root": self.manifest_root,
            "traces": [asdict(trace) for trace in self.traces],
        }


def _make_offer(*, offer_id: str, decision_index: int, rows: list[dict[str, Any]]) -> AssignmentEvidenceOffer:
    candidate_keys = ("agent-a@v1", "agent-b@v1")
    evidence_ids = tuple(sorted(str(row["source_event_id"]) for row in rows))
    payload = {
        "offer_id": offer_id,
        "task_id": "toy-task",
        "task_index": 0,
        "role": "consumer",
        "context_key": "toy-context",
        "candidate_keys": list(candidate_keys),
        "evidence_ids": list(evidence_ids),
        "evidence_version": "toy-evidence-v1",
        "public_rows": sorted(rows, key=lambda row: (int(row["arrival_index"]), str(row["feedback_id"]))),
        "available_index": decision_index,
        "watermark_schema": "global-event-index-v1",
    }
    return AssignmentEvidenceOffer(
        offer_id=offer_id,
        offer_record_hash=_digest({"offer_record": offer_id, "decision_index": decision_index}),
        task_id="toy-task",
        task_index=0,
        role="consumer",
        context_key="toy-context",
        candidate_keys=candidate_keys,
        evidence_ids=evidence_ids,
        evidence_version="toy-evidence-v1",
        public_rows=tuple(rows),
        available_index=decision_index,
        bundle_digest=_digest(payload),
    )


def _feedback_row(*, selected_key: str, arrival_index: int) -> dict[str, Any]:
    # The row is intentionally a public, selected-only situated judgment.  It
    # is generated after decision 0 so it cannot encode a future choice.
    return {
        "feedback_id": "feedback-0",
        "source_event_id": "selection-0",
        "source": "recipient_judgment",
        "candidate_key": selected_key,
        "evidence_version": "toy-evidence-v1",
        "source_index": 0,
        "arrival_index": arrival_index,
        "arrived_at": float(arrival_index),
        "delay": float(arrival_index),
        "action": "accept",
        "disposition": "eligible",
        "provenance": "public",
        "label": 1.0,
    }


def _decision_sidecar(policy: Any, selection: Any, *, decision_index: int, state_digest: str) -> DecisionSidecar:
    return DecisionSidecar(
        ledger_record_hash=_digest({"ledger": selection.event_id, "index": decision_index}),
        protocol_event_type="peer_selection",
        protocol_event_id=selection.event_id,
        task_id="toy-task",
        task_index=0,
        role="consumer",
        event_id=selection.event_id,
        selector_id=selection.selector_id,
        context_key=selection.context_key,
        candidates=selection.candidates,
        base_scores=selection.base_scores,
        chosen_index=selection.chosen_index,
        probabilities=selection.probabilities,
        propensity=selection.propensity,
        state_version=selection.state_version,
        encoder_version=selection.encoder_version,
        feature_schema=selection.feature_schema,
        policy_name=policy.name,
        policy_version="toy-policy-v1",
        base_score_version="toy-base-v1",
        rng_algorithm="numpy-pcg64-v1",
        rng_draw=decision_index,
        selected_at=float(decision_index),
        state_digest=state_digest,
    )


def run_interleaving(*, policy_name: str, arrival_index: int, seed: int = 41) -> InterleavingRun:
    """Run three decisions under one feedback-arrival condition."""

    if arrival_index not in {1, 3}:
        raise ValueError("qualification schedule supports arrival_index 1 (early) or 3 (late)")
    policy = ContextualTrustPolicy(temperature=1.0) if policy_name == "contextual_trust" else NoUpdatePolicy(temperature=1.0)
    rng = np.random.default_rng(seed)
    candidates = (CandidateRef("agent-a", "v1"), CandidateRef("agent-b", "v1"))
    rows_by_arrival: dict[int, list[dict[str, Any]]] = {}
    offered: set[str] = set()
    traces: list[DecisionTrace] = []
    manifest_rows: list[dict[str, str]] = []
    pending_row: dict[str, Any] | None = None

    for ordinal, decision_index in enumerate((0, 2, 4)):
        event_id = f"selection-{ordinal}"
        if ordinal == 0:
            rows: list[dict[str, Any]] = []
        else:
            rows = [
                row for row in rows_by_arrival.get(arrival_index, [])
                if int(row["arrival_index"]) <= decision_index and row["feedback_id"] not in offered
            ]
        offer = _make_offer(offer_id=f"offer-{ordinal}", decision_index=decision_index, rows=rows)

        # The policy has a chance to consume the exact same public offer as the
        # comparator.  NoUpdate sees the bundle but intentionally declines it.
        consumed = policy_name == "contextual_trust" and bool(rows)
        updates_before = policy.updates
        if consumed:
            for row in rows:
                feedback = Feedback(
                    feedback_id=str(row["feedback_id"]), source_event_id=str(row["source_event_id"]),
                    source=str(row["source"]), label=float(row["label"]),
                    arrived_at=float(row["arrived_at"]), delay=float(row["delay"]),
                    action=str(row["action"]), disposition=str(row["disposition"]),
                    provenance=str(row["provenance"]),
                )
                policy.observe_feedback(feedback)
            offered.update(str(row["feedback_id"]) for row in rows)
        elif rows:
            # A comparator is still exposed to the same evidence, but records
            # it as unconsumed so its decision input is the empty bundle.
            offered.update(str(row["feedback_id"]) for row in rows)

        state_digest = _digest(policy.snapshot())
        state_version = f"state-{policy.updates}"
        selection = policy.choose(
            event_id=event_id,
            context_key="toy-context",
            selector_id="selector-toy",
            candidates=candidates,
            base_scores=(0.0, 0.0),
            rng=rng,
            state_version=state_version,
            encoder_version="toy-encoder-v1",
            feature_schema="toy-feature-v1",
            selected_at=float(decision_index),
        )
        sidecar = _decision_sidecar(policy, selection, decision_index=decision_index, state_digest=state_digest)
        attestation = build_consumption_attestation(
            offer, sidecar, consumed=consumed, read_cut=decision_index, decision_index=decision_index
        )
        verified_consumed = verify_consumption_attestation(attestation, offer, sidecar)
        if verified_consumed != consumed:
            raise AssertionError("event-time consumption attestation did not verify")
        manifest_rows.extend([
            {
                "ledger_record_hash": offer.offer_record_hash,
                "protocol_event_type": "assignment_evidence_offer",
                "protocol_event_id": offer.offer_id,
                "sidecar_digest": _digest(offer.operator_binding_payload()),
            },
            {
                "ledger_record_hash": sidecar.ledger_record_hash,
                "protocol_event_type": "decision_consumption_attestation",
                "protocol_event_id": sidecar.protocol_event_id,
                "sidecar_digest": attestation.attestation_digest,
            },
        ])
        trace = DecisionTrace(
            policy=policy_name,
            decision_index=decision_index,
            event_id=event_id,
            offer_id=offer.offer_id,
            offer_available_index=offer.available_index,
            evidence_ids=offer.evidence_ids,
            consumed=consumed,
            feedback_updates=policy.updates - updates_before,
            state_digest=state_digest,
            probabilities=selection.probabilities,
            chosen_key=selection.chosen.key,
            attestation_digest=attestation.attestation_digest,
        )
        traces.append(trace)

        if ordinal == 0:
            pending_row = _feedback_row(selected_key=selection.chosen.key, arrival_index=arrival_index)
            rows_by_arrival.setdefault(arrival_index, []).append(pending_row)

    manifest = build_manifest(manifest_rows)
    manifest_root = validate_manifest(manifest, manifest_rows)
    return InterleavingRun(policy=policy_name, arrival_index=arrival_index,
                           traces=tuple(traces), manifest_root=manifest_root)


def qualify_event_time_interleaving() -> dict[str, Any]:
    """Return assertions that define the offline temporal qualification."""

    early = run_interleaving(policy_name="contextual_trust", arrival_index=1)
    late = run_interleaving(policy_name="contextual_trust", arrival_index=3)
    frozen = run_interleaving(policy_name="no_update", arrival_index=1)
    e0, e1, e2 = early.traces
    l0, l1, l2 = late.traces
    f0, f1, f2 = frozen.traces
    checks = {
        "same_seed_initial_decision": e0.chosen_key == l0.chosen_key == f0.chosen_key,
        "early_feedback_consumed_before_next_decision": e1.consumed and e1.feedback_updates == 1,
        "late_feedback_not_available_at_decision_one": not l1.consumed and not l1.evidence_ids and l1.feedback_updates == 0,
        "late_feedback_consumed_at_decision_two": l2.consumed and l2.feedback_updates == 1,
        "early_changes_next_policy_distribution": e1.probabilities != f1.probabilities,
        "late_does_not_rewrite_decision_one": l1.probabilities == f1.probabilities,
        "latency_only_shifts_effect": e2.probabilities == l2.probabilities,
        "attestations_are_distinct_per_decision": len({trace.attestation_digest for trace in early.traces}) == 3,
        "state_digest_changes_after_update": e0.state_digest != e1.state_digest,
        "append_only_manifest_seals_offer_and_consumption": (
            early.manifest_root != "GENESIS" and late.manifest_root != "GENESIS"
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"event-time qualification failed: {failed}")
    return {
        "status": "QUALIFIED_OFFLINE",
        "scientific_claim_allowed": False,
        "checks": checks,
        "runs": {"early": early.jsonable(), "late": late.jsonable(), "no_update": frozen.jsonable()},
        "interpretation": "A public label can affect only future decisions after its arrival; this does not establish benchmark efficacy or role learning.",
    }


__all__ = ["DecisionTrace", "InterleavingRun", "qualify_event_time_interleaving", "run_interleaving"]
