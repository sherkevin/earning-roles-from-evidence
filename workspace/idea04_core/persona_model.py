"""Vector-belief persona model for EDO Stage-2 (E-004 / R3).

Upgrades the Stage-1 ``competence: dict[str, float]`` (a *scalar* ability
score per agent) to a *vector* ``B_i^t(j) ∈ [0, 1]^7`` aligned axis-by-axis
with the task signature ``phi(z)`` defined in ``idea.md §9.2``::

    PERSONA_DIMS = (
        "need_decompose", "need_verification", "need_integration",
        "need_exploration", "evidence_breadth", "uncertainty",
        "cost_sensitivity",
    )

The 7 dimensions mean different things on either side:

  - ``phi(z)``  axis k = how much the *task* ``z`` *demands* attribute k.
  - ``P_i``      axis k = how good agent i is *at handling* tasks demanding k.
  - ``B_i(j)``   axis k = agent i's *belief* about j's competence on axis k.

``Fit(persona, signature) := dot(persona, signature) / DIM_COUNT`` (per
``idea.md §11.2``). The aggregate utility ``U_out_i(z, j) =
Fit(B_i(j), phi(z)) - costs`` is computed by ``action_policy.select_action``;
this module only owns the persona/belief data structure and its updates.

Update rule (per ``idea.md §13`` instantiated for vectors):

    B_i^(t+1)(j) = (1 - ν) * B_i^t(j) + ν * evidence_extract(audit_event)

where ``ν = EMA_NU_DEFAULT = 0.2`` and ``evidence_extract`` uses the audit
event from :mod:`workspace.idea04_core.audit_runtime` plus the task signature
to project the audit signal onto the 7 axes.

# Pinned C-3 — Dual-track persistence (do NOT remove)

R0 baseline ``routing_traces.jsonl`` (~2 GB on disk) was written with
``competence: dict[str, float]``. When we promote to vectors, the canonical
persisted payload is::

    {
      "schema_version": "competence_v2_vector",
      "competence_v1_scalar": dict[str, float],   # mean-projected from v2
      "competence_v2_vector": dict[str, list[float]],
    }

Carrying both tracks lets ``validate_logs.py`` and any historical replay tool
continue reading the v1 scalar field with zero code changes, while new
analyses use the v2 vector field. ``deserialize`` accepts EITHER schema and
broadcasts a v1 scalar to a uniform v2 vector on read.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any

from .audit_runtime import AuditEvent


# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------


PERSONA_DIMS: tuple[str, ...] = (
    "need_decompose",
    "need_verification",
    "need_integration",
    "need_exploration",
    "evidence_breadth",
    "uncertainty",
    "cost_sensitivity",
)
DIM_COUNT: int = len(PERSONA_DIMS)
assert DIM_COUNT == 7, "PERSONA_DIMS must have exactly 7 axes per idea.md §9.2"

EMA_NU_DEFAULT: float = 0.2

SCHEMA_V1: str = "competence_v1_scalar"
SCHEMA_V2: str = "competence_v2_vector"

NEUTRAL_INIT: float = 0.5
"""Default coordinate when a fresh PersonaVector or BeliefStore lookup fires."""


class PersonaModelError(ValueError):
    """Raised on schema, length, or range violations."""


# ---------------------------------------------------------------------------
# PersonaVector
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PersonaVector:
    """Immutable 7-dim vector in ``[0, 1]^7``.

    Frozen because (a) updates are functional (return a new vector — see
    :func:`apply_evidence`) and (b) shared across BeliefStore look-ups. The
    constructor clips out-of-range coordinates and rejects wrong lengths
    so that downstream Fit / EMA arithmetic never has to defend itself.
    """

    values: tuple[float, ...] = field(default_factory=lambda: tuple([NEUTRAL_INIT] * DIM_COUNT))

    def __post_init__(self) -> None:
        vals = tuple(float(v) for v in self.values)
        if len(vals) != DIM_COUNT:
            raise PersonaModelError(
                f"PersonaVector must have {DIM_COUNT} dims, got {len(vals)}"
            )
        clipped = tuple(max(0.0, min(1.0, v)) for v in vals)
        # frozen → bypass via object.__setattr__
        object.__setattr__(self, "values", clipped)

    @classmethod
    def neutral(cls) -> "PersonaVector":
        return cls()

    @classmethod
    def from_scalar(cls, scalar: float) -> "PersonaVector":
        """Broadcast a scalar to all DIM_COUNT axes (used for v1 → v2 upgrade)."""
        s = max(0.0, min(1.0, float(scalar)))
        return cls(values=tuple([s] * DIM_COUNT))

    def fit(self, signature: tuple[float, ...] | list[float]) -> float:
        """``Fit(persona, signature) = dot / DIM_COUNT`` ∈ ``[0, 1]``.

        Both vectors are clipped to ``[0, 1]^7``, so the dot product is in
        ``[0, 7]`` and the normalised fit is in ``[0, 1]``.
        """
        sig = tuple(float(v) for v in signature)
        if len(sig) != DIM_COUNT:
            raise PersonaModelError(
                f"signature must have {DIM_COUNT} dims, got {len(sig)}"
            )
        sig = tuple(max(0.0, min(1.0, v)) for v in sig)
        dot = sum(p * s for p, s in zip(self.values, sig))
        return dot / DIM_COUNT

    def as_dict(self) -> dict[str, float]:
        """Named-axis dict for human-readable logging / debugging."""
        return {name: v for name, v in zip(PERSONA_DIMS, self.values)}

    def to_list(self) -> list[float]:
        """List form for json.dumps; tuples don't survive jsonl round-trip."""
        return list(self.values)

    @classmethod
    def from_list(cls, values: list[float] | tuple[float, ...]) -> "PersonaVector":
        return cls(values=tuple(values))

    def mean(self) -> float:
        """v2 → v1 projection used by ``serialize_v2`` for dual-track logging."""
        return sum(self.values) / DIM_COUNT


