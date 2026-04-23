"""R41g robustness test: resume-time orphan-sibling-row cleanup.

Simulates the crash-mid-write scenario:
  1. Create a run_dir with sibling jsonls populated for N+1 samples.
  2. Create `_ckpt_preds.jsonl` containing only the first N task_ids
     (simulating a crash AFTER writing sibling for N+1 but BEFORE writing
     the corresponding ckpt line).
  3. Invoke RoundRunner._cleanup_orphan_sibling_rows.
  4. Verify every sibling jsonl now contains ONLY lines for the N
     committed task_ids (no orphans).

Does NOT need LLM config / runtime setup; pure I/O-level test.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from workspace.idea04_core.runner import RoundRunner


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_task_ids(path: Path) -> list[str]:
    """Return the task_id of each line in order (for ordering sanity)."""
    if not path.is_file():
        return []
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line)["task_id"])
    return out


class TestR41G_CleanupOrphanSiblingRows:
    """RoundRunner._cleanup_orphan_sibling_rows removes orphan sibling rows."""

    def test_cleanup_drops_single_orphan_across_all_stage1_sibling_files(
        self, tmp_path
    ):
        """3 committed samples (q0, q1, q2) + 1 orphan (q3) across each of
        the 4 Stage-1 sibling jsonls. Cleanup keeps only q0-q2.
        """
        run_dir = tmp_path / "run"
        committed = ["q0", "q1", "q2"]
        all_ids = committed + ["q3"]   # q3 = pre-crash orphan

        # Write ckpt with ONLY committed samples
        _write_jsonl(
            run_dir / "_ckpt_preds.jsonl",
            [{"task_id": t, "answer_f1": 0.5} for t in committed],
        )

        # Write each Stage-1 sibling with ALL 4 samples (including orphan)
        sibling_files = RoundRunner._SIBLING_FILES_STAGE1
        for fname in sibling_files:
            _write_jsonl(
                run_dir / fname,
                [{"task_id": t, "kind": fname[:-6]} for t in all_ids],
            )

        # Sanity: pre-cleanup each sibling has 4 rows
        for fname in sibling_files:
            assert len(_read_task_ids(run_dir / fname)) == 4

        # Cleanup
        RoundRunner._cleanup_orphan_sibling_rows(
            run_dir=run_dir, completed_ids=set(committed), is_stage2=False
        )

        # Post-cleanup: each sibling has only committed task_ids
        for fname in sibling_files:
            ids = _read_task_ids(run_dir / fname)
            assert ids == committed, (
                f"{fname}: expected {committed}, got {ids}"
            )

        # Stage-2 files should NOT have been created (is_stage2=False)
        for fname in RoundRunner._SIBLING_FILES_STAGE2_EXTRA:
            assert not (run_dir / fname).exists()

    def test_cleanup_also_processes_stage2_extra_sibling_files(self, tmp_path):
        """Same pattern but is_stage2=True must also clean the 3 extra
        Stage-2 jsonls (task_tree, audit_events, neighbor_belief_snapshots)."""
        run_dir = tmp_path / "run"
        committed = ["q0", "q1"]
        all_ids = committed + ["q2"]

        _write_jsonl(
            run_dir / "_ckpt_preds.jsonl",
            [{"task_id": t, "answer_f1": 0.7} for t in committed],
        )

        all_files = (
            RoundRunner._SIBLING_FILES_STAGE1
            + RoundRunner._SIBLING_FILES_STAGE2_EXTRA
        )
        for fname in all_files:
            _write_jsonl(
                run_dir / fname,
                [{"task_id": t, "kind": fname[:-6]} for t in all_ids],
            )

        RoundRunner._cleanup_orphan_sibling_rows(
            run_dir=run_dir, completed_ids=set(committed), is_stage2=True
        )

        for fname in all_files:
            ids = _read_task_ids(run_dir / fname)
            assert ids == committed, f"{fname}: expected {committed}, got {ids}"

    def test_cleanup_is_noop_when_no_orphans(self, tmp_path):
        """If sibling rows are already consistent with ckpt, cleanup is a
        no-op (file mtime may change harmlessly due to rewrite)."""
        run_dir = tmp_path / "run"
        committed = ["q0", "q1", "q2"]
        _write_jsonl(
            run_dir / "_ckpt_preds.jsonl",
            [{"task_id": t, "answer_f1": 0.5} for t in committed],
        )
        for fname in RoundRunner._SIBLING_FILES_STAGE1:
            _write_jsonl(
                run_dir / fname,
                [{"task_id": t, "k": "v"} for t in committed],
            )

        RoundRunner._cleanup_orphan_sibling_rows(
            run_dir=run_dir, completed_ids=set(committed), is_stage2=False
        )

        for fname in RoundRunner._SIBLING_FILES_STAGE1:
            ids = _read_task_ids(run_dir / fname)
            assert ids == committed

    def test_cleanup_tolerates_malformed_lines(self, tmp_path):
        """If a sibling jsonl has a malformed line (non-JSON), cleanup drops
        it along with orphans, without crashing the runner."""
        run_dir = tmp_path / "run"
        committed = ["q0"]
        _write_jsonl(
            run_dir / "_ckpt_preds.jsonl",
            [{"task_id": "q0", "answer_f1": 0.8}],
        )
        fpath = run_dir / "routing_traces.jsonl"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(
            '{"task_id": "q0", "k": "v"}\n'
            'NOT JSON AT ALL\n'
            '{"task_id": "q9_orphan", "k": "v"}\n',
            encoding="utf-8",
        )

        RoundRunner._cleanup_orphan_sibling_rows(
            run_dir=run_dir, completed_ids=set(committed), is_stage2=False
        )

        ids = _read_task_ids(fpath)
        assert ids == ["q0"], f"expected only q0, got {ids}"

    def test_cleanup_preserves_order_of_kept_rows(self, tmp_path):
        """When orphans are interleaved, cleanup preserves the order of the
        surviving rows (important for validate_logs.py which reads line-by-
        line and may assume monotonic sample order).
        """
        run_dir = tmp_path / "run"
        committed = ["qA", "qB", "qC"]
        # Write sibling with interleaved orphans: [qA, q_orphan1, qB, q_orphan2, qC]
        fpath = run_dir / "routing_traces.jsonl"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with fpath.open("w", encoding="utf-8") as fh:
            for tid in ["qA", "q_orphan1", "qB", "q_orphan2", "qC"]:
                fh.write(json.dumps({"task_id": tid, "k": "v"}) + "\n")

        _write_jsonl(
            run_dir / "_ckpt_preds.jsonl",
            [{"task_id": t, "answer_f1": 0.5} for t in committed],
        )

        RoundRunner._cleanup_orphan_sibling_rows(
            run_dir=run_dir, completed_ids=set(committed), is_stage2=False
        )

        ids = _read_task_ids(fpath)
        assert ids == committed, f"order preservation failed: {ids}"

    def test_r42_fu3_missing_sibling_emits_warning(self, tmp_path, capsys):
        """R42 FU-3: if a committed task_id has NO corresponding row in a
        sibling jsonl, emit a WARNING (but do not fail the cleanup).

        Scenario: ckpt has q0, q1, q2 committed; sibling routing_traces.jsonl
        has rows only for q0, q1 (q2 is MISSING). No orphans. Cleanup should
        log a `WARNING` mentioning q2 + 1 missing sample. All other sibling
        files are healthy (3/3 rows).
        """
        run_dir = tmp_path / "run"
        committed = ["q0", "q1", "q2"]
        _write_jsonl(
            run_dir / "_ckpt_preds.jsonl",
            [{"task_id": t, "answer_f1": 0.5} for t in committed],
        )
        # All siblings EXCEPT routing_traces have 3 rows
        for fname in RoundRunner._SIBLING_FILES_STAGE1:
            if fname == "routing_traces.jsonl":
                _write_jsonl(run_dir / fname, [
                    {"task_id": t, "k": "v"} for t in ("q0", "q1")
                ])
            else:
                _write_jsonl(run_dir / fname, [
                    {"task_id": t, "k": "v"} for t in committed
                ])

        RoundRunner._cleanup_orphan_sibling_rows(
            run_dir=run_dir,
            completed_ids=set(committed),
            is_stage2=False,
        )

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "routing_traces.jsonl" in captured.out
        assert "1/3 committed samples have no sibling rows" in captured.out
        assert "q2" in captured.out
        # No orphan rewrite should have occurred
        assert not (
            run_dir / "routing_traces.jsonl.r41g_tmp"
        ).exists()
        # routing_traces still has only 2 rows (NOT rewritten, just WARNING)
        assert _read_task_ids(run_dir / "routing_traces.jsonl") == ["q0", "q1"]

    def test_cleanup_handles_missing_sibling_file_gracefully(self, tmp_path):
        """If a sibling jsonl simply doesn't exist (e.g., Stage-1 run with
        is_stage2=False), cleanup skips it without error."""
        run_dir = tmp_path / "run"
        _write_jsonl(
            run_dir / "_ckpt_preds.jsonl",
            [{"task_id": "q0", "answer_f1": 0.5}],
        )
        # No sibling files created. Should be a quiet no-op.
        RoundRunner._cleanup_orphan_sibling_rows(
            run_dir=run_dir, completed_ids={"q0"}, is_stage2=True
        )
        # Assert no exception + no new files created
        assert not (run_dir / "routing_traces.jsonl").exists()
