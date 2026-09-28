"""Audit the intentional incomplete replay produced by a pending-attribution run."""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    events = json.loads((run / "ledger.json").read_text(encoding="utf-8"))
    replay = replay_ledger_events(events, allow_incomplete=True)
    missing = list(replay.missing)
    expected_missing = [{"stage": "role_evidence_update", "delivery_id": "delivery-0"}]
    errors = []
    passed = replay.status == "UNKNOWN" and missing == expected_missing and not errors
    result = {
        "audit_version": "pipe3-pending-replay-audit-v1",
        "run_dir": str(run), "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "event_count": len(events), "replay_status": replay.status,
        "missing": missing, "errors": errors, "expected_missing": expected_missing,
        "passed": passed, "policy_update_allowed": False,
        "scientific_claim_allowed": False,
        "interpretation": "terminal outcome is present; role evidence is intentionally absent pending attribution",
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    with (out / "raw.jsonl").open("w", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": result["created_at_utc"],
                                 "event_type": "pending_replay_audit", "payload": result},
                                ensure_ascii=False) + "\n")
    print(json.dumps({"passed": passed, "replay_status": replay.status,
                      "missing": missing, "policy_update_allowed": False}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
