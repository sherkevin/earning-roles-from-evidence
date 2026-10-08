"""Offline PIPE3 assignment runner boundary.

The runner is deliberately a small state machine around the already qualified
``MetaTeamAssignmentOffer``/attestation contract.  It performs no model, API,
or GPU work; its purpose is to make the selection -> task-start boundary
auditable and replayable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from peerrolebench_metateam_profile_sidecar import (
    MetaTeamAssignmentAttestation,
    MetaTeamAssignmentOffer,
    bind_assignment_to_selection,
)
from peerrolebench_isolated_policy_read import read_profiles_isolated


@dataclass
class Pipe3AssignmentRunner:
    offer: MetaTeamAssignmentOffer
    policy_read_trace_mode: str = "recorded_public_input_digest"
    isolated_policy_trace: bool = False

    def __post_init__(self) -> None:
        self.state = "created"
        self.trace: list[dict[str, Any]] = []
        self.attestation: MetaTeamAssignmentAttestation | None = None
        self.selection: Any | None = None
        self.task_start_event: Any | None = None
        self._profile_digests = {p.profile_id: p.profile_digest for p in self.offer.profiles}

    def _record(self, event: str, status: str = "accepted", **extra: Any) -> None:
        self.trace.append({
            "seq": len(self.trace), "event": event, "status": status,
            "offer_id": self.offer.offer_id,
            "offer_digest": self.offer.offer_digest,
            "policy_input_digest": self.attestation.policy_input_digest if self.attestation else None,
            "policy_read_trace_mode": self.policy_read_trace_mode,
            "isolated_policy_trace": self.isolated_policy_trace,
            **extra,
        })

    def _reject(self, event: str, reason: str) -> None:
        self._record(event, "rejected", reason=reason)
        raise ValueError(reason)

    def emit_offer(self) -> MetaTeamAssignmentOffer:
        if self.state != "created":
            self._reject("offer_emitted", "offer already emitted")
        self.state = "offer_emitted"
        self._record("offer_emitted", profile_ids=[p.profile_id for p in self.offer.profiles])
        return self.offer

    def consume_profiles(
        self, profile_ids: tuple[str, ...], *, isolated_policy_read: bool = False,
    ) -> MetaTeamAssignmentAttestation:
        if self.attestation is not None:
            self._reject("profile_consumed", "duplicate profile consumption")
        if self.state != "offer_emitted":
            self._reject("profile_consumed", "profile consumption requires emitted offer")
        # Verify the records still match the sealed offer before constructing a
        # consumption proof.  This catches post-offer profile replacement.
        current = {p.profile_id: p.profile_digest for p in self.offer.profiles}
        if current != self._profile_digests:
            self._reject("profile_consumed", "profile mutation detected")
        try:
            attestation = self.offer.attest_consumption(profile_ids)
            isolated_trace = None
            if isolated_policy_read:
                isolated_trace = read_profiles_isolated(
                    self.offer, profile_ids, read_cut=self.offer.read_cut,
                )
        except ValueError as exc:
            self._reject("profile_consumed", str(exc))
        self.attestation = attestation
        if isolated_trace is not None:
            self.policy_read_trace_mode = "isolated_process_public_digest"
            self.isolated_policy_trace = True
        self.state = "profile_consumed"
        self._record(
            "profile_consumed", profile_ids=list(profile_ids),
            isolated_read=(isolated_trace.__dict__ if isolated_trace is not None else None),
        )
        return self.attestation

    def seal_selection(self, selection: Any, attestation: MetaTeamAssignmentAttestation | None = None) -> None:
        if self.state != "profile_consumed" or self.attestation is None:
            self._reject("selection_sealed", "selection requires consumed attestation")
        if attestation is None:
            self._reject("selection_sealed", "missing attestation")
        if attestation != self.attestation:
            self._reject("selection_sealed", "attestation does not match consumed proof")
        try:
            bind_assignment_to_selection(self.offer, attestation, selection)
        except ValueError as exc:
            self._reject("selection_sealed", str(exc))
        self.selection = selection
        self.state = "selection_sealed"
        self._record("selection_sealed", task_index=getattr(selection, "task_index", None))

    def start_task(self, ledger: Any | None = None) -> None:
        """Cross the assignment -> task-start seam.

        When a PIPE3 ``PeerRoleLedger`` is supplied, append the native
        ``task_start`` event at the same decision index that was bound by the
        assignment attestation.  The ledger is deliberately duck-typed so the
        offline boundary does not import or execute the episode runner.  This
        method only records the protocol event; source dispatch, scoring,
        action execution, and outcome production remain downstream gates.
        """
        if self.state != "selection_sealed":
            self._reject("task_started", "task start requires sealed selection")
        if ledger is not None:
            if not hasattr(ledger, "record_task_start"):
                self._reject("task_started", "ledger lacks record_task_start")
            ledger.record_task_start(self.offer.task_id, self.offer.decision_index)
            self.task_start_event = ledger.events[-1] if hasattr(ledger, "events") else None
        self.state = "task_started"
        self._record("task_started", task_id=self.offer.task_id,
                     task_index=self.offer.decision_index,
                     ledger_record_hash=(self.task_start_event or {}).get("record_hash")
                     if isinstance(self.task_start_event, dict) else None)
