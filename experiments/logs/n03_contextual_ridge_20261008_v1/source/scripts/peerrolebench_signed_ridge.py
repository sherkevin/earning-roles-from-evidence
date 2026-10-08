"""Classical full-ridge numerical comparator for signed targets.

This state is not an innovation claim or an authorization to use a target as
reward. The caller must select the feature vector and establish reward legality
before calling ``update``. No candidate selection or runner policy lives here.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np


class SignedRidgeState:
    """Full ridge normal equations with a fixed feature dimension.

    For regularization rho, the state solves
    ``(rho I + X.T @ X) w = X.T @ u`` after each accepted update.
    A fresh dense solve costs O(d^3); this comparator makes no real-time claim.
    """

    def __init__(self, dimension: int, rho: float) -> None:
        if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension <= 0:
            raise ValueError("dimension must be a positive integer")
        if isinstance(rho, bool):
            raise ValueError("rho must be finite and positive")
        try:
            regularization = float(rho)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("rho must be finite and positive") from exc
        if not math.isfinite(regularization) or regularization <= 0:
            raise ValueError("rho must be finite and positive")
        self._dimension = dimension
        self._rho = regularization
        self._gram = np.eye(dimension, dtype=np.float64) * regularization
        self._rhs = np.zeros(dimension, dtype=np.float64)
        self._weights = np.zeros(dimension, dtype=np.float64)
        self._count = 0

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def rho(self) -> float:
        return self._rho

    @property
    def count(self) -> int:
        return self._count

    @property
    def memory_bytes(self) -> int:
        return int(self._gram.nbytes + self._rhs.nbytes + self._weights.nbytes)

    @property
    def weights(self) -> np.ndarray:
        return self._weights.copy()

    @property
    def gram(self) -> np.ndarray:
        return self._gram.copy()

    @property
    def rhs(self) -> np.ndarray:
        return self._rhs.copy()

    def _feature(self, x: object) -> np.ndarray:
        try:
            feature = np.asarray(x, dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("x must be a finite feature vector") from exc
        if feature.shape != (self._dimension,) or not np.all(np.isfinite(feature)):
            raise ValueError("x must be a finite feature vector with the configured dimension")
        norm = float(np.linalg.norm(feature))
        if not math.isfinite(norm) or norm > 1.0:
            raise ValueError("x norm must be at most one")
        return feature

    def predict(self, x: object) -> float:
        feature = self._feature(x)
        prediction = float(feature @ self._weights)
        if not math.isfinite(prediction):
            raise ValueError("prediction is not finite")
        return prediction

    def update(self, x: object, u: float) -> float:
        """Return prediction before update; commit only a finite new state."""
        feature = self._feature(x)
        if isinstance(u, bool):
            raise ValueError("u must be a finite signed target")
        try:
            target = float(u)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("u must be a finite signed target") from exc
        if not math.isfinite(target):
            raise ValueError("u must be a finite signed target")
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            prediction = float(feature @ self._weights)
            next_gram = self._gram + np.outer(feature, feature)
            next_rhs = self._rhs + feature * target
            if (not math.isfinite(prediction) or not np.all(np.isfinite(next_gram))
                    or not np.all(np.isfinite(next_rhs))):
                raise ValueError("ridge update is not finite")
            try:
                next_weights = np.linalg.solve(next_gram, next_rhs)
            except np.linalg.LinAlgError as exc:
                raise ValueError("ridge solve failed") from exc
        if not np.all(np.isfinite(next_weights)):
            raise ValueError("ridge update is not finite")
        self._weights = next_weights
        self._gram = next_gram
        self._rhs = next_rhs
        self._count += 1
        return prediction


class DisjointSignedRidgeState:
    """Classical disjoint ridge: one independent state per exact candidate version.

    It is equivalent to ridge on block features ``e_a ⊗ z`` with the same
    regularization in each block. The caller supplies one sealed context ``z``
    and establishes whether a signed target is legal. No UCB or reward gate is
    implemented here. Each accepted update solves one d-dimensional system.
    """

    def __init__(self, candidate_keys: Sequence[str], dimension: int, rho: float) -> None:
        keys = tuple(candidate_keys)
        if not keys or len(set(keys)) != len(keys):
            raise ValueError("candidate keys must be non-empty and unique")
        if any(not isinstance(key, str) or key.count("@") != 1
               or not all(key.split("@")) or key != key.strip() for key in keys):
            raise ValueError("candidate keys must be exact candidate@version strings")
        self._states = {key: SignedRidgeState(dimension, rho) for key in keys}

    @property
    def candidate_keys(self) -> tuple[str, ...]:
        return tuple(self._states)

    @property
    def memory_bytes(self) -> int:
        return sum(state.memory_bytes for state in self._states.values())

    @property
    def total_updates(self) -> int:
        return sum(state.count for state in self._states.values())

    def _state(self, candidate_key: str) -> SignedRidgeState:
        try:
            return self._states[candidate_key]
        except (KeyError, TypeError) as exc:
            raise ValueError("unknown candidate version") from exc

    def count(self, candidate_key: str) -> int:
        return self._state(candidate_key).count

    def weights(self, candidate_key: str) -> np.ndarray:
        return self._state(candidate_key).weights

    def predict(self, candidate_key: str, context: object) -> float:
        return self._state(candidate_key).predict(context)

    def scores(self, candidate_keys: Sequence[str], context: object) -> dict[str, float]:
        menu = tuple(candidate_keys)
        if not menu or len(set(menu)) != len(menu):
            raise ValueError("candidate menu must be non-empty and unique")
        return {key: self.predict(key, context) for key in menu}

    def update(self, chosen_candidate_key: str, context: object, signed_target: float) -> float:
        """Update only the chosen candidate and return its prior prediction."""
        return self._state(chosen_candidate_key).update(context, signed_target)


__all__ = ["SignedRidgeState", "DisjointSignedRidgeState"]
