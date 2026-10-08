"""Bounded public-profile generator seam for the versioned PIPE3 runner.

The project needs a replaceable boundary between an eligible recipient
judgment and a later assignment profile.  This module deliberately provides
only the deterministic qualification implementation.  It never calls an LLM
and therefore cannot support a profile-quality or efficacy claim.  A future
live generator must preserve the same request/receipt contract and replace
``DeterministicPublicProfileGenerator`` with a metered public-only summarizer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from peerrolebench_metateam_profile_sidecar import (
    MetaTeamProfile,
    build_public_profile_fixture,
    reject_private_public_input,
)


@dataclass(frozen=True)
class PublicProfileGenerationRequest:
    """Typed input accepted by a profile generator.

    ``public_projection`` must be the already-gated public projection.  The
    request intentionally has no raw artifact, terminal score, hidden trace,
    or policy-state field.
    """

    selection: Any
    feedback_sidecar: Any
    public_projection: Any
    attribution_gate: Any
    profile_id: str
    profile_revision: int
    profile: Mapping[str, Any]
    parser_version: str
    model_config_digest: str
    available_index: int | None = None
    supersedes_profile_id: str | None = None


@dataclass(frozen=True)
class ProfileGenerationReceipt:
    """Auditable generation metadata returned beside a profile."""

    generator_version: str
    generation_mode: str
    source_input_digest: str
    attribution_gate_digest: str
    profile_digest: str
    elapsed_seconds: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    real_api_calls: int
    gpu_jobs: int
    scientific_claim_allowed: bool

    def __post_init__(self) -> None:
        if not self.generator_version or not self.generation_mode:
            raise ValueError("generator identity is required")
        if any(len(value) != 64 for value in (self.source_input_digest, self.attribution_gate_digest, self.profile_digest)):
            raise ValueError("generation receipt digests must be SHA-256")
        for name, value in (
            ("elapsed_seconds", self.elapsed_seconds),
            ("cost_usd", self.cost_usd),
        ):
            if type(value) not in (int, float) or value < 0:
                raise ValueError(f"{name} must be non-negative")
        for name, value in (
            ("input_tokens", self.input_tokens),
            ("output_tokens", self.output_tokens),
            ("real_api_calls", self.real_api_calls),
            ("gpu_jobs", self.gpu_jobs),
        ):
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.real_api_calls == 0 and self.gpu_jobs == 0 and self.scientific_claim_allowed:
            raise ValueError("zero-call generation cannot allow a scientific claim")


@dataclass(frozen=True)
class GeneratedPublicProfile:
    profile: MetaTeamProfile
    receipt: ProfileGenerationReceipt


class PublicProfileGenerator(Protocol):
    def generate(self, request: PublicProfileGenerationRequest) -> GeneratedPublicProfile:
        ...


class DeterministicPublicProfileGenerator:
    """Zero-call fixture generator used only for contract qualification."""

    generator_version = "deterministic-public-profile-fixture-v1"

    def generate(self, request: PublicProfileGenerationRequest) -> GeneratedPublicProfile:
        gate = request.attribution_gate
        if gate is None or getattr(gate, "eligible", False) is not True:
            raise ValueError("profile generation requires an eligible responsibility gate")
        if getattr(gate, "sidecar_digest", None) != getattr(request.feedback_sidecar, "sidecar_digest", None):
            raise ValueError("responsibility gate is not bound to feedback sidecar")
        if getattr(gate, "protocol_event_id", None) != getattr(request.feedback_sidecar, "protocol_event_id", None):
            raise ValueError("responsibility gate event does not match feedback sidecar")
        public_payload = request.public_projection.public_payload()
        if not isinstance(public_payload, Mapping):
            raise ValueError("public projection must expose a mapping payload")
        reject_private_public_input(public_payload)
        profile = build_public_profile_fixture(
            selection=request.selection,
            feedback_sidecar=request.feedback_sidecar,
            public_projection=request.public_projection,
            profile_id=request.profile_id,
            profile_revision=request.profile_revision,
            profile=request.profile,
            parser_version=request.parser_version,
            model_config_digest=request.model_config_digest,
            available_index=request.available_index,
            supersedes_profile_id=request.supersedes_profile_id,
        )
        receipt = ProfileGenerationReceipt(
            generator_version=self.generator_version,
            generation_mode="deterministic_fixture",
            source_input_digest=profile.source_input_digest,
            attribution_gate_digest=gate.gate_digest,
            profile_digest=profile.profile_digest,
            elapsed_seconds=0.0,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            real_api_calls=0,
            gpu_jobs=0,
            scientific_claim_allowed=False,
        )
        return GeneratedPublicProfile(profile=profile, receipt=receipt)


__all__ = [
    "DeterministicPublicProfileGenerator",
    "GeneratedPublicProfile",
    "ProfileGenerationReceipt",
    "PublicProfileGenerationRequest",
    "PublicProfileGenerator",
]
