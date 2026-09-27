"""Bounded zero-LLM PIPE3 Qp/Qr/adoption and ledger-lineage preflight.

This root-specific seam deliberately does not use the DIST1 live runner.  It
executes frozen source variants through the two independent scorer workers and
records a strict selection -> delivery -> Qp -> judgment -> action -> outcome
-> evidence chain.  It is qualification evidence, never a role-learning result.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_producer_scorer import run_producer_scorer  # noqa: E402
from peerrolebench_pipe3_recipient_scorer import run_scorer  # noqa: E402
from peerrolebench_pipe3_producer_scorer_qualification import (  # noqa: E402
    correct_producer, interfaces,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, RecipientJudgment,
    RoleEvidenceUpdate, TerminalOutcome, ProducerScore,
)


def processor_variant(source: str, *, envelope: bool, latin1: bool) -> str:
    if not envelope:
        old = '            envelope = {"data": processed}\n            fout.write(json.dumps(envelope, ensure_ascii=False) + "\\n")'
        new = '            fout.write(json.dumps(processed, ensure_ascii=False) + "\\n")'
        if old not in source:
            raise ValueError("PIPE3 envelope patch anchor missing")
        source = source.replace(old, new, 1)
    if not latin1:
        old = 'open(output_path, "w", encoding="latin-1")'
        if old not in source:
            raise ValueError("PIPE3 encoding patch anchor missing")
        source = source.replace(old, 'open(output_path, "w", encoding="utf-8")', 1)
    return source


def score_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False).encode()).hexdigest()


def append_event(out, ledger, event_type, value):
    getattr(ledger, {
        "selection": "record_selection", "delivery": "record_delivery",
        "producer_score": "record_producer_score", "judgment": "record_judgment",
        "action": "record_action", "outcome": "record_outcome",
        "evidence": "record_evidence_update",
    }[event_type])(value)
    out.append(ledger.events[-1])


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=False, exist_ok=False)
    raw = out / "raw.jsonl"

    def log(event_type, payload):
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    config = {"qualification_version": "pipe3-lineage-preflight-v2",
              "task_id": "PIPE3_stream_processing", "seeds": [0, 1],
              "controls": ["all_correct", "producer_bad", "recipient_envelope_bad",
                           "recipient_encoding_bad", "both_bad", "unknown_scorer_no_update"],
              "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
              "controller_update_allowed": False, "scientific_claim_allowed": False,
              "unknown_never_updates": True}
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    results = []

    for seed in config["seeds"]:
        materials = build_materials(load_pipe3(seed))
        info = interfaces(materials)
        public = materials["agent_payloads"]["producer"]["source_files"]
        producer_original = public["producer.py"]
        producer_correct = correct_producer(producer_original, info)
        processor_original = materials["agent_payloads"]["recipient"]["source_files"]["processor.py"]
        processor_correct = processor_variant(processor_original, envelope=False, latin1=False)
        variants = {
            "all_correct": (producer_correct, processor_correct, {"qp": 1, "qr": 1, "adoption": 1}),
            "producer_bad": (producer_original, processor_correct, {"qp": 0, "qr": 1, "adoption": 0}),
            "recipient_envelope_bad": (producer_correct,
                                        processor_variant(processor_original, envelope=True, latin1=False),
                                        {"qp": 1, "qr": 0, "adoption": 0}),
            "recipient_encoding_bad": (producer_correct,
                                        processor_variant(processor_original, envelope=False, latin1=True),
                                        {"qp": 1, "qr": 0, "adoption": 0}),
            "both_bad": (producer_original, processor_original, {"qp": 0, "qr": 0, "adoption": 0}),
        }
        for name, (producer_text, processor_text, expected) in variants.items():
            case_dir = out / f"seed_{seed}" / name
            case_dir.mkdir(parents=True)
            sources = {"producer.py": producer_text, "processor.py": processor_text,
                       "models.py": public["models.py"], "sink.py": public["sink.py"]}
            log("case_start", {"seed": seed, "case": name,
                                "source_digests": {path: hashlib.sha256(text.encode()).hexdigest()
                                                   for path, text in sources.items()}})
            qp_dir = case_dir / "producer_score"; qr_dir = case_dir / "recipient_score"
            adoption_dir = case_dir / "adoption_score"
            qp = run_producer_scorer({"producer.py": producer_text, "models.py": public["models.py"]},
                                     info, "PIPE3_stream_processing", seed, qp_dir, log)
            qr = run_scorer({"processor.py": processor_text, "models.py": public["models.py"]},
                            info, "recipient", "PIPE3_stream_processing", seed, qr_dir, log)
            adoption = run_scorer(sources, info, "adoption", "PIPE3_stream_processing", seed,
                                  adoption_dir, log)

            ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
            records = []
            selection = PeerSelection(f"selection-{seed}-{name}", "PIPE3_stream_processing", seed,
                                      "recipient", "producer", ("producer",), "producer", 1.0)
            append_event(records, ledger, "selection", selection)
            ledger.record_task_start("PIPE3_stream_processing", seed)
            records.append(ledger.events[-1])
            producer_digest = digest_files({"producer.py": producer_text})
            delivery = Delivery(f"delivery-{seed}-{name}", "PIPE3_stream_processing", "producer",
                                "recipient", producer_digest, f"produce-{seed}-{name}", seed,
                                selection.selection_id)
            append_event(records, ledger, "delivery", delivery)
            append_event(records, ledger, "producer_score", ProducerScore(
                f"producer-score-{seed}-{name}", delivery.delivery_id, producer_digest,
                qp.get("scorer_version", "unknown"), qp.get("status", "UNKNOWN"), qp.get("label"),
                qp.get("quality_score"), qp.get("response_digest"),
                bool(qp.get("coverage_complete")), bool(qp.get("decision_complete"))))
            success = qr.get("status") == "PASS" and adoption.get("status") == "PASS"
            decision = "accept" if success else "reject_redo"
            judgment = RecipientJudgment(f"judgment-{seed}-{name}", delivery.delivery_id,
                                         "recipient", decision, producer_digest)
            append_event(records, ledger, "judgment", judgment)
            action = ConsumerAction(f"action-{seed}-{name}", delivery.delivery_id, "recipient",
                                    success, producer_digest, None, 0.0,
                                    "use" if success else "independent_redo")
            append_event(records, ledger, "action", action)
            adoption_digest = adoption.get("response_digest")
            outcome = TerminalOutcome(f"outcome-{seed}-{name}", delivery.delivery_id, success,
                                       "pipe3-recipient-objective-v1/adoption",
                                       adoption.get("quality_score"), adoption_digest)
            append_event(records, ledger, "outcome", outcome)
            append_event(records, ledger, "evidence", RoleEvidenceUpdate(
                f"evidence-{seed}-{name}", judgment.judgment_id, action.action_id,
                outcome.outcome_id, "pipe3-lineage-preflight-v1", 1.0))
            replay = replay_ledger_events(records)
            observed = {"seed": seed, "case": name,
                        "expected": expected,
                        "observed": {"qp": qp.get("label"), "qr": qr.get("label"),
                                     "adoption": adoption.get("label"), "outcome": int(success)},
                        "status": {"qp": qp.get("status"), "qr": qr.get("status"),
                                   "adoption": adoption.get("status")},
                        "ledger_status": replay.status, "ledger_event_count": replay.event_count,
                        "update_allowed": False}
            results.append(observed)
            log("case_result", observed)
            (case_dir / "ledger.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")

    # A scorer transport/schema mutation is not a negative example.  The
    # strict ledger may retain the UNKNOWN producer score for audit, but it
    # must stop before judgment, action, terminal outcome, evidence, or any
    # controller update.  This control exercises that boundary without
    # inventing a downstream result.
    unknown_dir = out / "unknown_scorer_no_update"
    unknown_dir.mkdir(parents=True)
    materials = build_materials(load_pipe3(0))
    info = interfaces(materials)
    public = materials["agent_payloads"]["producer"]["source_files"]
    producer_digest = digest_files({"producer.py": public["producer.py"]})
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    records = []
    selection = PeerSelection("selection-unknown", "PIPE3_stream_processing", 0,
                              "recipient", "producer", ("producer",), "producer", 1.0)
    append_event(records, ledger, "selection", selection)
    ledger.record_task_start("PIPE3_stream_processing", 0)
    records.append(ledger.events[-1])
    delivery = Delivery("delivery-unknown", "PIPE3_stream_processing", "producer", "recipient",
                        producer_digest, "produce-unknown", 0, selection.selection_id)
    append_event(records, ledger, "delivery", delivery)
    append_event(records, ledger, "producer_score", ProducerScore(
        "producer-score-unknown", delivery.delivery_id, producer_digest,
        "pipe3-producer-objective-v1", "UNKNOWN", None, None, None, False, False))
    replay = replay_ledger_events(records, allow_incomplete=True)
    unknown_control = {
        "status": replay.status,
        "complete": replay.complete,
        "missing": list(replay.missing),
        "snapshot": replay.snapshot,
        "producer_score_status": "UNKNOWN",
        "judgment_count": replay.snapshot["judgment_count"],
        "action_count": replay.snapshot["action_count"],
        "outcome_count": replay.snapshot["outcome_count"],
        "evidence_count": replay.snapshot["evidence_count"],
        "update_allowed": False,
    }
    (unknown_dir / "ledger.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    log("unknown_scorer_no_update", unknown_control)
    unknown_control_passed = (
        unknown_control["status"] == "UNKNOWN"
        and not unknown_control["complete"]
        and unknown_control["judgment_count"] == 0
        and unknown_control["action_count"] == 0
        and unknown_control["outcome_count"] == 0
        and unknown_control["evidence_count"] == 0
        and not unknown_control["update_allowed"]
    )

    passed = all(item["observed"]["qp"] == item["expected"]["qp"]
                 and item["observed"]["qr"] == item["expected"]["qr"]
                 and item["observed"]["adoption"] == item["expected"]["adoption"]
                 and item["ledger_status"] == "PASS" and not item["update_allowed"]
                 for item in results)
    summary = {**config, "passed": passed and unknown_control_passed, "results": results,
               "unknown_control": unknown_control,
               "unknown_control_passed": unknown_control_passed,
               "scorer_is_qualified": False, "benchmark_qualified": False,
               "scientific_claim_allowed": False,
               "remaining_gates": [
                   "real runner adapter and candidate/hidden scorer process separation",
                   "second independent structural root and same-information baselines",
               ]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"passed": passed, "scorer_is_qualified": False,
                      "benchmark_qualified": False}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
