"""Read-only inventory of the historical C1 episode schema, never a policy gate.

Preserve observed scores and their dependency; do not infer an objective
PASS/FAIL from a recipient opinion. Caller-provided lineage is descriptive.
Native sidecar, assignment, read-cut and credit validation remain separate.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Mapping

from peerrolebench_baseline_contract import BASELINE_ARM_SPECS
from peerrolebench_policy_projection import RAW_ACCEPTANCE_MAPPING_VERSION
from peerrolebench_role_evidence_scorer import JUDGMENT_LABELS, JUDGMENT_MAPPING_VERSION
from peerrolebench_terminal_outcome_projection import TERMINAL_LABEL_MAPPING_VERSION

CONTRACT_VERSION = "c1-signal-inventory-v1"
CHANNELS = ("Qp", "J", "A", "D", "Y", "L")
ARM_NAMES = tuple(spec.name for spec in BASELINE_ARM_SPECS)


def digest_payload(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def inventory_episode(episode: Mapping[str, Any], *, arm: str | None = None) -> dict[str, Any]:
    """Describe a C1 episode; not a converter for arbitrary benchmark outcomes."""
    if not isinstance(episode, Mapping):
        raise TypeError("episode must be a mapping")
    if arm is not None and arm not in ARM_NAMES and arm != "contextual_trust_linear":
        raise ValueError(f"unknown baseline arm: {arm!r}")

    def section(name: str) -> dict[str, Any]:
        value = episode.get(name)
        return deepcopy(dict(value)) if isinstance(value, Mapping) else {}

    producer, judgment, action = section("producer_score"), section("judgment"), section("action")
    adoption, outcome, recipient = section("adoption_score"), section("outcome"), section("recipient_score")
    decision = judgment.get("decision")
    judgment_label = JUDGMENT_LABELS.get(decision) if isinstance(decision, str) else None

    def score(channel: str, source_key: str, observed: dict[str, Any]) -> dict[str, Any]:
        return {
            "channel": channel, "source_key": source_key,
            "observation_status": "RECORDED" if observed else "MISSING",
            "observed": observed, "policy_eligible": False,
        }

    rows = [score("Qp", "producer_score", producer), {
        "channel": "J", "source_key": "judgment", "observed": judgment,
        "observation_status": "RECORDED" if judgment_label is not None else "UNKNOWN",
        "mapped_judgment_label": judgment_label, "mapping_version": JUDGMENT_MAPPING_VERSION,
        "policy_eligible": False,
    }, {
        "channel": "A", "source_key": "action",
        "observed": {k: v for k, v in action.items() if k != "source_files"},
        "observation_status": "RECORDED" if action else "MISSING",
        "policy_eligible": False,
    }, score("D", "adoption_score", adoption), {
        **score("Y", "outcome", outcome),
        "derived_from": ("D", "recipient"),
        "derivation": "C1 outcome quality copies D.quality_score when D and recipient checks are complete; status requires both PASS",
        "independent_terminal_measurement": False,
    }, {
        "channel": "L", "source_key": "external_peer_history_assignment_binding",
        "observation_status": "NOT_AUDITED", "observed": None,
        "reason": "This inventory does not load native peer-history/assignment credit; no absence or validity conclusion",
        "policy_eligible": False,
    }]
    return {
        "contract_version": CONTRACT_VERSION, "arm": arm,
        "episode_identity_unvalidated": {key: episode.get(key) for key in (
            "decision_index", "selection_id", "selected_key", "delivery_id", "artifact_digest",
            "judgment_id", "action_id", "outcome_id")},
        "signals": rows, "recipient_score_diagnostic": recipient,
        "terminal_baseline_qualified": False, "native_lineage_validated": False,
        "scientific_claim_allowed": False,
    }


def default_arm_contracts() -> dict[str, dict[str, Any]]:
    """Inventory registered obligations, without establishing implementation parity."""
    versions = {"raw_acceptance": RAW_ACCEPTANCE_MAPPING_VERSION,
                "recipient_judgment": JUDGMENT_MAPPING_VERSION,
                "terminal_outcome": TERMINAL_LABEL_MAPPING_VERSION}
    result = {s.name: {
        "arm": s.name, "accepted_sources": s.accepted_sources,
        "visibility_profile": s.visibility_profile, "update_rule": s.update_rule,
        "mapping_versions": tuple(versions[x] for x in s.accepted_sources),
        "correction_support": s.correction_support, "parity_qualified": False,
    } for s in BASELINE_ARM_SPECS}
    result["contextual_trust_linear"] = {
        "arm": "contextual_trust_linear", "registry_family": "contextual_trust",
        "accepted_sources": ("recipient_judgment",),
        "implementation": "FeatureContextualTrustPolicy (diagonal RLS); differs from ContextualTrustPolicy (Beta)",
        "algorithm_equivalent_to_registry_implementation": False, "parity_qualified": False,
    }
    return result
