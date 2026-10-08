"""Declarative contract for the ArtifactRole baseline matrix.

This module is intentionally small and model-free.  It does not choose a
baseline or claim that the matrix is scientifically fair.  It makes the
comparison obligations explicit so a root runner cannot silently omit an
information channel, an UNKNOWN rule, or a cost component.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Sequence


BASELINE_CONTRACT_VERSION = "artifactrole-baselines-v1"
COST_FIELDS = (
    "producer", "recipient", "judge", "scorer", "selection", "policy_update",
    "retry", "communication", "repair", "replay", "state", "api_calls",
    "input_tokens", "output_tokens", "gpu_seconds", "wall_seconds",
)
_COST_UNITS = {
    "producer": "seconds", "recipient": "seconds", "judge": "seconds",
    "scorer": "seconds", "selection": "seconds", "policy_update": "seconds",
    "retry": "count", "communication": "records", "repair": "count",
    "replay": "records", "state": "bytes", "api_calls": "count",
    "input_tokens": "tokens", "output_tokens": "tokens",
    "gpu_seconds": "seconds", "wall_seconds": "seconds",
}
UNKNOWN_RULE = "unknown_no_update_with_reason"


@dataclass(frozen=True)
class BaselineArmSpec:
    """Information and update obligations for one policy arm."""

    name: str
    track: str
    accepted_sources: tuple[str, ...]
    history_scope: str
    update_rule: str
    correction_support: str
    visibility_profile: str
    comparison_group: str
    parity_status: str


BASELINE_ARM_SPECS: tuple[BaselineArmSpec, ...] = (
    BaselineArmSpec(
        "uniform", "ArtifactRole", (), "none", "fixed_uniform", "ignore",
        "menu_only", "lower_bound", "ready_offline",
    ),
    BaselineArmSpec(
        "no_update", "ArtifactRole", (), "own", "frozen_prior", "ignore",
        "menu_context_without_feedback", "execution_control", "ready_offline",
    ),
    BaselineArmSpec(
        "raw_acceptance", "ArtifactRole", ("raw_acceptance",), "own",
        "acceptance_update", "ignore", "public_acceptance_only", "raw_control",
        "ready_offline",
    ),
    BaselineArmSpec(
        "terminal_only", "ArtifactRole", ("terminal_outcome",), "own",
        "terminal_update", "ignore", "independent_terminal_only", "terminal_control",
        "ready_offline",
    ),
    BaselineArmSpec(
        "contextual_trust", "ArtifactRole", ("recipient_judgment",), "own",
        "contextual_update", "unsupported_correction_no_update", "public_judgment_context",
        "same_information_control", "open_live_parity",
    ),
    BaselineArmSpec(
        "pooled_controller", "ArtifactRole", ("recipient_judgment",), "pooled_public",
        "pooled_contextual_update", "unsupported_correction_no_update",
        "pooled_public_judgment_context", "upper_bound_control", "open_live_parity",
    ),
    BaselineArmSpec(
        "RARE", "ArtifactRole", ("recipient_judgment",), "own",
        "responsibility_aware_update", "event_time_correction", "public_judgment_responsibility",
        "candidate_method", "open_live_parity",
    ),
)


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def contract_payload(
    specs: Sequence[BaselineArmSpec] = BASELINE_ARM_SPECS,
    *,
    cost_fields: Sequence[str] = COST_FIELDS,
    unknown_rule: str = UNKNOWN_RULE,
) -> dict[str, Any]:
    """Return a JSON-serializable, hashable contract snapshot."""

    return {
        "contract_version": BASELINE_CONTRACT_VERSION,
        "arms": [asdict(spec) for spec in specs],
        "cost_fields": list(cost_fields),
        "unknown_rule": unknown_rule,
        "requirements": {
            "same_menu_registry_and_schedule": True,
            "selected_only_feedback": True,
            "independent_live_history": True,
            "later_assignment_before_execution": True,
            "full_cost_ledger": True,
        },
    }


def contract_digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def validate_contract(
    specs: Sequence[BaselineArmSpec] = BASELINE_ARM_SPECS,
    *,
    cost_fields: Sequence[str] = COST_FIELDS,
    unknown_rule: str = UNKNOWN_RULE,
) -> dict[str, Any]:
    """Validate static obligations and return the sealed contract payload.

    The validator deliberately keeps ``open_live_parity`` as a valid status:
    the contract describes what must be tested, while the live runner decides
    whether that gate has actually passed.
    """

    specs = tuple(specs)
    names = [spec.name for spec in specs]
    if len(names) != len(set(names)):
        raise ValueError("baseline arm names must be unique")
    if set(names) != {spec.name for spec in BASELINE_ARM_SPECS}:
        raise ValueError("baseline arm set differs from the registered matrix")
    fields = tuple(cost_fields)
    if fields != COST_FIELDS:
        raise ValueError("cost field set/order differs from the registered contract")
    if unknown_rule != UNKNOWN_RULE:
        raise ValueError("UNKNOWN rule differs from the registered contract")
    for spec in specs:
        if spec.track != "ArtifactRole":
            raise ValueError(f"unsupported track for {spec.name}: {spec.track}")
        if not spec.visibility_profile or not spec.update_rule:
            raise ValueError(f"incomplete information/update contract for {spec.name}")
        if spec.name == "uniform" and spec.accepted_sources:
            raise ValueError("uniform cannot consume feedback")
        if spec.name == "RARE" and spec.correction_support != "event_time_correction":
            raise ValueError("RARE must declare event-time correction support")
        if spec.name == "contextual_trust" and spec.correction_support != "unsupported_correction_no_update":
            raise ValueError("contextual_trust correction behavior must be explicit")
    payload = contract_payload(specs, cost_fields=fields, unknown_rule=unknown_rule)
    payload["contract_digest"] = contract_digest(payload)
    return payload


def validate_cost_ledger(
    ledger: Mapping[str, Mapping[str, Any]],
    *,
    require_measured: bool,
) -> dict[str, dict[str, Any]]:
    """Validate per-arm cost receipts without fabricating measurements."""

    normalized: dict[str, dict[str, Any]] = {}
    for arm in sorted(ledger):
        row = ledger[arm]
        missing = [field for field in COST_FIELDS if field not in row]
        if missing:
            raise ValueError(f"{arm} cost ledger missing fields={missing}")
        clean: dict[str, Any] = {}
        for field in COST_FIELDS:
            cell = row[field]
            if not isinstance(cell, Mapping):
                raise ValueError(f"{arm}.{field} must be a mapping")
            value = cell.get("value")
            measured = bool(cell.get("measured", False))
            source = str(cell.get("source", ""))
            unit = str(cell.get("unit", ""))
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)) or float(value) < 0:
                raise ValueError(f"{arm}.{field}.value must be finite and non-negative")
            if not source:
                raise ValueError(f"{arm}.{field}.source is required")
            if unit != _COST_UNITS[field]:
                raise ValueError(f"{arm}.{field}.unit must be {_COST_UNITS[field]!r}")
            if require_measured and not measured:
                raise ValueError(f"{arm}.{field} is not measured")
            clean[field] = {
                "value": float(value), "measured": measured, "source": source,
                "unit": unit,
            }
        normalized[arm] = clean
    return normalized


__all__ = [
    "BASELINE_ARM_SPECS", "BASELINE_CONTRACT_VERSION", "COST_FIELDS",
    "UNKNOWN_RULE", "BaselineArmSpec", "contract_digest", "contract_payload",
    "validate_contract", "validate_cost_ledger",
]
