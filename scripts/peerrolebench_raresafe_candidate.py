"""Reference state for the RARE-Anchor candidate method.

This module is intentionally small and CPU-only.  It is a candidate-method
invariant reference, not a benchmark policy and not a scientific result.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class RoleFeedback:
    key: str
    source_index: int
    features: tuple[float, ...]
    label: float | None
    weight: float
    encoder_version: str = "hash64-v1"
    status: str = "eligible"
    supersedes: str | None = None


def _sigmoid(value: float) -> float:
    value = max(-50.0, min(50.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def _logloss(features: Sequence[float], label: float, theta: Sequence[float]) -> float:
    prediction = max(1e-8, min(1.0 - 1e-8, _sigmoid(sum(x * w for x, w in zip(features, theta)))))
    return -(label * math.log(prediction) + (1.0 - label) * math.log(1.0 - prediction))


class RareAnchorState:
    """Bounded fast evidence window with a protected reference anchor."""

    def __init__(
        self,
        *,
        dimension: int,
        window_size: int = 256,
        reservoir_size: int = 128,
        lam: float = 1.0,
        radius: float = 2.0,
        encoder_version: str = "hash64-v1",
    ) -> None:
        if dimension <= 0 or window_size <= 0 or reservoir_size <= 0:
            raise ValueError("dimension and capacities must be positive")
        if not math.isfinite(lam) or lam <= 0 or not math.isfinite(radius) or radius <= 0:
            raise ValueError("lam and radius must be positive and finite")
        self.dimension = int(dimension)
        self.window_size = int(window_size)
        self.reservoir_size = int(reservoir_size)
        self.lam = float(lam)
        self.radius = float(radius)
        self.encoder_version = str(encoder_version)
        self.anchor = [0.0] * self.dimension
        self.a = [0.0] * self.dimension
        self.b = [0.0] * self.dimension
        self.window: dict[str, RoleFeedback] = {}
        self.order: list[str] = []
        self.superseded: set[str] = set()
        self.correction_queue: list[str] = []
        self.watermark = -1
        self.updates = 0
        self.unknowns = 0
        self.duplicates = 0

    def _check(self, event: RoleFeedback) -> None:
        if not event.key:
            raise ValueError("feedback key is required")
        if len(event.features) != self.dimension or not all(math.isfinite(float(x)) for x in event.features):
            raise ValueError("feature dimension or finiteness mismatch")
        norm = math.sqrt(sum(float(x) * float(x) for x in event.features))
        if norm > 1.0 + 1e-9:
            raise ValueError("features must have L2 norm <= 1")
        if event.source_index < 0:
            raise ValueError("source_index must be non-negative")
        if event.status == "eligible":
            if event.label is None or not 0.0 <= float(event.label) <= 1.0:
                raise ValueError("eligible feedback requires label in [0,1]")
            if not 0.0 <= float(event.weight) <= 1.0:
                raise ValueError("eligible feedback requires weight in [0,1]")
        if event.encoder_version != self.encoder_version:
            raise ValueError("encoder version mismatch")

    def _add_contribution(self, event: RoleFeedback, sign: float) -> None:
        assert event.label is not None
        weight = float(event.weight) * sign
        for i, feature in enumerate(event.features):
            self.a[i] += weight * float(feature) * float(feature)
            self.b[i] += weight * float(event.label) * float(feature)

    def _theta_raw(self) -> list[float]:
        return [self.b[i] / (self.lam + max(0.0, self.a[i])) for i in range(self.dimension)]

    def _refresh(self) -> None:
        raw = self._theta_raw()
        delta = [raw[i] - self.anchor[i] for i in range(self.dimension)]
        norm = math.sqrt(sum(value * value for value in delta))
        scale = min(1.0, self.radius / norm) if norm > 0.0 else 1.0
        self.theta = [self.anchor[i] + scale * delta[i] for i in range(self.dimension)]

    def ingest(self, event: RoleFeedback) -> str:
        """Return UPDATE, DUPLICATE, UNKNOWN, or QUEUED_CORRECTION."""
        self._check(event)
        if event.status != "eligible":
            self.unknowns += 1
            return "UNKNOWN"
        if event.key in self.superseded or (event.key in self.window and event.supersedes is None):
            self.duplicates += 1
            return "DUPLICATE"
        if event.supersedes is not None:
            old = self.window.get(event.supersedes)
            if old is None:
                self.correction_queue.append(event.key)
                self.unknowns += 1
                return "QUEUED_CORRECTION"
            self._add_contribution(old, -1.0)
            del self.window[event.supersedes]
            self.order.remove(event.supersedes)
            self.superseded.add(event.supersedes)
        elif event.source_index < self.watermark:
            self.correction_queue.append(event.key)
            self.unknowns += 1
            return "QUEUED_CORRECTION"

        self._add_contribution(event, 1.0)
        self.window[event.key] = event
        self.order.append(event.key)
        self.watermark = max(self.watermark, event.source_index)
        while len(self.order) > self.window_size:
            expired = self.order.pop(0)
            old = self.window.pop(expired)
            self._add_contribution(old, -1.0)
        self.updates += 1
        self._refresh()
        return "UPDATE"

    def consolidate_if_safe(self, reservoir: Iterable[tuple[tuple[float, ...], float]], epsilon: float = 0.05) -> bool:
        """Move fast state to the anchor only when old loss does not worsen."""
        rows = list(reservoir)[: self.reservoir_size]
        if not rows:
            return False
        old_loss = sum(_logloss(phi, label, self.anchor) for phi, label in rows) / len(rows)
        new_loss = sum(_logloss(phi, label, self.theta) for phi, label in rows) / len(rows)
        if new_loss > old_loss + float(epsilon):
            return False
        self.anchor = list(self.theta)
        for key in list(self.window):
            del self.window[key]
        self.order.clear()
        self.a = [0.0] * self.dimension
        self.b = [0.0] * self.dimension
        self._refresh()
        return True

    def snapshot(self) -> dict[str, Any]:
        self._refresh()
        return {
            "dimension": self.dimension,
            "window_size": self.window_size,
            "reservoir_size": self.reservoir_size,
            "lam": self.lam,
            "radius": self.radius,
            "encoder_version": self.encoder_version,
            "anchor": list(self.anchor),
            "a": list(self.a),
            "b": list(self.b),
            "theta": list(self.theta),
            "window": {key: asdict(value) for key, value in self.window.items()},
            "order": list(self.order),
            "superseded": sorted(self.superseded),
            "correction_queue": list(self.correction_queue),
            "watermark": self.watermark,
            "updates": self.updates,
            "unknowns": self.unknowns,
            "duplicates": self.duplicates,
        }

    @classmethod
    def restore(cls, payload: Mapping[str, Any]) -> "RareAnchorState":
        state = cls(
            dimension=int(payload["dimension"]), window_size=int(payload["window_size"]),
            reservoir_size=int(payload["reservoir_size"]), lam=float(payload["lam"]),
            radius=float(payload["radius"]), encoder_version=str(payload["encoder_version"]),
        )
        state.anchor = [float(x) for x in payload["anchor"]]
        state.a = [float(x) for x in payload["a"]]
        state.b = [float(x) for x in payload["b"]]
        state.window = {
            str(key): RoleFeedback(**dict(value)) for key, value in dict(payload["window"]).items()
        }
        state.order = [str(key) for key in payload["order"]]
        state.superseded = {str(key) for key in payload["superseded"]}
        state.correction_queue = [str(key) for key in payload["correction_queue"]]
        state.watermark = int(payload["watermark"])
        state.updates = int(payload["updates"])
        state.unknowns = int(payload["unknowns"])
        state.duplicates = int(payload["duplicates"])
        state._refresh()
        return state

    def digest(self) -> str:
        encoded = json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    def semantic_digest(self) -> str:
        """Digest policy-visible state, excluding audit counters and queues."""
        payload = self.snapshot()
        payload.pop("unknowns", None)
        payload.pop("duplicates", None)
        payload.pop("correction_queue", None)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


__all__ = ["RareAnchorState", "RoleFeedback"]
