from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_real_closed_loop import (  # noqa: E402
    append_event,
    append_producer_score,
    producer_interface_names,
    producer_scorer_sources,
)
from peerrolebench_task_contract import export_task_materials, load_generated_task  # noqa: E402
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction,
    Delivery,
    PeerRoleLedger,
    PeerSelection,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)


DIGEST = "a" * 64
OUT = "b" * 64


def test_operator_source_names_are_derived_without_consumer_files():
    materials = export_task_materials(load_generated_task("DIST1_queue_race", 0))
    source = materials["agent_payloads"]["producer"]["source_files"]
    card = {"source_import_allowlist": [
        "__future__", "collections", "dataclasses", "functools", "heapq", "itertools",
        "math", "mqueue", "queue", "threading", "time", "typing", "uuid",
    ]}
    assert producer_interface_names(source, card) == {"queue": "TaskQueue", "priority": "PriorityTask"}


def test_producer_scorer_receives_actual_delivery_not_template():
    materials = export_task_materials(load_generated_task("DIST1_queue_race", 0))
    template = materials["agent_payloads"]["producer"]["source_files"]
    delivery = {"mqueue/queue.py": template["mqueue/queue.py"] + "\n# delivered-change",
                "mqueue/priority.py": template["mqueue/priority.py"]}
    source = producer_scorer_sources(materials, delivery)
    assert source["mqueue/queue.py"].endswith("# delivered-change")
    assert "mqueue/consumer.py" not in source


def test_unknown_producer_score_is_recorded_but_not_a_label(tmp_path):
    out = tmp_path
    (out / "raw.jsonl").touch()

    def log(event_type, payload):
        with (out / "raw.jsonl").open("a") as handle:
            handle.write(json.dumps({"event_type": event_type, "payload": payload}) + "\n")

    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    append_event(out, ledger, "record_selection", PeerSelection(
        "s0", "task", 0, "selector", "producer", ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start("task", 0)
    (out / "ledger.json").write_text(json.dumps(ledger.events))
    delivery = Delivery("d0", "task", "peer-a", "recipient", DIGEST, "produce-0", 0, "s0")
    append_event(out, ledger, "record_delivery", delivery)
    append_producer_score(out, ledger, delivery, {
        "status": "UNKNOWN", "label": None, "quality_score": None,
        "scorer_version": "producer-v1", "response_digest": None,
        "coverage_complete": False,
    })
    judgment = RecipientJudgment("j0", "d0", "recipient", "accept", DIGEST)
    append_event(out, ledger, "record_judgment", judgment)
    action = ConsumerAction("a0", "d0", "recipient", True, DIGEST, OUT, action="use")
    append_event(out, ledger, "record_action", action)
    outcome = TerminalOutcome("o0", "d0", True, "consumer-v1", 1.0, OUT)
    append_event(out, ledger, "record_outcome", outcome)
    append_event(out, ledger, "record_evidence_update",
                 RoleEvidenceUpdate("e0", "j0", "a0", "o0", "u1", 1.0))
    replay = replay_ledger_events(ledger.events)
    assert replay.status == "PASS"
    score = replay.ledger.producer_scores["producer-score-d0"]
    assert score.status == "UNKNOWN" and score.label is None