# ---------------------------------------------------------------------------
# BeliefStore (one per agent; maps neighbour_id -> PersonaVector)
# ---------------------------------------------------------------------------


class BeliefStore:
    """Per-agent map ``neighbour_id -> PersonaVector``.

    Mutable (we update beliefs in place per audit event), but each stored
    PersonaVector is itself immutable. Missing keys default to the neutral
    vector so that ``Fit`` is well-defined for first-time-seen neighbours.
    """

    __slots__ = ("_beliefs",)

    def __init__(self) -> None:
        self._beliefs: dict[str, PersonaVector] = {}

    def get(self, neighbour_id: str, default: PersonaVector | None = None) -> PersonaVector:
        return self._beliefs.get(neighbour_id, default or PersonaVector.neutral())

    def set(self, neighbour_id: str, vec: PersonaVector) -> None:
        self._beliefs[neighbour_id] = vec

    def keys(self) -> list[str]:
        return list(self._beliefs.keys())

    def __contains__(self, neighbour_id: str) -> bool:
        return neighbour_id in self._beliefs

    def __len__(self) -> int:
        return len(self._beliefs)

    def to_v2_dict(self) -> dict[str, list[float]]:
        return {nid: vec.to_list() for nid, vec in self._beliefs.items()}

    def to_v1_dict(self) -> dict[str, float]:
        """Mean-projected scalar dict for backward-compat consumers."""
        return {nid: vec.mean() for nid, vec in self._beliefs.items()}

    @classmethod
    def from_v2_dict(cls, d: dict[str, list[float]]) -> "BeliefStore":
        store = cls()
        for nid, vals in d.items():
            store.set(nid, PersonaVector.from_list(vals))
        return store

    @classmethod
    def from_v1_dict(cls, d: dict[str, float]) -> "BeliefStore":
        """Broadcast each scalar to all DIM_COUNT axes (legacy upgrade path)."""
        store = cls()
        for nid, scalar in d.items():
            store.set(nid, PersonaVector.from_scalar(scalar))
        return store


# ---------------------------------------------------------------------------
# Evidence extraction + EMA update
# ---------------------------------------------------------------------------


