"""Stateless assignment scores derived from public role evidence.

This adapter is an executable comparator for the assignment boundary.  It
does not mutate a persistent policy and it deliberately reads only the public
recipient judgment in a ``RoleEvidenceOffer``.  Producer scores, terminal
quality, artifact-private fields and later outcomes are excluded so a caller
can test the information value of situated judgment separately from delayed
policy credit.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

from peerrolebench_role_evidence_offer import RoleEvidenceOffer


VERSION = "role-evidence-judgment-beta-v1"
JUDGMENT_MAPPING_VERSION = "recipient-judgment-mapping-v1"
JUDGMENT_LABELS = {
    "accept": 1.0,
    "accept_with_rework": 0.5,
    "reject_redo": 0.0,
}


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class RoleEvidenceScoreConfig:
    """Frozen scoring constants; this comparator has no learned state."""

    prior: float = 1.0
    trust_scale: float = 2.0
    mapping_version: str = JUDGMENT_MAPPING_VERSION

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.prior)) or float(self.prior) <= 0.0:
            raise ValueError("prior must be positive and finite")
        if not math.isfinite(float(self.trust_scale)) or float(self.trust_scale) < 0.0:
            raise ValueError("trust_scale must be finite and non-negative")
        if self.mapping_version != JUDGMENT_MAPPING_VERSION:
            raise ValueError("unsupported judgment mapping version")


@dataclass(frozen=True)
class RoleEvidenceScore:
    """Scores and the exact public evidence snapshot used to derive them."""

    version: str
    mapping_version: str
    read_cut: int
    candidate_keys: tuple[str, ...]
    scores: tuple[float, ...]
    posterior_means: tuple[float, ...]
    evidence_ids: tuple[str, ...]
    input_digest: str

    def payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "mapping_version": self.mapping_version,
            "read_cut": self.read_cut,
            "candidate_keys": list(self.candidate_keys),
            "scores": list(self.scores),
            "posterior_means": list(self.posterior_means),
            "evidence_ids": list(self.evidence_ids),
        }


def score_role_evidence(
    offer: RoleEvidenceOffer,
    *,
    base_scores: Sequence[float],
    read_cut: int,
    config: RoleEvidenceScoreConfig | None = None,
) -> RoleEvidenceScore:
    """Convert visible public judgments into assignment overlay scores.

    For candidate ``c``, the posterior mean is

    ``(prior + sum(label_j)) / (2 * prior + n_c)``

    and the returned overlay is ``base[c] + trust_scale * (mean - .5)``.
    Rows at or after ``read_cut`` are excluded.  The function never changes
    ``offer`` or any policy object; assignment code remains responsible for
    enforcing the active method's evidence-subject invariant.
    """

    if not isinstance(offer, RoleEvidenceOffer):
        raise TypeError("offer must be a RoleEvidenceOffer")
    if type(read_cut) is not int or read_cut < 0:
        raise ValueError("read_cut must be a non-negative integer")
    values = tuple(float(value) for value in base_scores)
    if len(values) != len(offer.candidate_keys) or not all(math.isfinite(value) for value in values):
        raise ValueError("base_scores must be finite and aligned with the candidate menu")
    cfg = config or RoleEvidenceScoreConfig()
    counts = {key: [0, 0.0] for key in offer.candidate_keys}
    visible_ids: list[str] = []
    visible_rows: list[Mapping[str, Any]] = []
    for row in offer.public_evidence:
        if int(row["available_index"]) > read_cut:
            continue
        judgment = row.get("judgment")
        if judgment not in JUDGMENT_LABELS:
            raise ValueError(f"unsupported public judgment={judgment!r}")
        key = str(row["candidate_key"])
        if key not in counts:
            raise ValueError("evidence row references a candidate outside the offer menu")
        counts[key][0] += 1
        counts[key][1] += JUDGMENT_LABELS[judgment]
        visible_ids.append(str(row["evidence_id"]))
        # Keep the digest bound to the public judgment fields only.  In
        # particular, quality_score and other terminal fields cannot change
        # this assignment comparator's input.
        visible_rows.append({
            "evidence_id": str(row["evidence_id"]),
            "candidate_key": key,
            "judgment": judgment,
            "available_index": int(row["available_index"]),
        })
    means: list[float] = []
    scores: list[float] = []
    for key, base in zip(offer.candidate_keys, values):
        count, total = counts[key]
        mean = (cfg.prior + total) / (2.0 * cfg.prior + count)
        means.append(mean)
        scores.append(base + cfg.trust_scale * (mean - 0.5))
    input_digest = _digest({
        "version": VERSION,
        "mapping_version": cfg.mapping_version,
        "offer_id": offer.offer_id,
        "task_id": offer.task_id,
        "task_index": int(offer.task_index),
        "context_key": offer.context_key,
        "candidate_keys": list(offer.candidate_keys),
        "read_cut": read_cut,
        "base_scores": list(values),
        "public_judgments": visible_rows,
        "prior": cfg.prior,
        "trust_scale": cfg.trust_scale,
    })
    return RoleEvidenceScore(
        version=VERSION, mapping_version=cfg.mapping_version, read_cut=read_cut,
        candidate_keys=tuple(offer.candidate_keys), scores=tuple(scores),
        posterior_means=tuple(means), evidence_ids=tuple(sorted(visible_ids)),
        input_digest=input_digest,
    )


__all__ = [
    "JUDGMENT_LABELS", "JUDGMENT_MAPPING_VERSION", "RoleEvidenceScore",
    "RoleEvidenceScoreConfig", "VERSION", "score_role_evidence",
]
