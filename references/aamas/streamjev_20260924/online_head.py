"""Selected-only online parameter head for Stream-JEV.

The encoder and candidate feature construction stay frozen.  Every arrived
feedback event updates the small residual head parameters immediately with a
regularized, exponentially weighted recursive ridge fit.  This is the stable
parameter-learning baseline and the first candidate for the deployable
mainline; recurrent fast memory remains a separate challenger.
"""

from __future__ import annotations

from collections import deque
from typing import Mapping, Optional, Sequence, Tuple

import numpy as np


class OnlineRLSHead:
    """Low-dimensional selected-only recursive ridge head.

    ``theta`` is the live model parameter.  The base encoder is never touched
    by ``update``.  A candidate is represented only by its cached feature, so
    an unseen candidate/version can generalize without allocating an unbounded
    per-ID state table.
    """

    def __init__(
        self,
        feature_dim: int,
        forgetting: float = 0.995,
        ridge: float = 1.0,
        max_parameter_norm: float = 10.0,
        max_weight: float = 20.0,
        max_feature_norm: float = 20.0,
        residual_scale: float = 0.5,
        uncertainty_scale: float = 0.1,
        temperature: float = 1.0,
        max_seen_feedback: int = 100_000,
        encoder_version: str = "unknown",
        feature_schema: str = "default",
    ) -> None:
        values = (forgetting, ridge, max_parameter_norm, max_weight,
                  max_feature_norm, residual_scale, uncertainty_scale, temperature)
        if feature_dim <= 0 or not all(np.isfinite(v) for v in values):
            raise ValueError("invalid RLS dimensions or hyperparameters")
        if not (0.0 < forgetting <= 1.0) or ridge <= 0 or max_parameter_norm <= 0:
            raise ValueError("invalid RLS dimensions or hyperparameters")
        if max_weight <= 0 or max_feature_norm <= 0 or temperature <= 0 or max_seen_feedback <= 0:
            raise ValueError("invalid RLS dimensions or hyperparameters")
        self.feature_dim = int(feature_dim)
        self.forgetting = float(forgetting)
        self.ridge = float(ridge)
        self.max_parameter_norm = float(max_parameter_norm)
        self.max_weight = float(max_weight)
        self.max_feature_norm = float(max_feature_norm)
        self.residual_scale = float(residual_scale)
        self.uncertainty_scale = float(uncertainty_scale)
        self.temperature = float(temperature)
        self.max_seen_feedback = int(max_seen_feedback)
        if not encoder_version or not feature_schema:
            raise ValueError("encoder_version and feature_schema are required")
        self.encoder_version = str(encoder_version)
        self.feature_schema = str(feature_schema)
        self.theta0 = np.zeros(self.feature_dim, dtype=np.float64)
        self.theta = self.theta0.copy()
        self.A = self.ridge * np.eye(self.feature_dim, dtype=np.float64)
        self.b = np.zeros(self.feature_dim, dtype=np.float64)
        self.observed = 0
        self._seen_feedback = set()
        self._seen_order = deque()

    def _vector(self, feature: Sequence[float]) -> np.ndarray:
        x = np.asarray(feature, dtype=np.float64)
        if x.shape != (self.feature_dim,) or not np.all(np.isfinite(x)):
            raise ValueError(f"feature must be finite with shape {(self.feature_dim,)}")
        # Compute the norm after scaling by the largest coordinate so very
        # large but finite serialized embeddings cannot overflow the guard.
        scale = float(np.max(np.abs(x)))
        norm = 0.0 if scale == 0.0 else float(scale * np.linalg.norm(x / scale))
        if not np.isfinite(norm):
            raise ValueError("feature norm must be finite")
        if norm > self.max_feature_norm:
            x = x * (self.max_feature_norm / norm)
        return x

    def score(
        self,
        candidate_ids: Sequence[str],
        base_scores: Sequence[float],
        features: Mapping[str, Sequence[float]],
        explore: bool = True,
        encoder_version: Optional[str] = None,
        feature_schema: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        if encoder_version is not None and str(encoder_version) != self.encoder_version:
            raise ValueError("encoder version does not match head snapshot")
        if feature_schema is not None and str(feature_schema) != self.feature_schema:
            raise ValueError("feature schema does not match head snapshot")
        if not candidate_ids or len(candidate_ids) != len(base_scores):
            raise ValueError("candidate menu and base scores must be non-empty and aligned")
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("candidate IDs must be unique")
        base = np.asarray(base_scores, dtype=np.float64)
        if not np.all(np.isfinite(base)):
            raise ValueError("base scores must be finite")
        # Scores may come from an untrusted cache.  Bound them before the
        # max-subtraction below so 1e308 - (-1e308) cannot overflow.
        base = np.clip(base, -1e6, 1e6)
        # Solve against A instead of explicitly forming its inverse.  A is
        # symmetric positive definite up to numerical drift from long streams.
        A = 0.5 * (self.A + self.A.T)
        eye = np.eye(self.feature_dim, dtype=np.float64)
        try:
            solved = np.linalg.solve(A, eye)
        except np.linalg.LinAlgError:
            solved = np.linalg.solve(A + 1e-8 * eye, eye)
        residual, uncertainty = [], []
        for cid in candidate_ids:
            x = self._vector(features[cid])
            residual.append(float(self.theta @ x))
            variance = float(x @ solved @ x)
            if not np.isfinite(variance):
                raise ValueError("uncertainty became non-finite")
            uncertainty.append(float(np.sqrt(max(0.0, variance))))
        # ``base_scores`` and the learned residual are quality utilities on a
        # shared scale.  The returned probabilities are the behaviour policy;
        # they are not calibrated probabilities from the linear head.
        logits = base + self.residual_scale * np.asarray(residual)
        if explore:
            logits = logits + self.uncertainty_scale * np.asarray(uncertainty)
        # The head is a utility scorer; the softmax is only the behaviour
        # policy.  Clip the shifted utility to keep extreme cached scores
        # from overflowing exp while preserving the useful ranking.
        logits = np.clip((logits - np.max(logits)) / self.temperature, -60.0, 0.0)
        probs = np.exp(logits)
        probs /= np.sum(probs)
        return probs, np.asarray(uncertainty)

    def choose(
        self,
        candidate_ids: Sequence[str],
        base_scores: Sequence[float],
        features: Mapping[str, Sequence[float]],
        rng: np.random.Generator,
        explore: bool = True,
        encoder_version: Optional[str] = None,
        feature_schema: Optional[str] = None,
    ) -> dict:
        """Sample one action and return the exact propensity to log."""
        probs, uncertainty = self.score(
            candidate_ids, base_scores, features, explore=explore,
            encoder_version=encoder_version, feature_schema=feature_schema,
        )
        index = int(rng.choice(len(candidate_ids), p=probs))
        return {
            "chosen_id": candidate_ids[index],
            "chosen_index": index,
            "propensity": float(probs[index]),
            "probabilities": probs.tolist(),
            "uncertainty": uncertainty.tolist(),
        }

    def update(
        self,
        feature: Sequence[float],
        label: float,
        propensity: float,
        feedback_id: Optional[str] = None,
    ) -> bool:
        """Update live ``theta`` from one selected candidate feedback only."""
        if feedback_id is not None:
            feedback_id = str(feedback_id)
            if feedback_id in self._seen_feedback:
                return False
        if not (np.isfinite(label) and 0.0 <= label <= 1.0):
            raise ValueError("label must be finite and in [0,1]")
        if not (np.isfinite(propensity) and 0.0 < propensity <= 1.0):
            raise ValueError("propensity must be finite and in (0,1]")
        x = self._vector(feature)
        weight = min(self.max_weight, 1.0 / float(propensity))
        anchor_A = self.ridge * np.eye(self.feature_dim, dtype=np.float64)
        anchor_b = anchor_A @ self.theta0
        self.A = anchor_A + self.forgetting * (self.A - anchor_A) + weight * np.outer(x, x)
        self.b = anchor_b + self.forgetting * (self.b - anchor_b) + weight * float(label) * x
        target = np.linalg.solve(self.A, self.b)
        delta = target - self.theta0
        norm = float(np.linalg.norm(delta))
        if norm > self.max_parameter_norm:
            target = self.theta0 + delta * (self.max_parameter_norm / norm)
            # Keep the raw sufficient statistics.  Projection is a deployment
            # safety constraint; rewriting ``b`` would silently turn the next
            # update into a different estimator.
        self.theta = target
        self.observed += 1
        if feedback_id is not None:
            self._seen_feedback.add(feedback_id)
            self._seen_order.append(feedback_id)
            while len(self._seen_order) > self.max_seen_feedback:
                self._seen_feedback.remove(self._seen_order.popleft())
        return True

    def snapshot(self) -> dict:
        return {
            "feature_dim": self.feature_dim,
            "forgetting": self.forgetting,
            "ridge": self.ridge,
            "max_parameter_norm": self.max_parameter_norm,
            "max_weight": self.max_weight,
            "max_feature_norm": self.max_feature_norm,
            "residual_scale": self.residual_scale,
            "uncertainty_scale": self.uncertainty_scale,
            "temperature": self.temperature,
            "max_seen_feedback": self.max_seen_feedback,
            "encoder_version": self.encoder_version,
            "feature_schema": self.feature_schema,
            "theta0": self.theta0.tolist(),
            "theta": self.theta.tolist(),
            "A": self.A.tolist(),
            "b": self.b.tolist(),
            "observed": self.observed,
            "seen_feedback": list(self._seen_order),
        }

    @classmethod
    def restore(cls, payload: Mapping[str, object]) -> "OnlineRLSHead":
        obj = cls(
            feature_dim=int(payload["feature_dim"]),
            forgetting=float(payload["forgetting"]),
            ridge=float(payload["ridge"]),
            max_parameter_norm=float(payload["max_parameter_norm"]),
            max_weight=float(payload["max_weight"]),
            max_feature_norm=float(payload.get("max_feature_norm", 20.0)),
            residual_scale=float(payload["residual_scale"]),
            uncertainty_scale=float(payload["uncertainty_scale"]),
            temperature=float(payload.get("temperature", 1.0)),
            max_seen_feedback=int(payload.get("max_seen_feedback", 100_000)),
            encoder_version=str(payload.get("encoder_version", "unknown")),
            feature_schema=str(payload.get("feature_schema", "default")),
        )
        obj.theta0 = np.asarray(payload["theta0"], dtype=np.float64)
        obj.theta = np.asarray(payload["theta"], dtype=np.float64)
        obj.A = np.asarray(payload["A"], dtype=np.float64)
        obj.b = np.asarray(payload["b"], dtype=np.float64)
        if obj.theta0.shape != (obj.feature_dim,) or obj.theta.shape != (obj.feature_dim,):
            raise ValueError("invalid theta shape in snapshot")
        if obj.A.shape != (obj.feature_dim, obj.feature_dim) or obj.b.shape != (obj.feature_dim,):
            raise ValueError("invalid sufficient-statistic shape in snapshot")
        if not all(np.all(np.isfinite(x)) for x in (obj.theta0, obj.theta, obj.A, obj.b)):
            raise ValueError("non-finite value in snapshot")
        if not np.isfinite(obj.observed) or obj.observed < 0:
            raise ValueError("invalid observed count in snapshot")
        obj.observed = int(payload["observed"])
        for feedback_id in payload.get("seen_feedback", []):
            feedback_id = str(feedback_id)
            if feedback_id not in obj._seen_feedback:
                obj._seen_feedback.add(feedback_id)
                obj._seen_order.append(feedback_id)
        while len(obj._seen_order) > obj.max_seen_feedback:
            obj._seen_feedback.remove(obj._seen_order.popleft())
        return obj
