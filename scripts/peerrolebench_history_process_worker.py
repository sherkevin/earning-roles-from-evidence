"""Child-process replay worker for the peer-history persistence qualification.

The worker deliberately receives only serialized history snapshots and selector
inputs.  It never imports the canonical task ledger and never calls a model.
Even malformed input produces a structured UNKNOWN receipt before a non-zero
exit, so the parent cannot mistake a process failure for an empty history.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_history_selector import select_from_public_history  # noqa: E402
from peerrolebench_peer_history import PeerHistoryV1  # noqa: E402


VERSION = "peer-history-process-worker-v1"


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, default=str,
    ).encode("utf-8")).hexdigest()


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n",
                    encoding="utf-8")


def run(*, bundle_path: Path, output_path: Path, candidate_keys: list[str],
        base_scores: list[float], read_cut: int, rng_seed: int,
        target_scope_key: str | None) -> int:
    receipt: dict[str, object] = {
        "worker_version": VERSION,
        "pid": os.getpid(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "UNKNOWN",
        "selection": None,
        "update_count": 0,
    }
    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        if bundle.get("schema") != "peer-history-process-bundle-v1":
            raise ValueError("unsupported process bundle schema")
        snapshots = bundle.get("histories")
        if not isinstance(snapshots, dict) or set(snapshots) != set(candidate_keys):
            raise ValueError("history bundle keys do not match candidate menu")
        histories = {
            key: PeerHistoryV1.replay(snapshots[key]) for key in candidate_keys
        }
        projections = {
            key: histories[key].selector_projection(candidate_key=key)
            for key in candidate_keys
        }
        selection = select_from_public_history(
            candidate_keys=candidate_keys, projections=projections,
            base_scores=base_scores, read_cut=read_cut, rng_seed=rng_seed,
            target_scope_key=target_scope_key,
        )
        receipt.update({
            "status": "PASS",
            "state_digests": {key: histories[key].state_digest() for key in candidate_keys},
            "projection_digests": selection["projection_digests"],
            "selection": selection,
            "snapshot_sha256": _digest(bundle),
        })
        _write(output_path, receipt)
        return 0
    except Exception as exc:  # fail closed, preserving structured evidence
        receipt.update({
            "status": "UNKNOWN",
            "unknown_reason": f"{type(exc).__name__}: {exc}",
            "snapshot_sha256": None,
        })
        _write(output_path, receipt)
        return 2
    finally:
        receipt["ended_at_utc"] = datetime.now(timezone.utc).isoformat()
        # Rewrite so the end timestamp is present for both pass and failure.
        _write(output_path, receipt)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-keys", type=str, required=True)
    parser.add_argument("--base-scores", type=str, required=True)
    parser.add_argument("--read-cut", type=int, required=True)
    parser.add_argument("--rng-seed", type=int, required=True)
    parser.add_argument("--target-scope-key", type=str, default=None)
    args = parser.parse_args()
    return run(
        bundle_path=args.bundle, output_path=args.output,
        candidate_keys=list(json.loads(args.candidate_keys)),
        base_scores=list(json.loads(args.base_scores)), read_cut=args.read_cut,
        rng_seed=args.rng_seed, target_scope_key=args.target_scope_key,
    )


if __name__ == "__main__":
    raise SystemExit(main())
