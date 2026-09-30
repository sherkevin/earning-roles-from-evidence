"""Versioned PIPE3 runner boundary for a real event-time selection.

This module deliberately stops at the selection boundary.  It does not call an
LLM, execute candidate source, or score a task.  Its purpose is to provide one
reusable path that a future live runner can call after flushing the frozen
arrival schedule: public offer -> policy choice -> native selection -> sidecar
and consumption attestation.  The native and auxiliary manifests remain
separate by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

from peer_role_protocol_20260925 import PeerRoleLedger, PeerSelection
from peerrolebench_assignment_attestation import (
    AssignmentEvidenceOffer,
    DecisionConsumptionAttestation,
    build_consumption_attestation,
    verify_consumption_attestation,
)
from peerrolebench_assignment_manifest import build_manifest as build_aux_manifest
from peerrolebench_assignment_manifest import validate_manifest as validate_aux_manifest
from peerrolebench_baseline_policies import BaselinePolicy, CandidateRef, Feedback, Selection
from peerrolebench_candidate_registry import CandidateRegistryEntry, candidate_refs, validate_registry
from peerrolebench_policy_sidecar import DecisionSidecar
from peerrolebench_policy_sidecar_manifest import build_manifest as build_native_manifest
from peerrolebench_policy_sidecar_manifest import validate_manifest as validate_native_manifest


RUNNER_VERSION = "pipe3-runner-boundary-v1"


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _capture_rng_state(rng: Any) -> tuple[str, Any] | None:
    """Capture common RNG state forms for transaction retry determinism."""

    bit_generator = getattr(rng, "bit_generator", None)
    if bit_generator is not None and hasattr(bit_generator, "state"):
        try:
            return ("bit_generator", copy.deepcopy(bit_generator.state))
        except (TypeError, ValueError):
            pass
    getter = getattr(rng, "getstate", None)
    if callable(getter):
        try:
            return ("getstate", copy.deepcopy(getter()))
        except (TypeError, ValueError):
            pass
    return None


def _restore_rng_state(rng: Any, state: tuple[str, Any] | None) -> None:
    """Restore a captured RNG state when the object exposes a safe setter."""

    if state is None:
        return
    kind, value = state
    if kind == "bit_generator":
        bit_generator = getattr(rng, "bit_generator", None)
        if bit_generator is not None and hasattr(bit_generator, "state"):
            bit_generator.state = copy.deepcopy(value)
    elif kind == "getstate":
        setter = getattr(rng, "setstate", None)
        if callable(setter):
            setter(copy.deepcopy(value))


def auxiliary_manifest_root(rows: Sequence[Mapping[str, Any]]) -> str:
    """Return the current auxiliary manifest root before appending an offer."""

    if not rows:
        return "GENESIS"
    return build_aux_manifest(rows)[-1]["manifest_record_hash"]


def make_offer(
    *,
    offer_id: str,
    task_id: str,
    task_index: int,
    role: str,
    context_key: str,
    candidate_keys: Sequence[str],
    public_rows: Sequence[Mapping[str, Any]],
    evidence_version: str,
    available_index: int,
    previous_aux_hash: str = "GENESIS",
) -> AssignmentEvidenceOffer:
    """Construct an offer and canonical operator record hash.

    The operator hash is computed from the offer payload plus the preceding
    auxiliary-chain hash; it never hashes a payload containing itself.
    """

    rows = sorted((dict(row) for row in public_rows), key=lambda row: (int(row["arrival_index"]), str(row["feedback_id"])))
    evidence_ids = sorted({str(row["source_event_id"]) for row in rows})
    payload = {
        "offer_id": offer_id,
        "task_id": task_id,
        "task_index": int(task_index),
        "role": role,
        "context_key": context_key,
        "candidate_keys": list(candidate_keys),
        "evidence_ids": evidence_ids,
        "evidence_version": evidence_version,
        "public_rows": rows,
        "available_index": int(available_index),
        "watermark_schema": "global-event-index-v1",
    }
    bundle_digest = _digest(payload)
    record_payload = {"record_version": "pipe3-assignment-offer-v1",
                      "previous_aux_hash": previous_aux_hash, **payload}
    return AssignmentEvidenceOffer(
        offer_id=offer_id,
        offer_record_hash=_digest(record_payload),
        task_id=task_id,
        task_index=int(task_index),
        role=role,
        context_key=context_key,
        candidate_keys=tuple(candidate_keys),
        evidence_ids=tuple(evidence_ids),
        evidence_version=evidence_version,
        public_rows=tuple(rows),
        available_index=int(available_index),
        bundle_digest=bundle_digest,
    )


@dataclass(frozen=True)
class SelectionSeal:
    policy_selection: Selection
    native_selection: PeerSelection
    decision_sidecar: DecisionSidecar
    attestation: DecisionConsumptionAttestation


class Pipe3SelectionBoundary:
    """Reusable selection/attestation boundary for one policy arm."""

    def __init__(self, policy: BaselinePolicy, registry: Sequence[CandidateRegistryEntry | Mapping[str, Any]]):
        self.policy = policy
        self.registry = validate_registry(registry)
        self.ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
        self.selections: dict[str, Selection] = {}
        self.native_manifest_rows: list[dict[str, str]] = []
        self.auxiliary_manifest_rows: list[dict[str, str]] = []

    def _consume_rows(self, offer: AssignmentEvidenceOffer) -> int:
        updates = 0
        for row in offer.public_rows:
            source = self.selections.get(str(row["source_event_id"]))
            if source is None or row["candidate_key"] != source.chosen.key:
                raise ValueError("evidence row is not bound to the selected candidate")
            feedback = Feedback(
                feedback_id=str(row["feedback_id"]), source_event_id=str(row["source_event_id"]),
                source=str(row["source"]),
                label=None if row.get("label") is None else float(row["label"]),
                arrived_at=float(row["arrived_at"]), delay=float(row["delay"]),
                action=str(row["action"]), disposition=str(row["disposition"]),
                provenance=str(row["provenance"]),
                arrival_index=None if row.get("arrival_index") is None else int(row["arrival_index"]),
                supersedes=None if row.get("supersedes") is None else str(row["supersedes"]),
            )
            updates += int(self.policy.observe_feedback(feedback))
        return updates

    def choose_and_seal(
        self,
        *,
        offer: AssignmentEvidenceOffer,
        native_selection_id: str,
        selector_id: str,
        role: str,
        base_scores: Sequence[float],
        rng: Any,
        state_version: str,
        encoder_version: str,
        feature_schema: str,
        policy_version: str,
        base_score_version: str,
        rng_algorithm: str,
        rng_draw: int,
        selected_at: float,
        read_cut: int,
        decision_index: int,
        consume_evidence: bool,
        captured_features: Mapping[str, Sequence[float]] | None = None,
    ) -> SelectionSeal:
        """Apply visible feedback, choose a peer, and seal both manifest links."""

        offer_candidate_ids = tuple(key.rsplit("@", 1)[0] for key in offer.candidate_keys)
        refs = candidate_refs(offer_candidate_ids, self.registry)
        if tuple(ref.key for ref in refs) != offer.candidate_keys:
            raise ValueError("offer candidate keys are not registry-resolved in order")
        self._preflight_selection(
            offer=offer, refs=refs, native_selection_id=native_selection_id,
            selector_id=selector_id, role=role, base_scores=base_scores,
            state_version=state_version, encoder_version=encoder_version,
            feature_schema=feature_schema, policy_version=policy_version,
            base_score_version=base_score_version, rng_algorithm=rng_algorithm,
            rng_draw=rng_draw, selected_at=selected_at, read_cut=read_cut,
            decision_index=decision_index, consume_evidence=consume_evidence,
            captured_features=captured_features,
        )

        # Preflight catches all known ordering and identity failures.  Keep a
        # transaction snapshot as a last-resort guard for policy/ledger errors
        # that can only be observed after the sampled choice (for example a
        # custom RNG or a future ledger invariant).  This preserves object
        # identity while restoring every mutable component on failure.
        policy_state = copy.deepcopy(self.policy.__dict__)
        ledger_state = copy.deepcopy(self.ledger.__dict__)
        selections_state = copy.deepcopy(self.selections)
        native_rows_state = copy.deepcopy(self.native_manifest_rows)
        auxiliary_rows_state = copy.deepcopy(self.auxiliary_manifest_rows)
        rng_state = _capture_rng_state(rng)
        try:
            self.auxiliary_manifest_rows.append({
                "record_hash": offer.offer_record_hash,
                "event_type": "assignment_evidence_offer",
                "event_id": offer.offer_id,
                "offer_id": offer.offer_id,
                "decision_event_id": "",
                "attestation_digest": _digest(offer.operator_binding_payload()),
            })
            updates = self._consume_rows(offer) if consume_evidence else 0
            state_digest = _digest(self.policy.snapshot())
            policy_selection = self.policy.choose(
                event_id=f"policy-{native_selection_id}",
                context_key=offer.context_key,
                selector_id=selector_id,
                candidates=refs,
                base_scores=base_scores,
                rng=rng,
                state_version=state_version,
                encoder_version=encoder_version,
                feature_schema=feature_schema,
                selected_at=selected_at,
                captured_features=captured_features,
            )
            self.selections[policy_selection.event_id] = policy_selection
            native_selection = PeerSelection(
                selection_id=native_selection_id,
                task_id=offer.task_id,
                task_index=offer.task_index,
                selector_id=selector_id,
                role=role,
                candidate_ids=tuple(ref.candidate_id for ref in refs),
                chosen_peer_id=policy_selection.chosen.candidate_id,
                propensity=policy_selection.propensity,
            )
            self.ledger.record_selection(native_selection)
            native_record = self.ledger.events[-1]
            if native_record["event_type"] != "peer_selection":
                raise AssertionError("ledger did not append a peer_selection record")
            decision_sidecar = DecisionSidecar(
                ledger_record_hash=native_record["record_hash"], protocol_event_type="peer_selection",
                protocol_event_id=native_selection.selection_id, task_id=offer.task_id,
                task_index=offer.task_index, role=role, event_id=policy_selection.event_id,
                selector_id=selector_id, context_key=offer.context_key, candidates=refs,
                base_scores=policy_selection.base_scores, chosen_index=policy_selection.chosen_index,
                probabilities=policy_selection.probabilities, propensity=policy_selection.propensity,
                state_version=state_version, encoder_version=encoder_version, feature_schema=feature_schema,
                policy_name=self.policy.name, policy_version=policy_version,
                base_score_version=base_score_version, rng_algorithm=rng_algorithm,
                rng_draw=int(rng_draw), selected_at=selected_at,
                captured_features=policy_selection.captured_features, state_digest=state_digest,
            )
            attestation = build_consumption_attestation(
                offer, decision_sidecar, consumed=bool(consume_evidence),
                read_cut=int(read_cut), decision_index=int(decision_index),
            )
            if verify_consumption_attestation(attestation, offer, decision_sidecar) != bool(consume_evidence):
                raise AssertionError("selection consumption attestation did not verify")
            self.native_manifest_rows.append({
                "ledger_record_hash": native_record["record_hash"],
                "protocol_event_type": "peer_selection",
                "protocol_event_id": native_selection.selection_id,
                "sidecar_digest": decision_sidecar.sidecar_digest,
            })
            self.auxiliary_manifest_rows.append({
                "record_hash": native_record["record_hash"],
                "event_type": "decision_consumption_attestation",
                "event_id": native_selection.selection_id,
                "offer_id": offer.offer_id,
                "decision_event_id": native_selection.selection_id,
                "attestation_digest": attestation.attestation_digest,
            })
            return SelectionSeal(policy_selection, native_selection, decision_sidecar, attestation)
        except Exception:
            self.policy.__dict__.clear()
            self.policy.__dict__.update(policy_state)
            self.ledger.__dict__.clear()
            self.ledger.__dict__.update(ledger_state)
            self.selections.clear()
            self.selections.update(selections_state)
            self.native_manifest_rows[:] = native_rows_state
            self.auxiliary_manifest_rows[:] = auxiliary_rows_state
            _restore_rng_state(rng, rng_state)
            raise

    def _preflight_selection(
        self, *, offer: AssignmentEvidenceOffer, refs: Sequence[CandidateRef],
        native_selection_id: str, selector_id: str, role: str,
        base_scores: Sequence[float], state_version: str, encoder_version: str,
        feature_schema: str, policy_version: str, base_score_version: str,
        rng_algorithm: str, rng_draw: int, selected_at: float, read_cut: int,
        decision_index: int, consume_evidence: bool,
        captured_features: Mapping[str, Sequence[float]] | None,
    ) -> None:
        """Reject known invalid selections before touching policy or ledgers."""
        if offer.role != role:
            raise ValueError("offer role does not match selection role")
        if not native_selection_id or not selector_id:
            raise ValueError("selection and selector identifiers are required")
        if selector_id in {ref.candidate_id for ref in refs}:
            raise ValueError("selector cannot be one of the candidate peers")
        if native_selection_id in self.ledger.selections:
            raise ValueError("duplicate selection_id")
        policy_event_id = f"policy-{native_selection_id}"
        if policy_event_id in getattr(self.policy, "_decisions", {}):
            raise ValueError("duplicate policy decision event_id")
        task_key = (offer.task_id, int(offer.task_index))
        if task_key in self.ledger.started_tasks:
            raise ValueError("selection must be recorded before the task starts")
        if any((item.task_id, item.task_index) == task_key for item in self.ledger.selections.values()):
            raise ValueError("one selection is required per task episode")
        if not all(isinstance(value, str) and value for value in (
            state_version, encoder_version, feature_schema, policy_version,
            base_score_version, rng_algorithm,
        )):
            raise ValueError("state/model/schema/policy versions are required")
        if type(rng_draw) is not int or rng_draw < 0:
            raise ValueError("rng_draw must be a non-negative integer")
        if not math.isfinite(float(selected_at)) or float(selected_at) < 0.0:
            raise ValueError("selected_at must be non-negative and finite")
        if type(read_cut) is not int or read_cut < 0:
            raise ValueError("read_cut must be a non-negative integer")
        if type(decision_index) is not int or decision_index < 0:
            raise ValueError("decision_index must be a non-negative integer")
        if read_cut > decision_index:
            raise ValueError("read_cut is after decision index")
        if consume_evidence and offer.available_index > read_cut:
            raise ValueError("offer is unavailable at read cut")
        if len(refs) != len(base_scores) or not refs:
            raise ValueError("candidate menu and base scores must be non-empty and aligned")
        if not all(math.isfinite(float(value)) for value in base_scores):
            raise ValueError("base scores must be finite and aligned")
        for key, values in (captured_features or {}).items():
            if key not in {ref.key for ref in refs}:
                raise ValueError(f"captured feature has unknown candidate {key!r}")
            vector = tuple(float(value) for value in values)
            if not vector or not all(math.isfinite(value) for value in vector):
                raise ValueError("captured features must be finite and non-empty")
        if consume_evidence:
            for row in offer.public_rows:
                source = self.selections.get(str(row["source_event_id"]))
                if source is None or row["candidate_key"] != source.chosen.key:
                    raise ValueError("evidence row is not bound to the selected candidate")
                Feedback(
                    feedback_id=str(row["feedback_id"]), source_event_id=str(row["source_event_id"]),
                    source=str(row["source"]), label=None if row.get("label") is None else float(row["label"]),
                    arrived_at=float(row["arrived_at"]), delay=float(row["delay"]),
                    action=str(row["action"]), disposition=str(row["disposition"]),
                    provenance=str(row["provenance"]),
                    arrival_index=None if row.get("arrival_index") is None else int(row["arrival_index"]),
                    supersedes=None if row.get("supersedes") is None else str(row["supersedes"]),
                )

    def validate_selection_manifests(self) -> tuple[str, str]:
        """Validate the two chains after their required rows have been added."""

        native = build_native_manifest(self.native_manifest_rows)
        native_root = validate_native_manifest(native, self.native_manifest_rows)
        auxiliary = build_aux_manifest(self.auxiliary_manifest_rows)
        auxiliary_root = validate_aux_manifest(auxiliary, self.auxiliary_manifest_rows)
        return native_root, auxiliary_root

    def choose_and_seal_source_bound(self, *, source_offer: Any, **kwargs: Any) -> SelectionSeal:
        """Consume a source-bound offer only on the continuing auxiliary chain.

        The source-bound adapter records the previous auxiliary root when it
        seals the public offer.  Checking that root here prevents a later
        selection from silently starting a fresh manifest chain.
        """
        expected = auxiliary_manifest_root(self.auxiliary_manifest_rows)
        if getattr(source_offer, "previous_aux_hash", None) != expected:
            raise ValueError("source-bound offer previous auxiliary hash does not match runner state")
        offer = getattr(source_offer, "offer", None)
        if offer is None:
            raise TypeError("source_offer must expose an AssignmentEvidenceOffer")
        return self.choose_and_seal(offer=offer, **kwargs)


__all__ = ["Pipe3SelectionBoundary", "RUNNER_VERSION", "SelectionSeal", "auxiliary_manifest_root", "make_offer"]
