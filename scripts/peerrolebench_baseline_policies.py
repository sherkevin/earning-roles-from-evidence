"""Small, information-auditable policies for the N03 baseline matrix.

This module is deliberately independent of an LLM and of the live runner.  It
turns four baseline names into executable policy objects that can consume the
same selected-only decision/feedback stream before a root-specific adapter is
connected.  It is an implementation aid, not a benchmark result or a method
lock.  The two Beta policies intentionally remain simple comparators: they
record propensity but do not use inverse-propensity weighting.  That choice
must be fixed or rejected in the formal baseline card before live comparison.

The policy never receives a candidate id in a feedback event.  It resolves the
selected candidate from the sealed source decision, which makes accidental
unselected-label updates observable in tests.  ``source`` distinguishes
situated recipient judgment from independent terminal outcome; ``disposition``
and ``provenance`` are public-boundary results that must be produced by the
runner before this module is called.  A future runner must perform the stronger
responsibility and UNKNOWN checks before constructing these events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from typing import Any, Mapping, Sequence

import numpy as np


FEEDBACK_SOURCES = frozenset({"raw_acceptance", "recipient_judgment", "terminal_outcome"})
FEEDBACK_ACTIONS = frozenset({"none", "accept", "rework", "reject", "use", "repair", "redo"})


@dataclass(frozen=True)
class CandidateRef:
    """The minimum versioned candidate identity needed for replay."""

    candidate_id: str
    candidate_version: str

    def __post_init__(self) -> None:
        if not self.candidate_id or not self.candidate_version:
            raise ValueError("candidate_id and candidate_version are required")

    @property
    def key(self) -> str:
        return f"{self.candidate_id}@{self.candidate_version}"


@dataclass(frozen=True)
class Selection:
    """A sampled action and the exact behaviour-policy snapshot."""

    event_id: str
    context_key: str
    selector_id: str
    candidates: tuple[CandidateRef, ...]
    base_scores: tuple[float, ...]
    chosen_index: int
    probabilities: tuple[float, ...]
    propensity: float
    state_version: str
    encoder_version: str
    feature_schema: str
    selected_at: float
    captured_features: tuple[tuple[str, tuple[float, ...]], ...] = ()

    @property
    def chosen(self) -> CandidateRef:
        return self.candidates[self.chosen_index]

    @property
    def chosen_id(self) -> str:
        return self.chosen.candidate_id


@dataclass(frozen=True)
class Feedback:
    """A selected-only label arriving from one public feedback channel."""

    feedback_id: str
    source_event_id: str
    source: str
    label: float
    arrived_at: float
    delay: float = 0.0
    action: str = "none"
    disposition: str = "eligible"
    provenance: str = "public"


def _validate_menu(candidates: Sequence[CandidateRef], base_scores: Sequence[float]) -> tuple[tuple[CandidateRef, ...], np.ndarray]:
    refs = tuple(candidates)
    if not refs or len(refs) != len(base_scores) or len({ref.key for ref in refs}) != len(refs):
        raise ValueError("candidate menu and base scores must be non-empty and aligned")
    scores = np.asarray(base_scores, dtype=np.float64)
    if scores.shape != (len(refs),) or not np.all(np.isfinite(scores)):
        raise ValueError("base scores must be finite and aligned with candidates")
    return refs, np.clip(scores, -1e6, 1e6)


def _softmax(scores: np.ndarray, temperature: float) -> np.ndarray:
    shifted = np.clip((scores - np.max(scores)) / temperature, -60.0, 0.0)
    probabilities = np.exp(shifted)
    probabilities /= np.sum(probabilities)
    return probabilities


class BaselinePolicy(ABC):
    """Common policy contract used by the first parity tests.

    ``choose`` records the versioned decision snapshot.  ``observe_feedback``
    may only update state from an eligible public event that references a known
    source decision.  Concrete policies decide which public source channels
    they use.
    """

    name: str
    accepted_sources: frozenset[str]

    def __init__(self, *, temperature: float = 1.0) -> None:
        if not math.isfinite(temperature) or temperature <= 0:
            raise ValueError("temperature must be positive and finite")
        self.temperature = float(temperature)
        self._decisions: dict[str, Selection] = {}
        self._seen_feedback: set[str] = set()
        self._seen_source_channels: set[tuple[str, str]] = set()
        self.updates = 0

    @abstractmethod
    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        """Return policy utilities for the current menu."""

    def choose(
        self,
        *,
        event_id: str,
        context_key: str,
        selector_id: str,
        candidates: Sequence[CandidateRef],
        base_scores: Sequence[float],
        rng: np.random.Generator,
        state_version: str = "initial",
        encoder_version: str = "unknown",
        feature_schema: str = "default",
        selected_at: float = 0.0,
        captured_features: Mapping[str, Sequence[float]] | None = None,
    ) -> Selection:
        if not event_id or not context_key or not selector_id:
            raise ValueError("event_id, context_key and selector_id are required")
        if not state_version or not encoder_version or not feature_schema:
            raise ValueError("state, encoder and feature schema versions are required")
        if not math.isfinite(selected_at):
            raise ValueError("selected_at must be finite")
        if event_id in self._decisions:
            raise ValueError(f"duplicate decision event_id={event_id!r}")
        refs, base = _validate_menu(candidates, base_scores)
        captured: dict[str, tuple[float, ...]] = {}
        for key, values in (captured_features or {}).items():
            if key not in {ref.key for ref in refs}:
                raise ValueError(f"captured feature has unknown candidate {key!r}")
            vector = tuple(float(value) for value in values)
            if not vector or not all(math.isfinite(value) for value in vector):
                raise ValueError("captured features must be finite and non-empty")
            captured[str(key)] = vector
        placeholder = Selection(
            str(event_id), str(context_key), str(selector_id), refs,
            tuple(float(value) for value in base), 0, (), 0.0,
            str(state_version), str(encoder_version), str(feature_schema), float(selected_at),
        )
        probabilities = _softmax(self._scores(placeholder, base), self.temperature)
        index = int(rng.choice(len(refs), p=probabilities))
        selection = Selection(
            event_id=str(event_id), context_key=str(context_key), selector_id=str(selector_id),
            candidates=refs, base_scores=tuple(float(value) for value in base), chosen_index=index,
            probabilities=tuple(float(x) for x in probabilities),
            propensity=float(probabilities[index]),
            state_version=str(state_version), encoder_version=str(encoder_version),
            feature_schema=str(feature_schema), selected_at=float(selected_at),
            captured_features=tuple(sorted(captured.items())),
        )
        self.ingest_selection(selection)
        return selection

    def ingest_selection(self, selection: Selection) -> None:
        """Register an already sampled, versioned decision for replay.

        Live policies normally call :meth:`choose`, which samples and stores a
        decision atomically.  A sealed sidecar replay must instead consume the
        exact probabilities and chosen index that were recorded by the live
        runner; re-sampling would silently change the behaviour policy.  This
        method therefore validates the snapshot and stores it without running
        the scorer or RNG.
        """
        if not isinstance(selection, Selection):
            raise TypeError("selection must be a Selection")
        if not selection.event_id or not selection.context_key or not selection.selector_id:
            raise ValueError("selection identifiers are required")
        if selection.event_id in self._decisions:
            raise ValueError(f"duplicate decision event_id={selection.event_id!r}")
        refs, base = _validate_menu(selection.candidates, selection.base_scores)
        if not (0 <= int(selection.chosen_index) < len(refs)):
            raise ValueError("selection chosen index is outside the candidate menu")
        probabilities = np.asarray(selection.probabilities, dtype=np.float64)
        if probabilities.shape != (len(refs),) or not np.all(np.isfinite(probabilities)):
            raise ValueError("selection probabilities must be finite and aligned")
        if np.any(probabilities < 0.0) or not math.isclose(float(probabilities.sum()), 1.0, abs_tol=1e-9):
            raise ValueError("selection probabilities must be non-negative and sum to one")
        propensity = float(selection.propensity)
        if not math.isfinite(propensity) or not 0.0 < propensity <= 1.0:
            raise ValueError("selection propensity must be in (0,1]")
        if not math.isclose(propensity, float(probabilities[selection.chosen_index]), abs_tol=1e-12):
            raise ValueError("selection propensity must equal chosen probability")
        if not all((selection.state_version, selection.encoder_version, selection.feature_schema)):
            raise ValueError("selection state/model/schema versions are required")
        if not math.isfinite(float(selection.selected_at)) or float(selection.selected_at) < 0.0:
            raise ValueError("selection time must be non-negative and finite")
        self._decisions[selection.event_id] = selection

    def observe_feedback(self, feedback: Feedback) -> bool:
        if feedback.feedback_id in self._seen_feedback:
            return False
        if feedback.source not in FEEDBACK_SOURCES:
            raise ValueError(f"unsupported feedback source={feedback.source!r}")
        if feedback.action not in FEEDBACK_ACTIONS:
            raise ValueError(f"unsupported feedback action={feedback.action!r}")
        if feedback.disposition not in {"eligible", "pending", "unknown", "rejected"}:
            raise ValueError(f"unsupported disposition={feedback.disposition!r}")
        if feedback.provenance not in {"public", "unknown"}:
            raise ValueError(f"unsupported provenance={feedback.provenance!r}")
        if feedback.delay < 0 or not math.isfinite(feedback.delay):
            raise ValueError("delay must be non-negative and finite")
        if not math.isfinite(feedback.label) or not 0.0 <= feedback.label <= 1.0:
            raise ValueError("feedback label must be finite and in [0,1]")
        if feedback.disposition != "eligible" or feedback.provenance != "public":
            return False
        source_channel = (feedback.source_event_id, feedback.source)
        if source_channel in self._seen_source_channels:
            self._seen_feedback.add(feedback.feedback_id)
            return False
        selection = self._decisions.get(feedback.source_event_id)
        if selection is None:
            raise ValueError("feedback references an unknown source decision")
        if feedback.source not in self.accepted_sources:
            self._seen_feedback.add(feedback.feedback_id)
            return False
        self._seen_feedback.add(feedback.feedback_id)
        self._seen_source_channels.add(source_channel)
        changed = self._apply_feedback(selection, feedback)
        if changed:
            self.updates += 1
        return changed

    @abstractmethod
    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        """Apply one accepted public event and return whether state changed."""

    def snapshot(self) -> dict[str, Any]:
        return {
            "policy": self.name,
            "temperature": self.temperature,
            "updates": self.updates,
            "decision_count": len(self._decisions),
            "seen_feedback": sorted(self._seen_feedback),
            "seen_source_channels": [list(value) for value in sorted(self._seen_source_channels)],
            "decisions": {
                key: {
                    "context_key": value.context_key,
                    "selector_id": value.selector_id,
                    "candidate_keys": [ref.key for ref in value.candidates],
                    "chosen_key": value.chosen.key,
                    "base_scores": list(value.base_scores),
                    "probabilities": list(value.probabilities),
                    "propensity": value.propensity,
                    "state_version": value.state_version,
                    "encoder_version": value.encoder_version,
                    "feature_schema": value.feature_schema,
                    "selected_at": value.selected_at,
                    "captured_features": {key: list(vector) for key, vector in value.captured_features},
                }
                for key, value in sorted(self._decisions.items())
            },
            "state": self._state_snapshot(),
        }

    @classmethod
    def restore(cls, payload: Mapping[str, Any]) -> "BaselinePolicy":
        """Restore a policy snapshot without changing its policy family."""

        if not isinstance(payload, Mapping) or not isinstance(payload.get("policy"), str):
            raise ValueError("policy snapshot must name a policy")
        policy = policy_from_name(str(payload["policy"]), temperature=float(payload["temperature"]))
        for event_id, raw in dict(payload.get("decisions", {})).items():
            keys = tuple(str(value) for value in raw["candidate_keys"])
            refs = tuple(CandidateRef(*key.rsplit("@", 1)) for key in keys)
            chosen_key = str(raw["chosen_key"])
            chosen_index = next(index for index, ref in enumerate(refs) if ref.key == chosen_key)
            captured = tuple(
                (str(key), tuple(float(value) for value in values))
                for key, values in dict(raw.get("captured_features", {})).items()
            )
            policy._decisions[str(event_id)] = Selection(
                event_id=str(event_id), context_key=str(raw["context_key"]),
                selector_id=str(raw["selector_id"]), candidates=refs,
                base_scores=tuple(float(value) for value in raw["base_scores"]),
                chosen_index=chosen_index,
                probabilities=tuple(float(value) for value in raw["probabilities"]),
                propensity=float(raw["propensity"]),
                state_version=str(raw["state_version"]),
                encoder_version=str(raw["encoder_version"]),
                feature_schema=str(raw["feature_schema"]),
                selected_at=float(raw["selected_at"]), captured_features=captured,
            )
        policy._seen_feedback = {str(value) for value in payload.get("seen_feedback", [])}
        policy._seen_source_channels = {
            (str(value[0]), str(value[1])) for value in payload.get("seen_source_channels", [])
        }
        policy.updates = int(payload.get("updates", 0))
        policy._restore_state(payload.get("state", {}))
        return policy

    @abstractmethod
    def _state_snapshot(self) -> dict[str, Any]:
        """Return JSON-compatible policy state."""

    def _restore_state(self, state: Mapping[str, Any]) -> None:
        """Restore policy-specific state; stateless policies need no work."""


class UniformPolicy(BaselinePolicy):
    """Uniform random choice; ignores base scores and all feedback."""

    name = "uniform"
    accepted_sources = frozenset()

    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        return np.zeros_like(base_scores)

    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        return False

    def _state_snapshot(self) -> dict[str, Any]:
        return {}


class NoUpdatePolicy(BaselinePolicy):
    """Frozen contextual scorer supplied through the shared base-score input."""

    name = "no_update"
    accepted_sources = frozenset()

    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        return base_scores

    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        return False

    def _state_snapshot(self) -> dict[str, Any]:
        return {}


class _BetaTrustPolicy(BaselinePolicy):
    """Shared bounded trust update for the two simple feedback baselines."""

    trust_scale = 2.0

    def __init__(self, *, temperature: float = 1.0, prior: float = 1.0) -> None:
        super().__init__(temperature=temperature)
        if not math.isfinite(prior) or prior <= 0:
            raise ValueError("prior must be positive and finite")
        self.prior = float(prior)
        self._counts: dict[str, list[float]] = {}

    def _posterior_mean(self, key: str) -> float:
        alpha, beta = self._counts.get(key, [self.prior, self.prior])
        return alpha / (alpha + beta)

    def _update_key(self, key: str, label: float) -> bool:
        alpha, beta = self._counts.get(key, [self.prior, self.prior])
        self._counts[key] = [alpha + float(label), beta + (1.0 - float(label))]
        return True

    def _state_snapshot(self) -> dict[str, Any]:
        return {"prior": self.prior, "counts": {key: list(value) for key, value in sorted(self._counts.items())}}

    def _restore_state(self, state: Mapping[str, Any]) -> None:
        self.prior = float(state.get("prior", self.prior))
        self._counts = {
            str(key): [float(value[0]), float(value[1])]
            for key, value in dict(state.get("counts", {})).items()
        }


class TerminalOnlyPolicy(_BetaTrustPolicy):
    """Uses only independent terminal outcomes, pooled by candidate id."""

    name = "terminal_only"
    accepted_sources = frozenset({"terminal_outcome"})

    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        return base_scores + self.trust_scale * np.asarray(
            [self._posterior_mean(candidate.key) - 0.5 for candidate in selection.candidates],
            dtype=np.float64,
        )

    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        return self._update_key(selection.chosen.key, feedback.label)


class RawAcceptancePolicy(_BetaTrustPolicy):
    """Contextual trust on raw recipient accept/reject labels.

    This is intentionally separate from :class:`ContextualTrustPolicy`.  The
    context and candidate key are held constant so the comparison can isolate
    the responsibility-aware projection: raw acceptance may be public even
    when producer attribution is not eligible.  The runner must create the
    ``raw_acceptance`` source only from selected-only recipient accept/reject
    actions; this policy never reads private scorer fields.
    """

    name = "raw_acceptance"
    accepted_sources = frozenset({"raw_acceptance"})

    @staticmethod
    def _key(selection: Selection, candidate: CandidateRef) -> str:
        return f"{selection.context_key}\x1f{candidate.key}"

    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        return base_scores + self.trust_scale * np.asarray(
            [self._posterior_mean(self._key(selection, candidate)) - 0.5
             for candidate in selection.candidates],
            dtype=np.float64,
        )

    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        # A raw acceptance channel is narrower than a general recipient
        # judgment.  Malformed actions are ignored rather than converted into
        # a negative label; the runner should classify them as UNKNOWN.
        if feedback.action not in {"accept", "reject"}:
            return False
        return self._update_key(self._key(selection, selection.chosen), feedback.label)


class ContextualTrustPolicy(_BetaTrustPolicy):
    """Same-information trust control keyed by candidate and public context."""

    name = "contextual_trust"
    accepted_sources = frozenset({"recipient_judgment"})

    @staticmethod
    def _key(selection: Selection, candidate: CandidateRef) -> str:
        return f"{selection.context_key}\x1f{candidate.key}"

    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        return base_scores + self.trust_scale * np.asarray(
            [self._posterior_mean(self._key(selection, candidate)) - 0.5 for candidate in selection.candidates],
            dtype=np.float64,
        )

    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        return self._update_key(self._key(selection, selection.chosen), feedback.label)


class PooledControllerPolicy(_BetaTrustPolicy):
    """Shared candidate history without context or selector partitioning."""

    name = "pooled_controller"
    accepted_sources = frozenset({"recipient_judgment"})

    @staticmethod
    def _key(selection: Selection, candidate: CandidateRef) -> str:
        return candidate.key

    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        return base_scores + self.trust_scale * np.asarray(
            [self._posterior_mean(self._key(selection, candidate)) - 0.5
             for candidate in selection.candidates],
            dtype=np.float64,
        )

    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        return self._update_key(self._key(selection, selection.chosen), feedback.label)


def policy_from_name(name: str, *, temperature: float = 1.0) -> BaselinePolicy:
    """Construct one of the six currently implemented policy comparators.

    RARE is intentionally absent: its candidate updater still lacks the
    selection-boundary adapter required by the shared runner.
    """

    policies = {
        "uniform": UniformPolicy,
        "no_update": NoUpdatePolicy,
        "raw_acceptance": RawAcceptancePolicy,
        "terminal_only": TerminalOnlyPolicy,
        "contextual_trust": ContextualTrustPolicy,
        "pooled_controller": PooledControllerPolicy,
    }
    try:
        return policies[name](temperature=temperature)
    except KeyError as exc:
        raise ValueError(f"unsupported baseline policy={name!r}") from exc


__all__ = [
    "BaselinePolicy",
    "CandidateRef",
    "ContextualTrustPolicy",
    "Feedback",
    "NoUpdatePolicy",
    "PooledControllerPolicy",
    "RawAcceptancePolicy",
    "Selection",
    "TerminalOnlyPolicy",
    "UniformPolicy",
    "policy_from_name",
]