def evidence_extract(
    audit_event: AuditEvent,
    task_signature: tuple[float, ...] | list[float],
) -> PersonaVector:
    """Project one audit event onto the 7 persona axes.

    Intuition: when the downstream agent did *well* (``value_gain`` high), this
    is positive evidence on whichever task axes were most demanded by ``phi(z)``.
    When the downstream did *poorly* (``rework_cost`` high), this is negative
    evidence — but only on the demanded axes (no signal on axes the task did
    not exercise).

    Concretely, for each axis k::

        evidence[k] = task_signature[k] * value_gain
                    + (1 - task_signature[k]) * (1 - rework_cost) * 0.5

    The second term keeps non-demanded axes drifting toward the neutral 0.5
    so a single bad audit on a comparison-heavy task does not collapse the
    agent's belief about the neighbour's decomposition skill. ``timeliness``
    is folded in as a multiplicative dampener: late deliveries reduce the
    information value of the audit signal.

    All output coordinates are clipped to ``[0, 1]``.
    """
    sig = tuple(float(v) for v in task_signature)
    if len(sig) != DIM_COUNT:
        raise PersonaModelError(
            f"task_signature must have {DIM_COUNT} dims, got {len(sig)}"
        )

    vg = float(audit_event.value_gain)
    rc = float(audit_event.rework_cost)
    timeliness = max(0.05, float(audit_event.timeliness))  # avoid full collapse

    evidence: list[float] = []
    for k in range(DIM_COUNT):
        s = max(0.0, min(1.0, sig[k]))
        on_axis = s * vg
        off_axis = (1.0 - s) * (1.0 - rc) * 0.5
        raw = on_axis + off_axis
        # apply timeliness dampener (pull toward NEUTRAL_INIT proportionally)
        damped = NEUTRAL_INIT + (raw - NEUTRAL_INIT) * timeliness
        evidence.append(max(0.0, min(1.0, damped)))
    return PersonaVector(values=tuple(evidence))


def apply_evidence(
    belief: PersonaVector,
    evidence: PersonaVector,
    nu: float = EMA_NU_DEFAULT,
) -> PersonaVector:
    """Standard EMA update::

        new_belief[k] = (1 - nu) * belief[k] + nu * evidence[k]

    ``nu`` clipped to ``[0, 1]``. Result is automatically clipped by
    :class:`PersonaVector`'s constructor.
    """
    nu_c = max(0.0, min(1.0, float(nu)))
    new_vals = tuple(
        (1.0 - nu_c) * b + nu_c * e for b, e in zip(belief.values, evidence.values)
    )
    return PersonaVector(values=new_vals)


def update_belief_from_audit(
    store: BeliefStore,
    neighbour_id: str,
    audit_event: AuditEvent,
    task_signature: tuple[float, ...] | list[float],
    nu: float = EMA_NU_DEFAULT,
) -> PersonaVector:
    """One-shot helper: extract evidence, apply EMA, write back. Returns the new vector."""
    prior = store.get(neighbour_id)
    evidence = evidence_extract(audit_event, task_signature)
    new = apply_evidence(prior, evidence, nu=nu)
    store.set(neighbour_id, new)
    return new


# ---------------------------------------------------------------------------
# Dual-track persistence (C-3 hard constraint)
# ---------------------------------------------------------------------------


def serialize_v2(store: BeliefStore) -> dict[str, Any]:
    """Emit dual-track payload: v2 vector PLUS v1 scalar projection.

    R0 baseline ``validate_logs.py`` reads ``competence_v1_scalar`` for
    historical comparability; new tooling reads ``competence_v2_vector``.
    """
    return {
        "schema_version": SCHEMA_V2,
        SCHEMA_V1: store.to_v1_dict(),
        SCHEMA_V2: store.to_v2_dict(),
    }


def deserialize(record: dict[str, Any]) -> BeliefStore:
    """Read either v1 or v2 records into a BeliefStore.

    Selection rules:

      - If the record contains a ``competence_v2_vector`` key with a non-empty
        dict, use it.
      - Else if it contains ``competence_v1_scalar`` (legacy path), broadcast
        each scalar to all 7 axes.
      - Else if ``schema_version == SCHEMA_V1`` and the record itself looks
        like a flat scalar dict (very old path), accept it.
      - Otherwise raise.

    Forward-compat: unknown extra keys are silently dropped (per pinned C-3).
    """
    if not isinstance(record, dict):
        raise PersonaModelError(
            f"deserialize expects a dict, got {type(record).__name__}"
        )

    schema = record.get("schema_version")

    v2 = record.get(SCHEMA_V2)
    if isinstance(v2, dict) and v2:
        return BeliefStore.from_v2_dict(v2)

    v1 = record.get(SCHEMA_V1)
    if isinstance(v1, dict):
        return BeliefStore.from_v1_dict(v1)

    if schema == SCHEMA_V1:
        # Very-old layout: the record IS the scalar dict (no nested key).
        flat = {k: v for k, v in record.items() if k != "schema_version"}
        if flat and all(isinstance(v, (int, float)) for v in flat.values()):
            return BeliefStore.from_v1_dict(flat)  # type: ignore[arg-type]

    raise PersonaModelError(
        f"deserialize cannot recognise record (schema_version={schema!r}, "
        f"keys={sorted(record.keys())})"
    )
