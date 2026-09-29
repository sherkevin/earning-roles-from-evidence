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

from peerrolebench_raresafe_candidate import RareAnchorState, RoleFeedback


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
    label: float | None
    arrived_at: float
    delay: float = 0.0
    action: str = "none"
    disposition: str = "eligible"
    provenance: str = "public"
    arrival_index: int | None = None
    supersedes: str | None = None


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

    def __init__(self, *, temperature: float = 1.0, exploration: float = 0.0) -> None:
        if not math.isfinite(temperature) or temperature <= 0:
            raise ValueError("temperature must be positive and finite")
        if not math.isfinite(exploration) or not 0.0 <= exploration < 1.0:
            raise ValueError("exploration must be finite and in [0,1)")
        self.temperature = float(temperature)
        self.exploration = float(exploration)
        self._decisions: dict[str, Selection] = {}
        self._seen_feedback: set[str] = set()
        self._seen_source_channels: set[tuple[str, str]] = set()
        self._feedback_lineage_by_id: dict[str, tuple[str, str]] = {}
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
            tuple(sorted(captured.items())),
        )
        probabilities = _softmax(self._scores(placeholder, base), self.temperature)
        if self.exploration:
            probabilities = (1.0 - self.exploration) * probabilities + self.exploration / len(probabilities)
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
        if feedback.disposition not in {"eligible", "pending", "unknown", "rejected", "ineligible"}:
            raise ValueError(f"unsupported disposition={feedback.disposition!r}")
        if feedback.provenance not in {"public", "unknown"}:
            raise ValueError(f"unsupported provenance={feedback.provenance!r}")
        if feedback.delay < 0 or not math.isfinite(feedback.delay):
            raise ValueError("delay must be non-negative and finite")
        if feedback.label is not None and (
            not math.isfinite(float(feedback.label)) or not 0.0 <= float(feedback.label) <= 1.0
        ):
            raise ValueError("feedback label must be finite and in [0,1]")
        if feedback.disposition == "eligible" and feedback.label is None:
            raise ValueError("eligible feedback requires a label")
        if feedback.disposition != "eligible" or feedback.provenance != "public":
            return False
        if feedback.supersedes is not None and not self._accepts_corrections:
            raise ValueError("policy does not support feedback corrections")
        source_channel = (feedback.source_event_id, feedback.source)
        if source_channel in self._seen_source_channels and not (
            feedback.supersedes is not None and self._accepts_corrections
        ):
            self._seen_feedback.add(feedback.feedback_id)
            return False
        selection = self._decisions.get(feedback.source_event_id)
        if selection is None:
            raise ValueError("feedback references an unknown source decision")
        if feedback.source not in self.accepted_sources:
            self._seen_feedback.add(feedback.feedback_id)
            return False
        if feedback.supersedes is not None:
            previous_lineage = self._feedback_lineage_by_id.get(feedback.supersedes)
            if previous_lineage is None:
                raise ValueError("feedback correction supersedes unknown lineage")
            if previous_lineage != (feedback.source_event_id, feedback.source):
                raise ValueError("feedback correction crosses source-event or channel lineage")
        changed = self._apply_feedback(selection, feedback)
        # Commit replay markers only after the concrete updater accepts the
        # event.  A malformed RARE event must be retryable after the caller
        # repairs its metadata; marking it before validation would silently
        # turn a transport error into a duplicate no-op.
        self._seen_feedback.add(feedback.feedback_id)
        self._seen_source_channels.add(source_channel)
        self._feedback_lineage_by_id[feedback.feedback_id] = source_channel
        if changed:
            self.updates += 1
        return changed

    @abstractmethod
    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        """Apply one accepted public event and return whether state changed."""

    @property
    def _accepts_corrections(self) -> bool:
        """Whether a policy can consume a second event for one source channel."""

        return False

    def snapshot(self) -> dict[str, Any]:
        return {
            "policy": self.name,
            "temperature": self.temperature,
            "exploration": self.exploration,
            "updates": self.updates,
            "decision_count": len(self._decisions),
            "seen_feedback": sorted(self._seen_feedback),
            "seen_source_channels": [list(value) for value in sorted(self._seen_source_channels)],
            "feedback_lineage": {
                key: list(value) for key, value in sorted(self._feedback_lineage_by_id.items())
            },
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
        policy = policy_from_name(
            str(payload["policy"]), temperature=float(payload["temperature"]),
            exploration=float(payload.get("exploration", 0.0)),
        )
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
        policy._feedback_lineage_by_id = {
            str(key): (str(value[0]), str(value[1]))
            for key, value in dict(payload.get("feedback_lineage", {})).items()
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

    def __init__(self, *, temperature: float = 1.0, prior: float = 1.0, exploration: float = 0.0) -> None:
        super().__init__(temperature=temperature, exploration=exploration)
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


class RarePolicy(BaselinePolicy):
    """Selection adapter for the CPU-only RARE-Anchor candidate.

    The runner must capture the fixed feature vector for every candidate and
    attach an integer event-time ``arrival_index`` to eligible feedback.  The
    responsibility gate remains runner-owned: non-eligible or unknown rows are
    rejected by the common feedback boundary and never reach the updater.
    """

    name = "RARE"
    accepted_sources = frozenset({"recipient_judgment"})

    def __init__(self, *, temperature: float = 1.0, exploration: float = 0.10,
                 dimension: int = 64, window_size: int = 256,
                 reservoir_size: int = 128, pending_size: int = 128) -> None:
        super().__init__(temperature=temperature, exploration=exploration)
        self.dimension = int(dimension)
        self.state = RareAnchorState(
            dimension=self.dimension, window_size=window_size,
            reservoir_size=reservoir_size, pending_size=pending_size,
        )

    @staticmethod
    def _feature_map(selection: Selection) -> dict[str, tuple[float, ...]]:
        return {str(key): tuple(float(value) for value in vector)
                for key, vector in selection.captured_features}

    def _validate_rare_features(self, selection: Selection) -> dict[str, tuple[float, ...]]:
        if selection.encoder_version != self.state.encoder_version:
            raise ValueError("RARE selection encoder version does not match state")
        features = self._feature_map(selection)
        expected = {candidate.key for candidate in selection.candidates}
        if set(features) != expected or len(selection.captured_features) != len(expected):
            raise ValueError("RARE selection requires fixed features for every candidate")
        for vector in features.values():
            if len(vector) != self.dimension or not all(math.isfinite(value) for value in vector):
                raise ValueError("RARE features must be finite with fixed dimension")
            if math.sqrt(sum(value * value for value in vector)) > 1.0 + 1e-9:
                raise ValueError("RARE features must have L2 norm <= 1")
        return features

    def ingest_selection(self, selection: Selection) -> None:
        self._validate_rare_features(selection)
        super().ingest_selection(selection)

    def _scores(self, selection: Selection, base_scores: np.ndarray) -> np.ndarray:
        del base_scores
        features = self._validate_rare_features(selection)
        values = []
        for candidate in selection.candidates:
            vector = features.get(candidate.key)
            values.append(1.0 / (1.0 + math.exp(-max(-50.0, min(50.0,
                sum(x * w for x, w in zip(vector, self.state.theta)))))))
        return np.asarray(values, dtype=np.float64)

    @property
    def _accepts_corrections(self) -> bool:
        return True

    def _apply_feedback(self, selection: Selection, feedback: Feedback) -> bool:
        if type(feedback.arrival_index) is not int or feedback.arrival_index < 0:
            raise ValueError("RARE feedback requires a non-negative arrival_index")
        vector = self._validate_rare_features(selection).get(selection.chosen.key)
        event = RoleFeedback(
            key=str(feedback.feedback_id),
            source_index=int(feedback.arrival_index),
            features=vector,
            label=float(feedback.label),
            weight=1.0,
            status="eligible",
            supersedes=feedback.supersedes,
        )
        disposition = self.state.ingest(event)
        return disposition == "UPDATE"

    def _state_snapshot(self) -> dict[str, Any]:
        return {"dimension": self.dimension, "rare": self.state.snapshot()}

    def _restore_state(self, state: Mapping[str, Any]) -> None:
        rare = dict(state.get("rare", {}))
        self.dimension = int(state.get("dimension", rare.get("dimension", self.dimension)))
        self.state = RareAnchorState.restore(rare)


def policy_from_name(name: str, *, temperature: float = 1.0,
                     exploration: float | None = None) -> BaselinePolicy:
    """Construct one of the executable policy comparators and the RARE adapter."""

    policies = {
        "uniform": UniformPolicy,
        "no_update": NoUpdatePolicy,
        "raw_acceptance": RawAcceptancePolicy,
        "terminal_only": TerminalOnlyPolicy,
        "contextual_trust": ContextualTrustPolicy,
        "pooled_controller": PooledControllerPolicy,
        "RARE": RarePolicy,
    }
    try:
        kwargs: dict[str, Any] = {"temperature": temperature}
        if exploration is not None:
            kwargs["exploration"] = exploration
        return policies[name](**kwargs)
    except KeyError as exc:
        raise ValueError(f"unsupported baseline policy={name!r}") from exc


__all__ = [
    "BaselinePolicy",
    "CandidateRef",
    "ContextualTrustPolicy",
    "Feedback",
    "NoUpdatePolicy",
    "PooledControllerPolicy",
    "RarePolicy",
    "RawAcceptancePolicy",
    "Selection",
    "TerminalOnlyPolicy",
    "UniformPolicy",
    "policy_from_name",
]
