"""Small deterministic fast state for the first Stream-JEV experiments.

This is a strong baseline and runtime probe, not the final neural method. The
Bayesian arm is conservative and interpretable; the RLS residual is a bounded
context-conditioned adaptation path. Only observed actions are updated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np


@dataclass
class CandidateStats:
    alpha: float = 1.0
    beta: float = 1.0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        n = self.alpha + self.beta
        return self.alpha * self.beta / (n * n * (n + 1.0))


class DualFastState:
    """Posterior + RLS residual with bounded, event-level updates.

    `base_logits` are supplied by a frozen encoder/set scorer. `features` are
    cached candidate vectors. The state never receives unselected labels.
    """

    def __init__(
        self,
        feature_dim: int,
        forgetting: float = 0.995,
        ridge: float = 1.0,
        residual_scale: float = 0.5,
        gate_warmup: int = 8,
        max_update_norm: float = 1.0,
    ) -> None:
        if feature_dim <= 0 or not (0.0 < forgetting <= 1.0):
            raise ValueError("invalid feature_dim or forgetting")
        self.feature_dim = int(feature_dim)
        self.forgetting = float(forgetting)
        self.residual_scale = float(residual_scale)
        self.gate_warmup = int(gate_warmup)
        self.max_update_norm = float(max_update_norm)
        self.w = np.zeros(self.feature_dim, dtype=np.float64)
        self.P = np.eye(self.feature_dim, dtype=np.float64) / float(ridge)
        self.stats: Dict[str, CandidateStats] = {}
        self.observed = 0

    def _stats(self, candidate_id: str) -> CandidateStats:
        return self.stats.setdefault(candidate_id, CandidateStats())

    def _gate(self, uncertainty: float) -> float:
        warm = min(1.0, self.observed / max(1, self.gate_warmup))
        # High uncertainty should reduce the neural residual contribution.
        return float(warm / (1.0 + max(0.0, uncertainty)))

    def score(
        self,
        candidate_ids: Sequence[str],
        base_logits: Sequence[float],
        features: Mapping[str, Sequence[float]],
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        if len(candidate_ids) != len(base_logits) or not candidate_ids:
            raise ValueError("candidate_ids/base_logits mismatch or empty menu")
        residual = []
        posterior = []
        uncertainty = []
        for cid in candidate_ids:
            x = np.asarray(features[cid], dtype=np.float64)
            if x.shape != (self.feature_dim,):
                raise ValueError(f"feature shape for {cid} must be {(self.feature_dim,)}")
            residual.append(float(np.dot(self.w, x)))
            s = self._stats(cid)
            posterior.append(float(np.log(s.mean / (1.0 - s.mean))))
            uncertainty.append(float(np.sqrt(s.variance)))
        mean_uncertainty = float(np.mean(uncertainty))
        gate = self._gate(mean_uncertainty)
        logits = np.asarray(base_logits, dtype=np.float64)
        logits = logits + gate * self.residual_scale * np.asarray(residual)
        logits = logits + 0.25 * np.asarray(posterior)
        logits = logits - np.max(logits)
        probs = np.exp(logits)
        probs /= np.sum(probs)
        return probs, np.asarray(uncertainty), gate

    def update(
        self,
        candidate_id: str,
        features: Sequence[float],
        label: float,
        propensity: float,
    ) -> None:
        """Apply one selected-action feedback event.

        IPS is used only to scale the observed residual; no unselected label is
        manufactured. Labels are clipped to [0,1] for binary/soft outcomes.
        """
        if not (0.0 <= label <= 1.0):
            raise ValueError("label must be in [0,1]")
        if not (0.0 < propensity <= 1.0):
            raise ValueError("propensity must be in (0,1]")
        x = np.asarray(features, dtype=np.float64)
        if x.shape != (self.feature_dim,):
            raise ValueError(f"feature shape must be {(self.feature_dim,)}")
        # Decay the old per-candidate evidence. This is a deliberate drift
        # control; it does not change candidates that were not observed.
        for s in self.stats.values():
            s.alpha = 1.0 + self.forgetting * (s.alpha - 1.0)
            s.beta = 1.0 + self.forgetting * (s.beta - 1.0)
        s = self._stats(candidate_id)
        weight = min(20.0, 1.0 / propensity)
        s.alpha += weight * float(label)
        s.beta += weight * (1.0 - float(label))

        # RLS residual update. Limit the update norm so one noisy label cannot
        # erase the prior representation.
        px = self.P @ x
        denom = self.forgetting + float(x @ px)
        gain = px / max(denom, 1e-12)
        pred = float(self.w @ x)
        delta = gain * (weight * (float(label) - pred))
        norm = float(np.linalg.norm(delta))
        if norm > self.max_update_norm:
            delta *= self.max_update_norm / norm
        self.w += delta
        self.P = (self.P - np.outer(gain, x @ self.P)) / self.forgetting
        self.observed += 1

    def snapshot(self) -> Dict[str, object]:
        return {
            "feature_dim": self.feature_dim,
            "forgetting": self.forgetting,
            "residual_scale": self.residual_scale,
            "gate_warmup": self.gate_warmup,
            "max_update_norm": self.max_update_norm,
            "w": self.w.tolist(),
            "P": self.P.tolist(),
            "stats": {k: {"alpha": v.alpha, "beta": v.beta} for k, v in self.stats.items()},
            "observed": self.observed,
        }

    @classmethod
    def restore(cls, payload: Mapping[str, object]) -> "DualFastState":
        obj = cls(
            feature_dim=int(payload["feature_dim"]),
            forgetting=float(payload["forgetting"]),
            residual_scale=float(payload["residual_scale"]),
            gate_warmup=int(payload["gate_warmup"]),
            max_update_norm=float(payload["max_update_norm"]),
        )
        obj.w = np.asarray(payload["w"], dtype=np.float64)
        obj.P = np.asarray(payload["P"], dtype=np.float64)
        obj.stats = {
            k: CandidateStats(float(v["alpha"]), float(v["beta"]))
            for k, v in dict(payload["stats"]).items()
        }
        obj.observed = int(payload["observed"])
        return obj
