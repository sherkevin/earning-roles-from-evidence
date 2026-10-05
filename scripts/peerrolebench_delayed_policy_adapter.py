"""Candidate adapter for the method v1.1 publish/update separation.

The adapter is intentionally policy-agnostic at the evidence boundary.  A
published :class:`RoleEvidenceOffer` is an immutable public input and never
becomes a ``Feedback`` row.  Only a later target channel that passes the
strict ``validate_later`` replay/binding path (``recipient_judgment`` or
``terminal_outcome``) can reach the wrapped policy.  The lower-level
``apply_later_credit`` method remains a policy-side seam for unit tests.

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
from peerrolebench_ledger_replay import replay_ledger_events
from peerrolebench_peer_history import HistoryEntryV1
from peerrolebench_peer_history_binding import HistoryBindingReceiptV1, build_history_binding_receipt
from peerrolebench_role_evidence_offer import (
    RoleEvidenceOffer, build_role_evidence_from_ledger,
)
from peerrolebench_role_evidence_scorer import JUDGMENT_LABELS
from peerrolebench_two_stage_gate import (
    DelayedCreditLedger, LaterCredit, SourceGate, derive_later_credit_from_ledger,
)


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


@dataclass(frozen=True)
class ValidatedLaterCredit:
    """Canonical replay receipt accepted by the strict update entry point."""

    channel: LaterChannelPayload
    binding_receipt: HistoryBindingReceiptV1
    replay_status: str
    replay_digest: str
    target_selection_id: str


def _ledger_digest(events: Any) -> str:
    return _digest(list(events))


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
            "offer": offer.operator_binding_payload(),
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

    def publish_from_ledger(self, offer: RoleEvidenceOffer, *, ledger: Any,
                            source_gate: SourceGate) -> PublishReceipt:
        """Validate public evidence against a complete canonical source ledger.

        Responsibility eligibility is still supplied by the versioned
        ``SourceGate`` produced by the scorer/action layer; this method adds
        the independent replay and evidence-row/artifact lineage checks before
        the policy-side publication store is touched.
        """
        replay = replay_ledger_events(getattr(ledger, "events", ()))
        if replay.status != "PASS" or not replay.complete:
            raise ValueError("source ledger replay is not complete")
        for row in offer.public_evidence:
            canonical = build_role_evidence_from_ledger(
                ledger=replay.ledger, evidence_id=str(row["evidence_id"]),
                candidate_key=str(row["candidate_key"]), role=offer.role,
                target_task_index=int(offer.task_index),
                evidence_version=offer.evidence_version,
                available_index=int(row["available_index"]),
            )
            if canonical.payload() != dict(row):
                raise ValueError("public evidence row does not match canonical source ledger")
        return self.publish(offer, source_gate=source_gate)

    def validate_later(
        self, *, ledger: Any, source_gate: SourceGate, role_offer: RoleEvidenceOffer,
        target_assignment: Any, target_selection: Any, evidence_candidate_id: str,
        later_outcome_id: str, history_entry: HistoryEntryV1,
        assignment_read_cut: int, target_decision_index: int,
        target_arrival_index: int, candidate_registry_digest: str,
        target_policy_event_id: str, feedback: Feedback,
    ) -> ValidatedLaterCredit:
        """Derive a later credit only from a replayed, bound canonical ledger."""
        if not source_gate.evidence_publish_allowed or source_gate.policy_update_allowed:
            raise ValueError("source gate is not eligible for later credit")
        if role_offer.candidate_registry_digest != candidate_registry_digest:
            raise ValueError("role offer and later binding registry differ")
        replay = replay_ledger_events(getattr(ledger, "events", ()))
        if replay.status != "PASS" or not replay.complete:
            raise ValueError("later ledger replay is not complete")
        credit = derive_later_credit_from_ledger(
            ledger=replay.ledger, source_gate=source_gate,
            assignment_id=str(target_assignment.assignment_id),
            source_evidence_id=str(role_offer.evidence_ids[0]),
            evidence_candidate_id=str(evidence_candidate_id),
            later_outcome_id=str(later_outcome_id),
        )
        if credit is None:
            raise ValueError("canonical later credit lineage is invalid")
        binding = build_history_binding_receipt(
            entry=history_entry, ledger=replay.ledger, offer=role_offer,
            target_assignment=target_assignment, target_selection=target_selection,
            target_outcome_id=str(later_outcome_id),
            assignment_read_cut=int(assignment_read_cut),
            target_decision_index=int(target_decision_index),
            target_arrival_index=int(target_arrival_index),
            candidate_key=str(evidence_candidate_id),
            candidate_registry_digest=str(candidate_registry_digest),
            later_credit_digest=credit.credit_digest,
        )
        if binding.history_status not in {"PASS", "FAIL"}:
            raise ValueError("later history binding is UNKNOWN")
        if binding.later_credit_digest != credit.credit_digest:
            raise ValueError("history binding does not contain the derived credit digest")
        decisions = getattr(self.policy, "_decisions", {})
        selected = decisions.get(str(target_policy_event_id))
        if selected is None:
            raise ValueError("target policy selection is missing")
        if selected.chosen.key != str(evidence_candidate_id):
            raise ValueError("target policy selection chose a different candidate")
        if feedback.source_event_id != str(target_policy_event_id):
            raise ValueError("feedback must reference the target policy selection")
        target_outcome = replay.ledger.outcomes.get(str(later_outcome_id))
        if target_outcome is None:
            raise ValueError("target outcome is missing after replay")
        target_delivery = replay.ledger.deliveries.get(target_outcome.delivery_id)
        if target_delivery is None:
            raise ValueError("target delivery is missing after replay")
        target_judgment = next(
            (item for item in replay.ledger.judgments.values() if item.delivery_id == target_delivery.delivery_id),
            None,
        )
        if feedback.source == "recipient_judgment":
            if target_judgment is None or target_judgment.decision not in JUDGMENT_LABELS:
                raise ValueError("target recipient judgment has no registered label")
            if feedback.label is None or abs(float(feedback.label) - JUDGMENT_LABELS[target_judgment.decision]) > 1e-12:
                raise ValueError("feedback label does not match target recipient judgment")
        elif feedback.source == "terminal_outcome":
            expected = target_outcome.partial_score
            if expected is None:
                expected = 1.0 if target_outcome.success else 0.0
            if feedback.label is None or abs(float(feedback.label) - float(expected)) > 1e-12:
                raise ValueError("feedback label does not match target terminal outcome")
        else:
            raise ValueError("later feedback source is not a canonical target channel")
        channel = LaterChannelPayload(
            credit=credit, feedback=feedback, target_outcome_id=str(later_outcome_id),
            assignment_candidate_key=str(evidence_candidate_id), namespace=self.namespace,
            assignment_consumed=True, selection_matches_assignment=True,
        )
        return ValidatedLaterCredit(
            channel=channel, binding_receipt=binding, replay_status=replay.status,
            replay_digest=_ledger_digest(replay.ledger.events),
            target_selection_id=str(target_selection.selection_id),
        )

    def apply_validated_later_credit(self, validated: ValidatedLaterCredit) -> str:
        """Apply only a receipt produced by :meth:`validate_later`."""
        if not isinstance(validated, ValidatedLaterCredit):
            raise TypeError("validated must be a ValidatedLaterCredit")
        if validated.replay_status != "PASS" or not validated.binding_receipt.later_credit_digest:
            raise ValueError("validated later credit lacks complete replay/binding")
        if validated.binding_receipt.later_credit_digest != validated.channel.credit.credit_digest:
            raise ValueError("validated binding and credit digest differ")
        return self.apply_later_credit(validated.channel)

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
        credit_digest = credit.credit_digest
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
        return {**payload, "snapshot_digest": _digest(payload)}

    @classmethod
    def restore(cls, payload: Mapping[str, Any]) -> "DelayedPolicyAdapter":
        if payload.get("version") != VERSION:
            raise ValueError("unsupported delayed adapter snapshot version")
        raw = dict(payload)
        snapshot_digest = raw.pop("snapshot_digest", None)
        if not isinstance(snapshot_digest, str) or snapshot_digest != _digest(raw):
            raise ValueError("delayed adapter snapshot digest is invalid")
        policy = BaselinePolicy.restore(payload["policy"])
        adapter = cls(
            policy,
            namespace=str(payload["namespace"]),
            state_cap_bytes=int(payload["state_cap_bytes"]),
        )
        offers: dict[str, dict[str, Any]] = {}
        derived_subjects: dict[str, str] = {}
        for key, value in dict(payload.get("offers", {})).items():
            raw_value = dict(value)
            raw_offer = dict(raw_value.get("offer", {}))
            bundle_payload = dict(raw_offer)
            bundle_payload.pop("offer_record_hash", None)
            bundle_digest = _digest(bundle_payload)
            raw_offer.pop("schema", None)
            raw_offer["bundle_digest"] = bundle_digest
            try:
                offer = RoleEvidenceOffer(**raw_offer)
            except Exception as exc:
                raise ValueError("delayed adapter snapshot contains an invalid role offer") from exc
            if _digest(offer.operator_binding_payload()) != raw_value.get("offer_digest"):
                raise ValueError("delayed adapter offer digest is invalid")
            state_digest = raw_value.get("state_digest")
            if (not isinstance(state_digest, str) or len(state_digest) != 64
                    or any(char not in "0123456789abcdef" for char in state_digest)
                    or int(raw_value.get("policy_updates", -1)) < 0):
                raise ValueError("delayed adapter offer state receipt is invalid")
            for row in offer.public_evidence:
                evidence_id = str(row["evidence_id"])
                if evidence_id in derived_subjects:
                    raise ValueError("delayed adapter snapshot contains duplicate evidence")
                derived_subjects[evidence_id] = str(row["candidate_key"])
            offers[str(key)] = raw_value
        if derived_subjects != {str(key): str(value) for key, value in dict(payload.get("evidence_subjects", {})).items()}:
            raise ValueError("delayed adapter evidence subject index is inconsistent")
        adapter._offers = offers
        adapter._evidence_subjects = derived_subjects
        adapter._applied_assignments = {
            str(key): {str(k): str(v) for k, v in dict(value).items()}
            for key, value in dict(payload.get("applied_assignments", {})).items()
        }
        for key, raw_credit in dict(payload.get("credit_ledger", {}).get("credits", {})).items():
            credit = LaterCredit(**dict(raw_credit))
            expected_key = f"{credit.assignment_id}\x1f{credit.later_outcome_id}"
            rebuilt = LaterCredit.build(
                assignment_id=credit.assignment_id,
                source_evidence_id=credit.source_evidence_id,
                later_outcome_id=credit.later_outcome_id,
                later_quality=credit.later_quality,
            )
            if str(key) != expected_key or rebuilt.credit_digest != credit.credit_digest:
                raise ValueError("delayed adapter credit ledger integrity is invalid")
            adapter._credit_ledger.credits[expected_key] = credit
        for assignment_id, record in adapter._applied_assignments.items():
            matching = [credit for credit in adapter._credit_ledger.credits.values()
                        if credit.assignment_id == assignment_id]
            if len(matching) != 1 or record.get("credit_digest") != matching[0].credit_digest:
                raise ValueError("delayed adapter assignment index is inconsistent")
            if not record.get("feedback_id") or not record.get("feedback_digest"):
                raise ValueError("delayed adapter assignment receipt is incomplete")
        adapter._check_capacity()
        return adapter


__all__ = [
    "DelayedPolicyAdapter", "LaterChannelPayload", "PublishReceipt", "ValidatedLaterCredit", "VERSION",
]
