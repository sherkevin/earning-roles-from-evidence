"""R42 E-3 regression test: validate_logs check #9.5 row-count symmetry.

Creates synthetic run directories that simulate:
  1. Healthy 1:1 ckpt↔sibling alignment → PASS (no errors)
  2. Sibling orphan (extra traces row for unrecorded task_id) → ROW_COUNT_MISMATCH_TRACES
  3. Missing sibling (ckpt committed but traces row lost) → ROW_COUNT_MISMATCH_TRACES
  4. Stage-1 post_sample snap (snaps = hop_count + 1) → PASS (acceptable per invariant)
  5. Stage-1 snap = hop_count + 2 → ROW_COUNT_MISMATCH_SNAPS (too many post rows)

Per ``[r42_engineer_takeover_pipeline_20260421]`` E-3, check #9.5 verifies:
  traces / packets / raw_outs rows_by_task_id == hop_count (strict)
  snaps rows_by_task_id in {hop_count, hop_count+1} (soft)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[2]
_VALIDATE_LOGS = _REPO_ROOT / "scripts" / "validate_logs.py"


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _make_healthy_run_dir(run_dir: Path, n_samples: int = 3) -> None:
    """Emit a minimal but fully valid run_dir that all check #1-#11 pass.

    Each sample has hop_count=2, so:
      - routing_traces.jsonl: 2 rows per sample
      - handoff_packets.jsonl: 2 rows per sample
      - raw_model_outputs.jsonl: 2 rows per sample
      - competence_snapshots.jsonl: 2 rows per sample (no post_sample)
      - parsed_predictions.jsonl: 1 row per sample with hop_count=2
    """
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. run_config.yaml
    (run_dir / "run_config.yaml").write_text(
        "topology: chain\nmax_handoff: 4\nn_workers: 1\n", encoding="utf-8"
    )

    sample_ids = [f"q{i}" for i in range(n_samples)]
    (run_dir / "sample_ids.json").write_text(
        json.dumps(sample_ids, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    traces: list[dict] = []
    packets: list[dict] = []
    raw_outs: list[dict] = []
    snaps: list[dict] = []
    preds: list[dict] = []
    raw_inputs: list[dict] = []
    for sid in sample_ids:
        raw_inputs.append({"task_id": sid, "question": f"q_{sid}", "answer": "a"})
        for hop in (0, 1):
            traces.append({"task_id": sid, "hop_index": hop, "chosen_target": "verifier" if hop == 0 else ""})
            packets.append({"task_id": sid, "hop_index": hop, "current_subgoal": "x"})
            raw_outs.append({"task_id": sid, "hop_index": hop, "node_name": "n", "raw_response": "r"})
            snaps.append({
                "task_id": sid,
                "hop_index": hop,
                "node_name": "n",
                "update": {"before": {"n": 0.5}, "after": {"n": 0.5}, "signal": "x"},
                "competence_after": {"n": 0.5},
            })
        preds.append({
            "task_id": sid,
            "question": f"q_{sid}",
            "gold_answer": "a",
            "final_answer": "a",
            "accepted_node": "synthesizer",
            "hop_count": 2,
            "answer_em": 1.0,
            "answer_f1": 1.0,
            "termination_reason": "accepted",
            "token_cost": 300,
        })

    _write_jsonl(run_dir / "raw_inputs.jsonl", raw_inputs)
    _write_jsonl(run_dir / "routing_traces.jsonl", traces)
    _write_jsonl(run_dir / "handoff_packets.jsonl", packets)
    _write_jsonl(run_dir / "raw_model_outputs.jsonl", raw_outs)
    _write_jsonl(run_dir / "competence_snapshots.jsonl", snaps)
    _write_jsonl(run_dir / "parsed_predictions.jsonl", preds)

    (run_dir / "metrics.json").write_text(
        json.dumps({"answer_em": 1.0, "answer_f1": 1.0, "sample_count": n_samples}),
        encoding="utf-8",
    )
    (run_dir / "main_table.csv").write_text(
        "answer_em,answer_f1,sample_count\n1.0,1.0,3\n", encoding="utf-8"
    )
    (run_dir / "failure_cases.md").write_text("# failure_cases\n", encoding="utf-8")
    (run_dir / "case_studies.md").write_text("# case_studies\n", encoding="utf-8")
    (run_dir / "run_notes.md").write_text("# run_notes\n", encoding="utf-8")


def _run_validate_logs(run_dir: Path) -> tuple[int, str]:
    """Invoke scripts/validate_logs.py as a subprocess; return (rc, stdout+stderr)."""
    result = subprocess.run(
        [sys.executable, str(_VALIDATE_LOGS), str(run_dir)],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


class TestR42_ValidateLogsRowCountSymmetry:
    """validate_logs.py check #9.5: per-sample row-count symmetry."""

    def test_healthy_run_dir_passes(self, tmp_path):
        """Baseline: a fully-valid run_dir triggers no errors."""
        run_dir = tmp_path / "run"
        _make_healthy_run_dir(run_dir, n_samples=3)

        rc, out = _run_validate_logs(run_dir)
        assert rc == 0, f"expected rc=0 on healthy run_dir; got rc={rc}\n{out}"
        assert "[OK]" in out, f"expected [OK] marker; got:\n{out}"
        assert "ROW_COUNT_MISMATCH" not in out, (
            f"healthy data should not trigger symmetry error; got:\n{out}"
        )

    def test_orphan_trace_row_triggers_mismatch(self, tmp_path):
        """Adding an orphan traces row for a task_id not in predictions
        triggers ROW_COUNT_MISMATCH_TRACES.
        """
        run_dir = tmp_path / "run"
        _make_healthy_run_dir(run_dir, n_samples=3)

        # Append 1 extra traces row for q0 (now q0 has 3 traces vs hop_count=2)
        with (run_dir / "routing_traces.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "task_id": "q0", "hop_index": 2, "chosen_target": "",
            }) + "\n")

        rc, out = _run_validate_logs(run_dir)
        assert rc != 0, "expected non-zero rc on orphan; got rc=0"
        # Check which specific mismatch label fires — could be TRACES (orphan
        # extra row) or ROUTING_CHAIN_GAP (since hop 2 may not be contiguous).
        # Our orphan is hop_index=2 appended after (hop 0, hop 1), so chain
        # IS contiguous. The failure is strictly row-count.
        assert "ROW_COUNT_MISMATCH_TRACES" in out, (
            f"expected ROW_COUNT_MISMATCH_TRACES; got:\n{out}"
        )

    def test_missing_packet_row_triggers_mismatch(self, tmp_path):
        """Removing a packet row (ckpt committed with hop_count=2 but only
        1 packet row on disk) triggers ROW_COUNT_MISMATCH_PACKETS.
        """
        run_dir = tmp_path / "run"
        _make_healthy_run_dir(run_dir, n_samples=3)

        # Rewrite packets keeping only 1 row per sample
        packets_path = run_dir / "handoff_packets.jsonl"
        original = [
            json.loads(line)
            for line in packets_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        kept_first_per_sample: dict[str, dict] = {}
        for row in original:
            kept_first_per_sample.setdefault(row["task_id"], row)
        _write_jsonl(packets_path, list(kept_first_per_sample.values()))

        rc, out = _run_validate_logs(run_dir)
        assert rc != 0, "expected non-zero rc on missing packet rows; got rc=0"
        assert "ROW_COUNT_MISMATCH_PACKETS" in out, (
            f"expected ROW_COUNT_MISMATCH_PACKETS; got:\n{out}"
        )

    def test_snaps_plus_one_post_sample_is_accepted(self, tmp_path):
        """Adding 1 post_sample snap per sample (stage-1 fixed_peer_calibrated
        behaviour) means snaps == hop_count+1; check #9.5 should allow this
        via the softer {hop_count, hop_count+1} invariant.
        """
        run_dir = tmp_path / "run"
        _make_healthy_run_dir(run_dir, n_samples=3)

        snaps_path = run_dir / "competence_snapshots.jsonl"
        with snaps_path.open("a", encoding="utf-8") as fh:
            for sid in ("q0", "q1", "q2"):
                fh.write(json.dumps({
                    "task_id": sid,
                    "hop_index": "post_sample",
                    "node_name": "synthesizer",
                    "update": {"before": {"n": 0.5}, "after": {"n": 0.6}, "signal": "post"},
                    "competence_after": {"n": 0.6},
                }) + "\n")

        rc, out = _run_validate_logs(run_dir)
        assert rc == 0, (
            f"snaps == hop_count+1 should pass; got rc={rc}\n{out}"
        )
        assert "ROW_COUNT_MISMATCH_SNAPS" not in out, (
            f"snaps=hop+1 should not trigger error; got:\n{out}"
        )

    def test_snaps_plus_two_triggers_mismatch(self, tmp_path):
        """Adding 2 post-rows per sample (snaps == hop_count+2) exceeds the
        {hop_count, hop_count+1} invariant and triggers mismatch.
        """
        run_dir = tmp_path / "run"
        _make_healthy_run_dir(run_dir, n_samples=3)

        snaps_path = run_dir / "competence_snapshots.jsonl"
        with snaps_path.open("a", encoding="utf-8") as fh:
            for sid in ("q0", "q1", "q2"):
                for label in ("post_1", "post_2"):
                    fh.write(json.dumps({
                        "task_id": sid,
                        "hop_index": label,
                        "node_name": "synthesizer",
                        "update": {"before": {"n": 0.5}, "after": {"n": 0.6}, "signal": "post"},
                        "competence_after": {"n": 0.6},
                    }) + "\n")

        rc, out = _run_validate_logs(run_dir)
        assert rc != 0, "snaps=hop+2 should trigger rc!=0"
        assert "ROW_COUNT_MISMATCH_SNAPS" in out, (
            f"expected ROW_COUNT_MISMATCH_SNAPS; got:\n{out}"
        )
