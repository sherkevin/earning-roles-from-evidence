"""Zero-call adversarial qualification for multi-entry peer history boundaries."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_history_selector import select_from_public_history  # noqa: E402
from peerrolebench_peer_history import (  # noqa: E402
    AssignmentSealV1, HistoryCostV1, HistoryEntryV1, PeerHistoryV1,
)
from peerrolebench_history_four_cell_qualification import (  # noqa: E402
    CANDIDATES, READ_CUT, RNG_SEED, _fixture,
)


VERSION = "peer-history-adversarial-qualification-v1"
CELLS = ("valid-two-entry", "permuted-two-entry", "candidate-mismatch",
         "projection-rate-mutation", "scope-isolation")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, default=str,
    ).encode("utf-8")).hexdigest()


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n",
                    encoding="utf-8")


def _two_entry_history() -> PeerHistoryV1:
    _, _, _, original, _, _ = _fixture()
    history = deepcopy(original)
    role_hash = _digest("role-two")
    state_hash = _digest("state-two")
    seal = AssignmentSealV1(
        assignment_id="as2", subject_key="peer-a",
        role_signature_hash=role_hash,
        execution_state_fingerprint=state_hash,
        sealed_arrival_index=14,
        candidate_registry_digest=_digest("history-four-cell-registry-v1"),
    )
    entry = HistoryEntryV1(
        entry_id="history-as2", agent_key="peer-a", subject_key="peer-a",
        role_signature_hash=role_hash,
        execution_state_fingerprint=state_hash,
        delivery_digest=_digest("delivery-two"),
        recipient_judgment_id="j2", recipient_judgment_label=0.0,
        later_outcome_id="o2", later_outcome_label=0.0,
        metric_digest=_digest("metric-two"), cost=HistoryCostV1(wall_ms=2.0),
        arrival_index=20, assignment_id="as2", status="FAIL",
    )
    history.seal_assignment(seal)
    history.append(entry)
    return history


def _select(history: PeerHistoryV1, *, target_scope_key: str) -> dict[str, Any]:
    projections = {
        "peer-a@v1": history.selector_projection(candidate_key="peer-a@v1"),
        "peer-b@v1": PeerHistoryV1.empty("peer-b").selector_projection(
            candidate_key="peer-b@v1"
        ),
    }
    return select_from_public_history(
        candidate_keys=CANDIDATES, projections=projections,
        base_scores=(0.0, 0.0), read_cut=READ_CUT, rng_seed=RNG_SEED,
        target_scope_key=target_scope_key,
    )


def _run_cell(cell: str, history: PeerHistoryV1, target_scope_key: str) -> dict[str, Any]:
    started = time.perf_counter()
    row: dict[str, Any] = {
        "cell": cell, "status": "UNKNOWN", "update_count": 0,
        "target_scope_key": target_scope_key,
        "scientific_claim_allowed": False,
    }
    try:
        snapshot = history.snapshot()
        row.update({
            "entry_count": len(history.entries),
            "scope_count": len(history.selector_projection(candidate_key="peer-a@v1")["scopes"]),
            "state_digest": history.state_digest(),
            "snapshot_bytes": len(json.dumps(snapshot, sort_keys=True).encode()),
        })
        if cell == "valid-two-entry":
            restored = PeerHistoryV1.replay(snapshot)
            selection = _select(restored, target_scope_key=target_scope_key)
            row.update({"status": "PASS", "selection": selection,
                        "projection_digest": selection["projection_digests"]["peer-a@v1"]})
        elif cell == "permuted-two-entry":
            malformed = deepcopy(snapshot)
            malformed["entries"] = list(reversed(malformed["entries"]))
            payload = {key: malformed[key] for key in
                       ("schema", "version", "agent_key", "seals", "entries", "scopes")}
            malformed["state_digest"] = _digest(payload)
            PeerHistoryV1.replay(malformed)
            row.update({"status": "FAIL", "selection": None,
                        "unknown_reason": "permuted history unexpectedly replayed"})
        elif cell == "candidate-mismatch":
            history.selector_projection(candidate_key="peer-b@v1")
            row.update({"status": "FAIL", "selection": None,
                        "unknown_reason": "candidate mismatch unexpectedly projected"})
        elif cell == "projection-rate-mutation":
            mutated = deepcopy(snapshot)
            first_scope = next(iter(mutated["scopes"].values()))
            first_scope["smoothed_rate"] = 1.0
            payload = {key: mutated[key] for key in
                       ("schema", "version", "agent_key", "seals", "entries", "scopes")}
            mutated["state_digest"] = _digest(payload)
            row["attested_state_digest"] = snapshot["state_digest"]
            PeerHistoryV1.replay(mutated)
            row.update({"status": "FAIL", "selection": None,
                        "unknown_reason": "mutated projection unexpectedly replayed"})
        else:
            base = _select(history, target_scope_key=target_scope_key)
            mutated = deepcopy(history.selector_projection(candidate_key="peer-a@v1"))
            unrelated = [scope for scope in mutated["scopes"]
                         if scope["scope_key"] != target_scope_key]
            if not unrelated:
                raise ValueError("scope-isolation fixture has no unrelated scope")
            unrelated[0]["smoothed_rate"] = 1.0
            projections = {
                "peer-a@v1": mutated,
                "peer-b@v1": PeerHistoryV1.empty("peer-b").selector_projection(
                    candidate_key="peer-b@v1"
                ),
            }
            changed = select_from_public_history(
                candidate_keys=CANDIDATES, projections=projections,
                base_scores=(0.0, 0.0), read_cut=READ_CUT, rng_seed=RNG_SEED,
                target_scope_key=target_scope_key,
            )
            decision_fields = ("scores", "probabilities", "chosen_peer", "propensity")
            isolated = all(changed[field] == base[field] for field in decision_fields)
            row.update({"status": "PASS" if isolated else "FAIL",
                        "selection": changed, "baseline_selection": base,
                        "decision_fields_equal": isolated,
                        "projection_digest": changed["projection_digests"]["peer-a@v1"]})
        row.setdefault("selection", None)
    except Exception as exc:
        row.update({"status": "UNKNOWN", "selection": None,
                    "unknown_reason": f"{type(exc).__name__}: {exc}"})
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 6)
    row["wall_ms"] = elapsed_ms
    row["cost"] = {"api_calls": 0, "gpu_jobs": 0, "input_tokens": 0,
                   "output_tokens": 0, "tool_calls": 0,
                   "replay_entries": len(history.entries), "wall_ms": elapsed_ms,
                   "updates": 0}
    return row


def run(out: Path) -> dict[str, Any]:
    out = out.resolve()
    out.mkdir(parents=False, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     text=True).strip()
    components = {
        name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest()
        for name in ("peerrolebench_peer_history.py", "peerrolebench_history_selector.py",
                     "peerrolebench_history_adversarial_qualification.py")
    }
    worktree_status = subprocess.check_output(
        ["git", "status", "--short", "--untracked-files=no"], cwd=ROOT, text=True
    )
    config = {"qualification_version": VERSION, "git_commit": commit,
              "python": sys.version, "platform": platform.platform(),
              "cells": list(CELLS), "candidate_keys": list(CANDIDATES),
              "read_cut": READ_CUT, "rng_seed": RNG_SEED,
              "fixture": "two-entry-history-with-cross-scope-v1",
              "component_sha256": components,
              "git_worktree_status_before": worktree_status,
              "llm_calls": 0, "gpu_jobs": 0,
              "scientific_claim_allowed": False,
              "started_at_utc": datetime.now(timezone.utc).isoformat()}
    _json(out / "config.json", config)
    history = _two_entry_history()
    scopes = history.selector_projection(candidate_key="peer-a@v1")["scopes"]
    target_scope_key = scopes[0]["scope_key"]
    results: dict[str, Any] = {}
    for cell in CELLS:
        cell_out = out / cell
        cell_out.mkdir(parents=False, exist_ok=False)
        row = _run_cell(cell, history, target_scope_key)
        _json(cell_out / "summary.json", row)
        (cell_out / "raw.jsonl").write_text(
            json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "event_type": "history_adversarial_cell", "payload": row},
                       ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        results[cell] = row
    passed = bool(
        results["valid-two-entry"]["status"] == "PASS"
        and all(results[cell]["status"] == "UNKNOWN"
                for cell in ("permuted-two-entry", "candidate-mismatch",
                             "projection-rate-mutation"))
        and results["scope-isolation"]["status"] == "PASS"
        and all(row["update_count"] == 0 for row in results.values())
    )
    summary = {**config, "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
               "passed": passed, "cells": results,
               "checks": {
                   "valid_two_entry": results["valid-two-entry"]["status"] == "PASS",
                   "permutation_rejected": results["permuted-two-entry"]["status"] == "UNKNOWN",
                   "candidate_mismatch_rejected": results["candidate-mismatch"]["status"] == "UNKNOWN",
                   "projection_mutation_rejected": results["projection-rate-mutation"]["status"] == "UNKNOWN",
                   "scope_isolated": results["scope-isolation"]["status"] == "PASS",
                   "all_updates_zero": all(row["update_count"] == 0 for row in results.values()),
               },
               "real_api_calls": 0, "gpu_jobs": 0,
               "scientific_claim_allowed": False,
               "interpretation": "Multi-entry order, identity, projection integrity and scope isolation only.",
               "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    _json(out / "summary.json", summary)
    (out / "raw.jsonl").write_text(
        json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "event_type": "history_adversarial_summary", "payload": summary},
                   ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
