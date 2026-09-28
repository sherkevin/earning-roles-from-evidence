"""Qualify the J/A/U/F factor seams without an API or a GPU run.

This is a schema/causal-order check, not a benchmark.  It deliberately builds
two complete protocol episodes so that a role-evidence update from episode 0
can be consumed by a later assignment before episode 1 starts.  The report
then distinguishes what the append-only ledger can express from what the
current policy sidecar/replay can actually prove the policy consumed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references/aamas"
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))

from peer_role_protocol_20260925 import (  # type: ignore[import-not-found]
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    ProducerScore,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)
from peerrolebench_ledger_replay import replay_ledger_events


def _digest(char: str) -> str:
    return char * 64


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_two_episode_ledger() -> PeerRoleLedger:
    """Build a valid two-episode ledger with future assignment consumption."""

    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    for index, artifact in enumerate((_digest("a"), _digest("b"))):
        propensity = 0.5 if index == 0 else 0.75
        # Episode 1 has an assignment recorded below, before this selection.
        ledger.record_selection(PeerSelection(
            selection_id=f"selection-{index}", task_id="PIPE3_stream_processing",
            task_index=index, selector_id="peer-a", role="producer",
            candidate_ids=("peer-b", "peer-c"), chosen_peer_id="peer-b",
            propensity=propensity,
        ))
        ledger.record_task_start("PIPE3_stream_processing", index)
        ledger.record_delivery(Delivery(
            delivery_id=f"delivery-{index}", task_id="PIPE3_stream_processing",
            producer_id="peer-b", recipient_id="peer-a", artifact_sha256=artifact,
            source_event_id=f"request-{index}", task_index=index,
            selection_id=f"selection-{index}",
        ))
        ledger.record_producer_score(ProducerScore(
            producer_score_id=f"producer-score-{index}",
            delivery_id=f"delivery-{index}", artifact_sha256=artifact,
            scorer_version="fixture-producer-v2", status="PASS", label=1,
            quality_score=1.0, score_payload_sha256=_digest("c"),
            coverage_complete=True, decision_complete=True,
        ))
        ledger.record_judgment(RecipientJudgment(
            judgment_id=f"judgment-{index}", delivery_id=f"delivery-{index}",
            consumer_id="peer-a", decision="accept",
            observed_artifact_sha256=artifact,
        ))
        ledger.record_action(ConsumerAction(
            action_id=f"action-{index}", delivery_id=f"delivery-{index}",
            consumer_id="peer-a", used_artifact=True,
            input_artifact_sha256=artifact, output_artifact_sha256=_digest("d"),
            action="use",
        ))
        ledger.record_outcome(TerminalOutcome(
            outcome_id=f"outcome-{index}", delivery_id=f"delivery-{index}",
            success=True, scorer_version="fixture-terminal-v1", partial_score=1.0,
        ))
        ledger.record_evidence_update(RoleEvidenceUpdate(
            evidence_id=f"evidence-{index}", judgment_id=f"judgment-{index}",
            action_id=f"action-{index}", outcome_id=f"outcome-{index}",
            update_version="fixture-evidence-v1", arrived_at=float(10 + index),
        ))
        # Assignment must be inserted after evidence and before the next
        # episode's task starts.  It is intentionally created between the two
        # loop iterations below by the caller.
        if index == 0:
            ledger.record_assignment(LaterAssignment(
                assignment_id="assignment-1", task_id="PIPE3_stream_processing",
                task_index=1, agent_id="peer-b", role="producer",
                evidence_ids=("evidence-0",), decision_propensity=0.75,
            ))
    return ledger


def inspect_mapping(ledger: PeerRoleLedger) -> dict[str, Any]:
    events = ledger.events
    replay = replay_ledger_events(events, allow_incomplete=False)
    selections = list(ledger.selections.values())
    assignment = ledger.assignments["assignment-1"]
    next_selection = ledger.selections["selection-1"]

    protocol = {
        "J": {
            "name": "situated judgment and actual use",
            "expressible": all((ledger.judgments, ledger.actions)),
            "evidence": "recipient_judgment -> consumer_action with recipient/artifact binding",
        },
        "A": {
            "name": "responsibility attribution and UNKNOWN gate",
            "expressible": bool(ledger.producer_scores) and replay.status == "PASS",
            "evidence": "producer_score is a distinct event; strict replay preserves delivery lineage",
        },
        "U": {
            "name": "delayed online update",
            "expressible": True,
            "evidence": "the policy sidecar schema carries arrived_at/delay and replay orders feedback by arrival",
        },
        "F": {
            "name": "future assignment consumption",
            "expressible": bool(ledger.assignments),
            "evidence": "later_assignment cites evidence and is consumed by the next selection",
        },
    }

    protocol["F"]["assignment_consumed_by_ledger"] = (
        assignment.agent_id == next_selection.chosen_peer_id
        and assignment.decision_propensity == next_selection.propensity
    )
    sidecar_supported = {
        "J": True,  # raw judgment/action fields exist in FeedbackSidecar.
        "A": False,  # ProducerScore and attribution gate are outside sidecar coverage.
        "U": True,  # delay/order and policy update hooks exist.
        "F": False,  # assignment/evidence consumption is absent from sidecar/replay.
    }
    cells = []
    for bits in itertools.product((0, 1), repeat=4):
        enabled = dict(zip(("J", "A", "U", "F"), bits))
        cells.append({
            "condition_id": "".join(str(enabled[key]) for key in ("J", "A", "U", "F")),
            "enabled": enabled,
            "ledger_protocol_available": all(
                not enabled[key] or protocol[key]["expressible"] for key in enabled
            ),
            "policy_sidecar_seam_available": all(
                not enabled[key] or sidecar_supported[key] for key in enabled
            ),
            "scientific_cell_ready": False,
        })

    return {
        "status": "QUALIFIED_OFFLINE",
        "ledger_replay_status": replay.status,
        "ledger_snapshot": replay.snapshot,
        "module_mapping": protocol,
        "policy_sidecar_support": sidecar_supported,
        "supported_policy_cells": [cell["condition_id"] for cell in cells if cell["policy_sidecar_seam_available"]],
        "unsupported_policy_cells": [cell["condition_id"] for cell in cells if not cell["policy_sidecar_seam_available"]],
        "cells": cells,
        "scientific_claim_allowed": False,
        "reason": (
            "The ledger can express all four protocol stages, but the current "
            "policy sidecar/replay cannot attest producer-score attribution or "
            "policy consumption of later assignments."
        ),
    }


def run(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    config = {
        "experiment_id": "n03_factorial_mapping_qualification_20260928",
        "kind": "zero_llm_j_a_u_f_schema_and_causal_order_qualification",
        "runtime": {
            "started_at_utc": started,
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": _file_sha256(Path(__file__).resolve()),
            "protocol_sha256": _file_sha256(REFERENCE / "peer_role_protocol_20260925.py"),
        },
        "episodes": 2,
        "modules": ["J", "A", "U", "F"],
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    ledger = build_two_episode_ledger()
    result = inspect_mapping(ledger)
    raw = {
        "event_type": "factorial_mapping_result",
        "payload": {"ledger_events": ledger.events, "mapping": result},
    }
    (out_dir / "raw.jsonl").write_text(json.dumps(raw, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {
        "experiment_id": config["experiment_id"],
        "passed": result["status"] == "QUALIFIED_OFFLINE" and result["ledger_replay_status"] == "PASS",
        "status": result["status"],
        "module_mapping": result["module_mapping"],
        "supported_policy_cells": result["supported_policy_cells"],
        "unsupported_policy_cells": result["unsupported_policy_cells"],
        "ledger_snapshot": result["ledger_snapshot"],
        "scientific_claim_allowed": False,
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args.out_dir)
    print(json.dumps({
        "passed": summary["passed"],
        "status": summary["status"],
        "supported_policy_cells": summary["supported_policy_cells"],
        "unsupported_policy_cells": summary["unsupported_policy_cells"],
        "scientific_claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
