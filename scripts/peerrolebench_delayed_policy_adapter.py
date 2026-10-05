"""Candidate adapter for the method v1.1 publish/update separation.

The adapter is intentionally policy-agnostic at the evidence boundary.  A
published :class:`RoleEvidenceOffer` is an immutable public input and never
becomes a ``Feedback`` row.  Only a later, replay-validated target channel
(``recipient_judgment`` or ``terminal_outcome``) can reach the wrapped policy.

This is a CPU qualification seam, not a live runner or a scientific result.
It adds the assignment-level idempotency that ``DelayedCreditLedger`` alone
does not provide (that ledger keys by assignment *and* outcome lineage).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping

from peerrolebench_baseline_policies import BaselinePolicy, Feedback
from peerrolebench_role_evidence_offer import RoleEvidenceOffer
from peerrolebench_two_stage_gate import DelayedCreditLedger, LaterCredit, SourceGate


VERSION = "delayed-policy-adapter-v1"


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class PublishReceipt:
    offer_id: str
    offer_digest: str
    evidence_ids: tuple[str, ...]
    state_digest_before: str
    state_digest_after: str
    policy_updates_before: int
    policy_updates_after: int
    namespace: str

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LaterChannelPayload:
    """A target-task feedback channel bound to one delayed credit."""

    credit: LaterCredit
    feedback: Feedback
    target_outcome_id: str
    assignment_candidate_key: str
    namespace: str
    assignment_consumed: bool = True
    selection_matches_assignment: bool = True


class DelayedPolicyAdapter:
    """Separate public evidence publication from real policy updates.

    ``publish`` accepts only a gate-approved typed public offer.  It stores
    the offer and its subject metadata without calling the policy updater.
    ``apply_later_credit`` is the only method that may call
    ``BaselinePolicy.observe_feedback``.  The feedback must point at the
    target task's sealed policy selection; source evidence ids are never
    accepted as feedback event ids.
    """

    def __init__(self, policy: BaselinePolicy, *, namespace: str, state_cap_bytes: int = 1 << 20) -> None:
        if not isinstance(policy, BaselinePolicy):
            raise TypeError("policy must be a BaselinePolicy")
        if not namespace:
            raise ValueError("namespace is required")
        if isinstance(state_cap_bytes, bool) or not isinstance(state_cap_bytes, int) or state_cap_bytes <= 0:
            raise ValueError("state_cap_bytes must be a positive integer")
        self.policy = policy
        self.namespace = str(namespace)
        self.state_cap_bytes = int(state_cap_bytes)
        self._offers: dict[str, dict[str, Any]] = {}
        self._evidence_subjects: dict[str, str] = {}
        self._applied_assignments: dict[str, dict[str, str]] = {}
        self._credit_ledger = DelayedCreditLedger()

    def _state_digest(self) -> str:
        return _digest(self.policy.snapshot())

    def _snapshot_payload(self) -> dict[str, Any]:
        return {
            "version": VERSION,
            "namespace": self.namespace,
            "state_cap_bytes": self.state_cap_bytes,
            "policy": self.policy.snapshot(),
            "offers": self._offers,
            "evidence_subjects": self._evidence_subjects,
            "applied_assignments": self._applied_assignments,
            "credit_ledger": self._credit_ledger.snapshot(),
        }

    def _check_capacity(self) -> None:
        encoded = json.dumps(self._snapshot_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if len(encoded.encode("utf-8")) > self.state_cap_bytes:
            raise ValueError("delayed adapter state cap exceeded")

    def publish(self, offer: RoleEvidenceOffer, *, source_gate: SourceGate) -> PublishReceipt:
        """Store public evidence while keeping persistent policy unchanged."""

        if not isinstance(offer, RoleEvidenceOffer):
            raise TypeError("publish requires a typed RoleEvidenceOffer")
        if not isinstance(source_gate, SourceGate):
            raise TypeError("publish requires a SourceGate")
        if not source_gate.attribution_eligible or not source_gate.evidence_publish_allowed:
            raise ValueError("source gate does not permit evidence publication")
        if source_gate.policy_update_allowed:
            raise ValueError("source gate cannot authorize a policy update during publication")
        digest = _digest(offer.operator_binding_payload())
        existing = self._offers.get(offer.offer_id)
        if existing is not None:
            if existing["offer_digest"] != digest:
                raise ValueError("offer id is already bound to a different payload")
            return PublishReceipt(
                offer.offer_id, digest, tuple(offer.evidence_ids), existing["state_digest"],
                existing["state_digest"], existing["policy_updates"], existing["policy_updates"], self.namespace,
            )
        before = self._state_digest()
        updates_before = int(self.policy.updates)
        subjects = {str(row["evidence_id"]): str(row["candidate_key"]) for row in offer.public_evidence}
        if any(evidence_id in self._evidence_subjects for evidence_id in subjects):
            raise ValueError("evidence id is already published")
        self._offers[offer.offer_id] = {
            "offer_digest": digest,
            "offer": offer.payload(),
            "state_digest": before,
            "policy_updates": updates_before,
        }
        self._evidence_subjects.update(subjects)
        try:
            self._check_capacity()
        except Exception:
            self._offers.pop(offer.offer_id, None)
            for evidence_id in subjects:
                self._evidence_subjects.pop(evidence_id, None)
            raise
        after = self._state_digest()
        updates_after = int(self.policy.updates)
        if after != before or updates_after != updates_before:
            # This should be impossible for this implementation; fail closed
            # if a future hook accidentally performs a policy update.
            self._offers.pop(offer.offer_id, None)
            for evidence_id in subjects:
                self._evidence_subjects.pop(evidence_id, None)
            raise AssertionError("public evidence publication changed policy state")
        return PublishReceipt(
            offer.offer_id, digest, tuple(offer.evidence_ids), before, after,
            updates_before, updates_after, self.namespace,
        )

    def apply_later_credit(self, payload: LaterChannelPayload) -> str:
        """Apply one validated target channel, at most once per assignment."""

        if not isinstance(payload, LaterChannelPayload):
            raise TypeError("payload must be a LaterChannelPayload")
        credit = payload.credit
        feedback = payload.feedback
        if payload.namespace != self.namespace:
            raise ValueError("later channel namespace does not match adapter")
        if payload.target_outcome_id != credit.later_outcome_id:
            raise ValueError("target outcome id does not match delayed credit")
        if not payload.assignment_consumed or not payload.selection_matches_assignment:
            raise ValueError("assignment was not consumed by the matching target selection")
        subject = self._evidence_subjects.get(credit.source_evidence_id)
        if subject is None:
            raise ValueError("delayed credit references unpublished evidence")
        if subject != payload.assignment_candidate_key:
            raise ValueError("assignment candidate does not match evidence subject")
        previous = self._applied_assignments.get(credit.assignment_id)
        credit_digest = _digest(asdict(credit))
        feedback_digest = _digest(asdict(feedback))
        if previous is not None:
            if (previous["credit_digest"] == credit_digest
                    and previous["feedback_id"] == feedback.feedback_id
                    and previous.get("feedback_digest") == feedback_digest):
                return "NOOP_DUPLICATE"
            raise ValueError("an assignment already has a different delayed outcome")
        if feedback.source not in self.policy.accepted_sources:
            raise ValueError("feedback channel is not accepted by this policy")
        if feedback.source_event_id not in getattr(self.policy, "_decisions", {}):
            raise ValueError("feedback must reference a known target policy selection")
        selected = self.policy._decisions[feedback.source_event_id]  # internal seam, guarded by this adapter
        if selected.chosen.key != payload.assignment_candidate_key:
            raise ValueError("target selection chose a different candidate")
        if feedback.source_event_id == credit.source_evidence_id:
            raise ValueError("source evidence id cannot stand in for target selection id")
        before = self._state_digest()
        before_updates = int(self.policy.updates)
        policy_before = self.policy.snapshot()
        ledger_before = dict(self._credit_ledger.credits)
        assignments_before = dict(self._applied_assignments)

        def updater(_: LaterCredit) -> None:
            changed = self.policy.observe_feedback(feedback)
            if not changed:
                raise ValueError("later feedback did not produce an eligible policy update")

        try:
            self._credit_ledger.apply_once(
                credit,
                updater,
                snapshot=lambda: self.policy.snapshot(),
                restore=lambda state: self._restore_policy_snapshot(state),
            )
            if int(self.policy.updates) <= before_updates or self._state_digest() == before:
                raise AssertionError("valid later credit did not change policy state")
            self._applied_assignments[credit.assignment_id] = {
                "credit_digest": credit_digest,
                "feedback_id": feedback.feedback_id,
                "feedback_digest": feedback_digest,
                "later_outcome_id": credit.later_outcome_id,
            }
            self._check_capacity()
        except Exception:
            self._restore_policy_snapshot(policy_before)
            self._credit_ledger.credits = ledger_before
            self._applied_assignments = assignments_before
            raise
        return "UPDATED_ONCE"

    def _restore_policy_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        restored = BaselinePolicy.restore(snapshot)
        self.policy.__dict__.clear()
        self.policy.__dict__.update(restored.__dict__)

    def snapshot(self) -> dict[str, Any]:
        payload = self._snapshot_payload()
        self._check_capacity()
        return payload

    @classmethod
    def restore(cls, payload: Mapping[str, Any]) -> "DelayedPolicyAdapter":
        if payload.get("version") != VERSION:
            raise ValueError("unsupported delayed adapter snapshot version")
        policy = BaselinePolicy.restore(payload["policy"])
        adapter = cls(
            policy,
            namespace=str(payload["namespace"]),
            state_cap_bytes=int(payload["state_cap_bytes"]),
        )
        adapter._offers = {str(key): dict(value) for key, value in dict(payload.get("offers", {})).items()}
        adapter._evidence_subjects = {str(key): str(value) for key, value in dict(payload.get("evidence_subjects", {})).items()}
        adapter._applied_assignments = {
            str(key): {str(k): str(v) for k, v in dict(value).items()}
            for key, value in dict(payload.get("applied_assignments", {})).items()
        }
        for key, raw in dict(payload.get("credit_ledger", {}).get("credits", {})).items():
            adapter._credit_ledger.credits[str(key)] = LaterCredit(**dict(raw))
        adapter._check_capacity()
        return adapter


__all__ = ["DelayedPolicyAdapter", "LaterChannelPayload", "PublishReceipt", "VERSION"]
