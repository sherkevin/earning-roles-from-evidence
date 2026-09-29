"""Information-boundary contract for a Meta-Team-style public profile adapter.

This module does not implement Meta-Team's reflection model and makes no
quality claim.  It only validates the smallest public profile record that a
future ``MetaTeam-L2-public`` adapter may emit.  The record is derived from a
selected ArtifactRole interaction and can be consumed only after its public
arrival watermark.  Terminal scores, raw trajectories, hidden scorer fields,
and other policy state are intentionally absent.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Mapping

PROFILE_SCHEMA = "metateam-profile-v1"
PROFILE_ADAPTER_VERSION = "metateam-l2-public-sidecar-v1"
ATTESTATION_VERSION = "metateam-profile-consumption-v1"
PROFILE_VARIANTS = frozenset({"public", "original_info", "ablation_profile_only"})
RELIABILITY = frozenset({"high", "medium", "low", "unknown"})
PROFILE_FIELDS = frozenset({
    "reliability", "strengths", "weaknesses", "communication_style", "notes",
})
PUBLIC_INPUT_FIELDS = frozenset({
    "feedback_id", "source_event_id", "source", "candidate_key", "evidence_version",
    "source_index", "arrival_index", "arrived_at", "delay", "action", "disposition",
    "provenance", "label", "supersedes", "unknown_reason",
})
FORBIDDEN_PUBLIC_FIELDS = frozenset({
    "terminal_score", "final_outcome", "hidden_score", "hidden_label",
    "raw_trace", "trajectory", "operator_ledger", "private_scorer",
    "policy_state", "other_policy_state", "future_result",
})


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value != value.lower():
        raise ValueError(f"{name} must be a SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a SHA-256 digest") from exc
    return value


def _text(value: Any, name: str, *, max_chars: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_chars:
        raise ValueError(f"{name} must be non-empty text of at most {max_chars} characters")
    return value


def _tuple_text(value: Any, name: str, *, max_items: int, max_chars: int) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or len(value) > max_items:
        raise ValueError(f"{name} must have at most {max_items} items")
    result = tuple(_text(item, f"{name} item", max_chars=max_chars) for item in value)
    if len(set(result)) != len(result):
        raise ValueError(f"{name} must not contain duplicates")
    return result


def _nonnegative_int(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _attestation_payload(
    *, profile_id: str, profile_digest: str, candidate_key: str,
    source_decision_index: int, available_index: int,
    decision_index: int, read_cut: int, consumed: bool,
) -> dict[str, Any]:
    return {
        "attestation_version": ATTESTATION_VERSION,
        "profile_id": profile_id,
        "profile_digest": profile_digest,
        "candidate_key": candidate_key,
        "source_decision_index": source_decision_index,
        "available_index": available_index,
        "decision_index": decision_index,
        "read_cut": read_cut,
        "consumed": consumed,
    }


@dataclass(frozen=True)
class MetaTeamProfile:
    """A bounded qualitative profile visible to a future selector.

    ``profile`` follows the qualitative fields in the inspected Meta-Team L2
    protocol.  The source is represented by a digest of the public event
    bundle, rather than by hidden trajectory text or a terminal grader result.
    """

    profile_id: str
    profile_revision: int
    adapter_variant: str
    candidate_key: str
    producer_id: str
    producer_version: str
    recipient_id: str
    selected_candidate_key: str
    selection_event_id: str
    source_event_id: str
    delivery_id: str
    source_decision_index: int
    source_arrival_index: int
    available_index: int
    source_disposition: str
    source_provenance: str
    source_input_digest: str
    profile_schema: str
    parser_version: str
    model_config_digest: str
    profile: Mapping[str, Any]
    supersedes_profile_id: str | None = None
    sidecar_version: str = PROFILE_ADAPTER_VERSION

    def __post_init__(self) -> None:
        required = (
            self.profile_id, self.candidate_key, self.producer_id, self.producer_version,
            self.recipient_id, self.selected_candidate_key, self.selection_event_id,
            self.source_event_id, self.delivery_id,
            self.profile_schema, self.parser_version,
        )
        if not all(isinstance(value, str) and value for value in required):
            raise ValueError("profile identity and schema fields are required")
        if self.sidecar_version != PROFILE_ADAPTER_VERSION:
            raise ValueError("unsupported Meta-Team profile sidecar version")
        if self.adapter_variant not in PROFILE_VARIANTS:
            raise ValueError("unsupported Meta-Team profile adapter variant")
        _nonnegative_int(self.profile_revision, "profile_revision")
        if self.profile_revision == 0:
            raise ValueError("profile_revision starts at one")
        if self.profile_revision == 1 and self.supersedes_profile_id is not None:
            raise ValueError("first profile revision cannot supersede another profile")
        if self.profile_revision > 1 and self.supersedes_profile_id is None:
            raise ValueError("later profile revisions require supersedes_profile_id")
        if self.selected_candidate_key != self.candidate_key:
            raise ValueError("profile must bind to the selected candidate")
        if self.profile_schema != PROFILE_SCHEMA:
            raise ValueError("unsupported profile schema")
        _nonnegative_int(self.source_decision_index, "source_decision_index")
        _nonnegative_int(self.source_arrival_index, "source_arrival_index")
        _nonnegative_int(self.available_index, "available_index")
        if self.source_arrival_index > self.available_index:
            raise ValueError("profile cannot be available before its source arrival")
        if self.source_disposition != "eligible" or self.source_provenance != "public":
            raise ValueError("profile may only be built from eligible public feedback")
        _sha(self.source_input_digest, "source_input_digest")
        _sha(self.model_config_digest, "model_config_digest")
        if self.supersedes_profile_id is not None:
            if not self.supersedes_profile_id or self.supersedes_profile_id == self.profile_id:
                raise ValueError("supersedes_profile_id must name a different profile")
        if not isinstance(self.profile, Mapping):
            raise ValueError("profile must be a mapping")
        keys = set(self.profile)
        if keys != PROFILE_FIELDS:
            raise ValueError("profile keys must exactly match the fixed Meta-Team schema")
        reliability = self.profile["reliability"]
        if reliability not in RELIABILITY:
            raise ValueError("profile reliability is outside the fixed enum")
        _tuple_text(self.profile["strengths"], "strengths", max_items=5, max_chars=240)
        _tuple_text(self.profile["weaknesses"], "weaknesses", max_items=5, max_chars=240)
        _text(self.profile["communication_style"], "communication_style", max_chars=400)
        _tuple_text(self.profile["notes"], "notes", max_items=3, max_chars=240)
        # Refuse accidental embedding of hidden or post-hoc objects in a
        # qualitative field.  Actual semantic validation remains a later gate.
        for value in self.profile.values():
            if isinstance(value, Mapping) or isinstance(value, set):
                raise ValueError("profile values must be bounded scalar/list fields")
        object.__setattr__(self, "profile", MappingProxyType({
            "reliability": reliability,
            "strengths": tuple(self.profile["strengths"]),
            "weaknesses": tuple(self.profile["weaknesses"]),
            "communication_style": self.profile["communication_style"],
            "notes": tuple(self.profile["notes"]),
        }))

    def payload(self) -> dict[str, Any]:
        return {
            "sidecar_version": self.sidecar_version,
            "profile_id": self.profile_id,
            "profile_revision": self.profile_revision,
            "adapter_variant": self.adapter_variant,
            "candidate_key": self.candidate_key,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "recipient_id": self.recipient_id,
            "selected_candidate_key": self.selected_candidate_key,
            "selection_event_id": self.selection_event_id,
            "source_event_id": self.source_event_id,
            "delivery_id": self.delivery_id,
            "source_decision_index": self.source_decision_index,
            "source_arrival_index": self.source_arrival_index,
            "available_index": self.available_index,
            "source_disposition": self.source_disposition,
            "source_provenance": self.source_provenance,
            "source_input_digest": self.source_input_digest,
            "profile_schema": self.profile_schema,
            "parser_version": self.parser_version,
            "model_config_digest": self.model_config_digest,
            "profile": {
                "reliability": self.profile["reliability"],
                "strengths": list(self.profile["strengths"]),
                "weaknesses": list(self.profile["weaknesses"]),
                "communication_style": self.profile["communication_style"],
                "notes": list(self.profile["notes"]),
            },
            **({"supersedes_profile_id": self.supersedes_profile_id}
               if self.supersedes_profile_id is not None else {}),
        }

    @property
    def profile_digest(self) -> str:
        return _digest(self.payload())

    def consume_before(self, *, decision_index: int, read_cut: int) -> "ProfileConsumptionAttestation":
        payload = _attestation_payload(
            profile_id=self.profile_id, profile_digest=self.profile_digest,
            candidate_key=self.candidate_key, source_decision_index=self.source_decision_index,
            available_index=self.available_index, decision_index=decision_index,
            read_cut=read_cut, consumed=True,
        )
        return ProfileConsumptionAttestation(
            profile_id=self.profile_id,
            profile_digest=self.profile_digest,
            candidate_key=self.candidate_key,
            source_decision_index=self.source_decision_index,
            available_index=self.available_index,
            decision_index=decision_index,
            read_cut=read_cut,
            consumed=True,
            attestation_digest=_digest(payload),
        )


@dataclass(frozen=True)
class ProfileConsumptionAttestation:
    """Evidence that a later assignment could see only an arrived profile."""

    profile_id: str
    profile_digest: str
    candidate_key: str
    source_decision_index: int
    available_index: int
    decision_index: int
    read_cut: int
    consumed: bool
    attestation_digest: str

    def __post_init__(self) -> None:
        if not self.profile_id or not self.candidate_key:
            raise ValueError("profile_id and candidate_key are required")
        _sha(self.profile_digest, "profile_digest")
        for name, value in (
            ("source_decision_index", self.source_decision_index),
            ("available_index", self.available_index),
            ("decision_index", self.decision_index),
            ("read_cut", self.read_cut),
        ):
            _nonnegative_int(value, name)
        if self.consumed:
            if self.decision_index <= self.source_decision_index:
                raise ValueError("profile consumption must target a later decision")
            if self.read_cut < self.available_index:
                raise ValueError("profile is not visible at this read cut")
            if self.read_cut > self.decision_index:
                raise ValueError("profile read cut is after the decision")
        _sha(self.attestation_digest, "attestation_digest")
        if self.attestation_digest != _digest(self.payload()):
            raise ValueError("attestation_digest does not match canonical payload")

    def payload(self) -> dict[str, Any]:
        return _attestation_payload(
            profile_id=self.profile_id, profile_digest=self.profile_digest,
            candidate_key=self.candidate_key, source_decision_index=self.source_decision_index,
            available_index=self.available_index, decision_index=self.decision_index,
            read_cut=self.read_cut, consumed=self.consumed,
        )

    def with_digest(self) -> "ProfileConsumptionAttestation":
        payload = self.payload()
        return ProfileConsumptionAttestation(
            profile_id=self.profile_id,
            profile_digest=self.profile_digest,
            candidate_key=self.candidate_key,
            source_decision_index=self.source_decision_index,
            available_index=self.available_index,
            decision_index=self.decision_index,
            read_cut=self.read_cut,
            consumed=self.consumed,
            attestation_digest=_digest(payload),
        )


def reject_private_public_input(payload: Mapping[str, Any]) -> None:
    """Reject a would-be public adapter input containing hidden/post-hoc keys."""
    keys = set(payload)
    forbidden = keys & FORBIDDEN_PUBLIC_FIELDS
    if forbidden:
        raise ValueError(f"public Meta-Team adapter input contains forbidden fields: {sorted(forbidden)}")
    unknown = keys - PUBLIC_INPUT_FIELDS
    if unknown:
        raise ValueError(f"public Meta-Team adapter input contains unknown fields: {sorted(unknown)}")
    if "raw_trace" in payload or "trajectory" in payload:
        raise ValueError("full trajectory is not part of the public adapter input")


def build_public_profile_fixture(
    *,
    selection: Any,
    feedback_sidecar: Any,
    public_projection: Any,
    profile_id: str,
    profile_revision: int,
    profile: Mapping[str, Any],
    parser_version: str,
    model_config_digest: str,
    available_index: int | None = None,
    supersedes_profile_id: str | None = None,
) -> MetaTeamProfile:
    """Build a deterministic public profile record from typed sidecars.

    This is a *fixture builder*, not the Meta-Team reflection model.  The
    caller supplies the already-produced qualitative profile so this function
    can qualify source binding and replay without making an LLM call.  A live
    adapter must replace that input with a separately metered summarizer and
    keep the same public payload and digest contract.
    """
    if getattr(public_projection, "source", None) != "recipient_judgment":
        raise ValueError("Meta-Team-L2-public profile requires recipient judgment")
    if getattr(public_projection, "disposition", None) != "eligible" or getattr(public_projection, "provenance", None) != "public":
        raise ValueError("Meta-Team-L2-public profile requires eligible public projection")
    chosen = selection.candidates[selection.chosen_index]
    candidate_key = chosen.key
    if getattr(public_projection, "candidate_key", None) != candidate_key:
        raise ValueError("profile source is not the selected candidate")
    for name in ("selection_event_id", "source_event_id", "delivery_id", "producer_id", "producer_version", "recipient_id"):
        if getattr(feedback_sidecar, name, None) is None:
            raise ValueError(f"feedback sidecar is missing {name}")
    if feedback_sidecar.selection_event_id != selection.protocol_event_id:
        raise ValueError("feedback and selection protocol events do not match")
    if feedback_sidecar.source_event_id != public_projection.source_event_id:
        raise ValueError("projection and feedback source events do not match")
    arrival_index = getattr(public_projection, "arrival_index", None)
    if type(arrival_index) is not int or arrival_index < 0:
        raise ValueError("public projection requires arrival_index")
    if available_index is None:
        available_index = arrival_index
    _nonnegative_int(available_index, "available_index")
    if available_index < arrival_index:
        raise ValueError("profile availability cannot precede public feedback arrival")
    public_input = {
        "selection_event_id": selection.protocol_event_id,
        "selection_event": selection.event_id,
        "candidate_key": candidate_key,
        "feedback": public_projection.public_payload(),
        "producer_id": feedback_sidecar.producer_id,
        "producer_version": feedback_sidecar.producer_version,
        "recipient_id": feedback_sidecar.recipient_id,
        "delivery_id": feedback_sidecar.delivery_id,
    }
    source_input_digest = _digest(public_input)
    return MetaTeamProfile(
        profile_id=profile_id,
        profile_revision=profile_revision,
        adapter_variant="public",
        candidate_key=candidate_key,
        producer_id=feedback_sidecar.producer_id,
        producer_version=feedback_sidecar.producer_version,
        recipient_id=feedback_sidecar.recipient_id,
        selected_candidate_key=candidate_key,
        selection_event_id=selection.protocol_event_id,
        source_event_id=public_projection.source_event_id,
        delivery_id=feedback_sidecar.delivery_id,
        source_decision_index=selection.task_index,
        source_arrival_index=arrival_index,
        available_index=available_index,
        source_disposition=public_projection.disposition,
        source_provenance=public_projection.provenance,
        source_input_digest=source_input_digest,
        profile_schema=PROFILE_SCHEMA,
        parser_version=parser_version,
        model_config_digest=model_config_digest,
        profile=profile,
        supersedes_profile_id=supersedes_profile_id,
    )


def replay_public_profile_fixture(
    profile: MetaTeamProfile,
    *,
    selection: Any,
    feedback_sidecar: Any,
    public_projection: Any,
) -> MetaTeamProfile:
    """Reconstruct and verify a public profile from its source sidecars.

    The replay deliberately reuses the recorded profile payload and versioned
    parser/model digests.  It does not call a summarizer.  A future live
    runner must run this check after replacing the fixture profile with a
    metered public-only generator.
    """
    replayed = build_public_profile_fixture(
        selection=selection, feedback_sidecar=feedback_sidecar,
        public_projection=public_projection, profile_id=profile.profile_id,
        profile_revision=profile.profile_revision, profile=profile.profile,
        parser_version=profile.parser_version, model_config_digest=profile.model_config_digest,
        available_index=profile.available_index,
        supersedes_profile_id=profile.supersedes_profile_id,
    )
    if replayed.profile_digest != profile.profile_digest:
        raise ValueError("profile replay digest does not match sealed profile")
    return replayed


@dataclass(frozen=True)
class MetaTeamAssignmentOffer:
    """Public candidate/profile bundle available before a later assignment."""

    offer_id: str
    task_id: str
    decision_index: int
    read_cut: int
    candidate_keys: tuple[str, ...]
    profiles: tuple[MetaTeamProfile, ...]
    offer_digest: str
    watermark_schema: str = "global-event-index-v1"

    def __post_init__(self) -> None:
        if not self.offer_id or not self.task_id:
            raise ValueError("assignment offer identity is required")
        _nonnegative_int(self.decision_index, "decision_index")
        _nonnegative_int(self.read_cut, "read_cut")
        if self.read_cut > self.decision_index:
            raise ValueError("assignment offer read cut is after the decision")
        if not self.candidate_keys or len(set(self.candidate_keys)) != len(self.candidate_keys):
            raise ValueError("candidate keys must be non-empty and unique")
        if self.watermark_schema != "global-event-index-v1":
            raise ValueError("unsupported watermark schema")
        profile_ids = set()
        profile_candidates = set()
        for profile in self.profiles:
            if not isinstance(profile, MetaTeamProfile):
                raise ValueError("assignment profiles must be MetaTeamProfile records")
            if profile.profile_id in profile_ids or profile.candidate_key in profile_candidates:
                raise ValueError("assignment profiles must be unique")
            if profile.candidate_key not in self.candidate_keys:
                raise ValueError("assignment profile candidate is outside the menu")
            if profile.available_index > self.read_cut:
                raise ValueError("assignment offer contains a profile after its read cut")
            if profile.source_decision_index >= self.decision_index:
                raise ValueError("assignment profile is not from an earlier decision")
            profile_ids.add(profile.profile_id)
            profile_candidates.add(profile.candidate_key)
        _sha(self.offer_digest, "offer_digest")
        if self.offer_digest != _digest(self.payload()):
            raise ValueError("offer_digest does not match canonical payload")

    def payload(self) -> dict[str, Any]:
        return {
            "offer_id": self.offer_id,
            "task_id": self.task_id,
            "decision_index": self.decision_index,
            "read_cut": self.read_cut,
            "candidate_keys": list(self.candidate_keys),
            "profiles": [profile.payload() for profile in self.profiles],
            "watermark_schema": self.watermark_schema,
        }

    @classmethod
    def build(
        cls, *, offer_id: str, task_id: str, decision_index: int, read_cut: int,
        candidate_keys: tuple[str, ...], profiles: tuple[MetaTeamProfile, ...],
    ) -> "MetaTeamAssignmentOffer":
        provisional = {
            "offer_id": offer_id, "task_id": task_id,
            "decision_index": decision_index, "read_cut": read_cut,
            "candidate_keys": list(candidate_keys),
            "profiles": [profile.payload() for profile in profiles],
            "watermark_schema": "global-event-index-v1",
        }
        return cls(
            offer_id=offer_id, task_id=task_id, decision_index=decision_index,
            read_cut=read_cut, candidate_keys=candidate_keys, profiles=profiles,
            offer_digest=_digest(provisional),
        )

    def attest_consumption(self, profile_ids: tuple[str, ...]) -> "MetaTeamAssignmentAttestation":
        selected = tuple(profile_ids)
        known = {profile.profile_id: profile for profile in self.profiles}
        if tuple(sorted(set(selected))) != selected:
            raise ValueError("consumed profile ids must be sorted and unique")
        if any(profile_id not in known for profile_id in selected):
            raise ValueError("consumed profile is not in the assignment offer")
        for profile_id in selected:
            if known[profile_id].available_index > self.read_cut:
                raise ValueError("consumed profile is after the read cut")
        return MetaTeamAssignmentAttestation.build(
            offer_id=self.offer_id, offer_digest=self.offer_digest,
            profile_ids=selected, decision_index=self.decision_index,
            read_cut=self.read_cut,
        )


@dataclass(frozen=True)
class MetaTeamAssignmentAttestation:
    """Digest-bound proof of profile inputs available to one later assignment."""

    offer_id: str
    offer_digest: str
    profile_ids: tuple[str, ...]
    decision_index: int
    read_cut: int
    policy_input_digest: str
    attestation_digest: str

    def __post_init__(self) -> None:
        if not self.offer_id:
            raise ValueError("assignment attestation offer_id is required")
        _sha(self.offer_digest, "offer_digest")
        if tuple(sorted(set(self.profile_ids))) != self.profile_ids:
            raise ValueError("attestation profile ids must be sorted and unique")
        _nonnegative_int(self.decision_index, "decision_index")
        _nonnegative_int(self.read_cut, "read_cut")
        if self.read_cut > self.decision_index:
            raise ValueError("attestation read cut is after the decision")
        _sha(self.policy_input_digest, "policy_input_digest")
        _sha(self.attestation_digest, "attestation_digest")
        if self.policy_input_digest != self.expected_input_digest(
            self.offer_digest, self.profile_ids, self.read_cut
        ):
            raise ValueError("policy_input_digest does not match consumed profiles")
        if self.attestation_digest != _digest(self.payload()):
            raise ValueError("attestation_digest does not match canonical payload")

    @staticmethod
    def expected_input_digest(offer_digest: str, profile_ids: tuple[str, ...], read_cut: int) -> str:
        return _digest({"offer_digest": offer_digest, "profile_ids": list(profile_ids), "read_cut": read_cut})

    @classmethod
    def build(
        cls, *, offer_id: str, offer_digest: str, profile_ids: tuple[str, ...],
        decision_index: int, read_cut: int,
    ) -> "MetaTeamAssignmentAttestation":
        policy_input_digest = cls.expected_input_digest(offer_digest, profile_ids, read_cut)
        provisional = {
            "attestation_version": "metateam-assignment-consumption-v1",
            "offer_id": offer_id, "offer_digest": offer_digest,
            "profile_ids": list(profile_ids), "decision_index": decision_index,
            "read_cut": read_cut, "policy_input_digest": policy_input_digest,
        }
        return cls(
            offer_id=offer_id, offer_digest=offer_digest, profile_ids=profile_ids,
            decision_index=decision_index, read_cut=read_cut,
            policy_input_digest=policy_input_digest,
            attestation_digest=_digest(provisional),
        )

    def payload(self) -> dict[str, Any]:
        return {
            "attestation_version": "metateam-assignment-consumption-v1",
            "offer_id": self.offer_id, "offer_digest": self.offer_digest,
            "profile_ids": list(self.profile_ids), "decision_index": self.decision_index,
            "read_cut": self.read_cut, "policy_input_digest": self.policy_input_digest,
        }
