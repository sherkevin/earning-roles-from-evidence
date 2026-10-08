"""Classical full-ridge numerical comparator for signed targets.

This state is not an innovation claim or an authorization to use a target as
reward. The caller must select the feature vector and establish reward legality
before calling ``update``. No candidate selection or runner policy lives here.
"""

from __future__ import annotations

import math

import numpy as np


class SignedRidgeState:
    """Full inverse ridge recursion with a fixed feature dimension.

    For regularization rho, the state solves
    ``(rho I + X.T @ X) w = X.T @ u`` after each accepted update.
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
        inverse_scale = 1.0 / regularization
        if not math.isfinite(inverse_scale):
            raise ValueError("rho is too small for a finite inverse")
        self._dimension = dimension
        self._rho = regularization
        self._inverse = np.eye(dimension, dtype=np.float64) * inverse_scale
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
        return int(self._weights.nbytes + self._inverse.nbytes)

    @property
    def weights(self) -> np.ndarray:
        return self._weights.copy()

    @property
    def inverse(self) -> np.ndarray:
        return self._inverse.copy()

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
            v = self._inverse @ feature
            s = float(1.0 + feature @ v)
            if not math.isfinite(prediction) or not math.isfinite(s) or s <= 0:
                raise ValueError("ridge update is not finite")
            gain = v / s
            next_weights = self._weights + gain * (target - prediction)
            next_inverse = self._inverse - np.outer(v, v) / s
        if not np.all(np.isfinite(next_weights)) or not np.all(np.isfinite(next_inverse)):
            raise ValueError("ridge update is not finite")
        self._weights = next_weights
        self._inverse = next_inverse
        self._count += 1
        return prediction


__all__ = ["SignedRidgeState"]
