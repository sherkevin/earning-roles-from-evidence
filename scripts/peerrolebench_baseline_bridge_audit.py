"""Audit whether a PeerRole ledger can be mapped to BaselinePolicy inputs.

The current peer-role protocol intentionally stores only the causal ledger
fields.  This audit refuses to invent context, candidate versions, feature
schema or feedback arrival metadata when those fields are absent.  A
``NOT_MAPPABLE`` result is therefore useful progress: it identifies the exact
adapter fields required before a baseline can consume the ledger fairly.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


SELECTION_FIELDS = (
    "context_key", "candidate_versions", "base_scores", "state_version",
    "encoder_version", "feature_schema", "selected_at",
)
FEEDBACK_FIELDS = ("arrived_at", "delay", "disposition", "provenance")


def _records(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, list):
        return [row for row in value if isinstance(row, Mapping)]
    if isinstance(value, Mapping) and isinstance(value.get("events"), list):
        return [row for row in value["events"] if isinstance(row, Mapping)]
    raise ValueError("ledger must be a list or an object containing events")


def audit_records(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    missing = Counter()
    selection_count = 0
    feedback_count = 0
    selection_ids: set[str] = set()
    for row in rows:
        kind = row.get("event_type")
        payload = row.get("payload")
        if not isinstance(payload, Mapping):
            missing["malformed_payload"] += 1
            continue
        if kind == "peer_selection":
            selection_count += 1
            selection_ids.add(str(payload.get("selection_id")))
            for field in SELECTION_FIELDS:
                if field not in payload:
                    missing[f"selection.{field}"] += 1
            versions = payload.get("candidate_versions")
            ids = payload.get("candidate_ids")
            if "candidate_versions" in payload and isinstance(ids, list) and isinstance(versions, list):
                if len(ids) != len(versions):
                    missing["selection.candidate_versions_length"] += 1
        elif kind in {"recipient_judgment", "consumer_action", "terminal_outcome"}:
            feedback_count += 1
            for field in FEEDBACK_FIELDS:
                if field not in payload:
                    missing[f"feedback.{field}"] += 1
            if kind == "recipient_judgment" and "label" not in payload:
                missing["feedback.recipient_label_mapping"] += 1
            if kind == "terminal_outcome" and "label" not in payload:
                missing["feedback.terminal_label_mapping"] += 1
    status = "MAPPABLE" if not missing else "NOT_MAPPABLE"
    return {
        "status": status,
        "record_count": len(rows),
        "selection_count": selection_count,
        "feedback_event_count": feedback_count,
        "selection_ids": sorted(selection_ids),
        "missing": dict(sorted(missing.items())),
        "policy_update_allowed": status == "MAPPABLE",
        "scientific_claim_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = audit_records(_records(json.loads(args.ledger.read_text(encoding="utf-8"))))
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "MAPPABLE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
