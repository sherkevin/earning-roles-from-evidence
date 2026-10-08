"""Versioned public PIPE3 behavior contract over the pinned v1 source payloads.

This module changes only actor-visible task prose. The trace below stays in the
parent manifest and is never included in either actor payload.
"""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from peerrolebench_pipe3_material_adapter import build_materials as build_v1_materials
from peerrolebench_pipe3_material_adapter import digest_files


CONTRACT_VERSION = "peerrolebench-pipe3-public-contract-v2"
MATERIAL_VERSION = "peerrolebench-pipe3-materials-v2"

# The IDs link public clauses to private checks without exposing the checks to actors.
CLAUSES = {
    "C1_interfaces": "Keep the public names, call signatures, event fields, and assigned file ownership unchanged.",
    "C2_producer_timestamp": "For every event, serialize its datetime timestamp as a string with a 'T' between date and time and no space in that timestamp.",
    "C3_producer_jsonl": "Produce UTF-8 JSON Lines: one complete event object per input event, in the same order, with every declared event field. Preserve field values except for the datetime serialization required by C2_producer_timestamp.",
    "C4_processor_jsonl": "Process each valid input event once, return the number processed, and write UTF-8 JSON Lines with one output object per input event in the same order.",
    "C5_sink_shape": "Write bare processed event objects with their declared fields at the top level; the public sink must be able to read each object directly.",
    "C6_processor_semantics": "Preserve all event fields and values, including non-ASCII text, except for uppercasing the categorical field named by the public schema (action, metric_type, or txn_type, as applicable), formatting the processed timestamp with a 'T' between date and time and no space, and adding processed_at. Do not drop or otherwise change event values.",
}

TRACE = {
    "C1_interfaces": ["P1_import", "R1_process", "A2_sink_adoption"],
    "C2_producer_timestamp": ["P2_iso_serialization", "A1_producer_boundary"],
    "C3_producer_jsonl": ["P3_batch_output", "T2_batch_cardinality", "T3_unicode_semantics"],
    "C4_processor_jsonl": ["R1_process", "T2_batch_cardinality"],
    "C5_sink_shape": ["R2_shape", "A2_sink_adoption", "T1_holdout_projection"],
    "C6_processor_semantics": ["R3_utf8_semantics", "T1_holdout_projection", "T3_unicode_semantics"],
}


def public_task_text(domain: str) -> dict[str, str]:
    requirements = "\n".join(f"- **{clause_id}**: {clause}" for clause_id, clause in CLAUSES.items())
    spec = f"""# PIPE3: Stream Processing Interoperability ({domain})

## Goal
Make the public producer -> processor -> sink pipeline interoperate for this event schema.

## Responsibilities
- The producer owns `producer.py`.
- The recipient owns `processor.py`.
- `models.py` and `sink.py` are read-only support files.

## Public behavior contract
{requirements}

Inspect the public interfaces and data flow before editing. Return only complete text
for files assigned to your role.
"""
    brief = f"""# PIPE3 stream task ({domain})

Repair the assigned component under the public behavior contract in the shared spec.
Preserve the public interfaces and return only complete text for files assigned to you.
"""
    return {"spec_md": spec, "brief_md": brief}


def build_materials(generated: Any) -> dict[str, Any]:
    materials = build_v1_materials(generated)
    task_text = public_task_text(str(materials["manifest"]["domain"]))
    for payload in materials["agent_payloads"].values():
        payload["task_text"] = deepcopy(task_text)
        payload["contract_clause_refs"] = list(CLAUSES)

    payloads = materials["agent_payloads"]
    manifest = materials["manifest"]
    manifest["schema_version"] = MATERIAL_VERSION
    manifest["public_contract_version"] = CONTRACT_VERSION
    manifest["payload_sha256"] = digest_files({
        role: json.dumps(payload, ensure_ascii=False, sort_keys=True)
        for role, payload in payloads.items()
    })
    manifest["public_contract_trace_parent_only"] = deepcopy(TRACE)
    manifest["public_contract_clauses_parent_only"] = deepcopy(CLAUSES)
    manifest["public_contract_trace_scope"] = "limited scorer check coverage mapping; no clause is necessarily fully verified by its mapped checks"
    manifest["scorer_version_pins_parent_only"] = {
        "producer": "pipe3-producer-objective-v2",
        "recipient_and_adoption": "pipe3-recipient-objective-v2",
        "terminal": "pipe3-terminal-holdout-v2",
    }
    # Source redaction and contract coverage alone do not qualify a scientific task.
    manifest["scientific_task_text_qualified"] = False
    manifest["scientific_qualification_note"] = "public contract coverage only; other qualification gates remain open"
    return materials
