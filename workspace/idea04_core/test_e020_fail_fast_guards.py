"""E-020 unit tests: fail-fast guards against quota exhaustion + silent corruption.

Per ``four-role-todo-workflow.mdc §6.1.4`` (E-020 ticket spec), these tests
cover three runtime guards added after the
``quota_exhaustion_incident_20260419_2338`` post-mortem:

  1. ``llm_client.call_llm`` raises ``QuotaExhaustedError`` on HTTP 403
     ``insufficient_user_quota`` + HTTP 401 ``Invalid token``, instead of
     retrying and returning an empty prediction.
  2. ``RoundRunner.run`` halts the batch and writes ``_ckpt_meta.json`` when
     ``N`` consecutive samples yield F1 == 0.0 (``N`` configurable, default 50).
  3. ``scripts/run_e017_fullval_seed.py`` refuses to launch the runner when
     the pre-flight quota probe does not return ``newapi ACTIVE``.

All tests mock the LLM / subprocess calls so the suite makes zero network
calls. Run from repo root::

    python -m pytest workspace/idea04_core/test_e020_fail_fast_guards.py -v
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "workspace"))

from workspace.idea04_core import llm_client  # noqa: E402
from workspace.idea04_core.llm_client import (  # noqa: E402
    ModelDriftError,
    QuotaExhaustedError,
    call_llm,
    configure_runtime,
)
from workspace.idea04_core.runner import (  # noqa: E402
    ConsecutiveZeroF1Halt,
    RoundRunner,
)


# =============================================================================
# E-020.1 — call_llm raises QuotaExhaustedError on 403 insufficient_user_quota
# =============================================================================


def _make_http_error(status: int, body_text: str) -> urllib.error.HTTPError:
    """Build a minimal HTTPError whose ``.read()`` returns ``body_text``."""
    return urllib.error.HTTPError(
        url="https://xh.v1api.cc/v1/chat/completions",
        code=status,
        msg="mocked",
        hdrs=None,  # type: ignore[arg-type]
        fp=io.BytesIO(body_text.encode("utf-8")),
    )


@pytest.fixture
def _reset_llm_runtime():
    """Reset llm_client module-level state between tests so configure_runtime
    does not error on repeated calls."""
    saved_runtime = dict(llm_client._runtime)
    saved_contract = llm_client._contract_model
    try:
        yield
    finally:
        llm_client._runtime.clear()
        llm_client._runtime.update(saved_runtime)
        llm_client._contract_model = saved_contract


class TestE020_1_QuotaExhaustedError:
    """llm_client raises QuotaExhaustedError instead of retry-empty-return."""

    def test_403_insufficient_user_quota_raises_immediately(
        self, _reset_llm_runtime, monkeypatch
    ):
        """HTTP 403 + ``insufficient_user_quota`` body triggers
        ``QuotaExhaustedError`` on the FIRST attempt (no retry delay)."""
        # Minimal runtime wiring (no real HTTP call will be made).
        llm_client._runtime.update({
            "chat_url": "https://example/v1/chat",
            "api_key": "sk-test",
            "model": "gpt-4.1-mini",
            "backend": "newapi",
            "before_request": None,
            "enforce_model": False,
        })
        llm_client._contract_model = ""

        body = (
            '{"error":{"message":"\\u7528\\u6237\\u989d\\u5ea6\\u4e0d\\u8db3"'
            ',"type":"new_api_error","code":"insufficient_user_quota"}}'
        )
        call_count = {"n": 0}

        def _fake_opener_open(req, timeout=60):  # noqa: ARG001
            call_count["n"] += 1
            raise _make_http_error(403, body)

        def _fake_urlopen(req, timeout=60):  # noqa: ARG001
            call_count["n"] += 1
            raise _make_http_error(403, body)

        mock_opener = MagicMock()
        mock_opener.open.side_effect = _fake_opener_open
        monkeypatch.setattr(
            "urllib.request.build_opener", lambda *a, **kw: mock_opener
        )
        monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

        # Should raise immediately WITHOUT 3 retries.
        with pytest.raises(QuotaExhaustedError) as excinfo:
            call_llm([{"role": "user", "content": "x"}], max_tokens=1, retries=3)

        assert "insufficient_user_quota" in str(excinfo.value)
        assert "newapi_quota_probe" in str(excinfo.value)
        # Exactly ONE attempt — no retries for quota errors.
        assert call_count["n"] == 1, (
            f"Quota exhaustion should NOT retry; got {call_count['n']} calls"
        )

    def test_401_invalid_token_raises_immediately(
        self, _reset_llm_runtime, monkeypatch
    ):
        """HTTP 401 + ``Invalid token`` body raises QuotaExhaustedError."""
        llm_client._runtime.update({
            "chat_url": "https://example/v1/chat",
            "api_key": "sk-test",
            "model": "gpt-4.1-mini",
            "backend": "newapi",
            "before_request": None,
            "enforce_model": False,
        })
        llm_client._contract_model = ""

        body = '{"error":{"message":"Invalid token","code":"invalid_api_key"}}'

        def _raise_401(req, timeout=60):  # noqa: ARG001
            raise _make_http_error(401, body)

        monkeypatch.setattr("urllib.request.urlopen", _raise_401)
        mock_opener = MagicMock()
        mock_opener.open.side_effect = _raise_401
        monkeypatch.setattr(
            "urllib.request.build_opener", lambda *a, **kw: mock_opener
        )

        with pytest.raises(QuotaExhaustedError) as excinfo:
            call_llm([{"role": "user", "content": "x"}], max_tokens=1, retries=3)
        assert "Invalid token" in str(excinfo.value)

    def test_quota_exhausted_not_swallowed_by_except_exception(
        self, _reset_llm_runtime, monkeypatch
    ):
        """QuotaExhaustedError inherits BaseException so broad ``except
        Exception`` handlers cannot swallow it (prevents the original
        2026-04-19 silent-corruption failure mode)."""
        assert not issubclass(QuotaExhaustedError, Exception), (
            "QuotaExhaustedError must inherit from BaseException, not "
            "Exception, to prevent method code from swallowing it."
        )
        # Sanity: ModelDriftError has the same property (regression guard).
        assert not issubclass(ModelDriftError, Exception)

    def test_500_server_error_still_retries_as_before(
        self, _reset_llm_runtime, monkeypatch
    ):
        """Non-quota HTTP errors (500, etc.) preserve the legacy retry-3
        behavior — this is a regression guard to confirm E-020 did not
        break the generic retry path."""
        llm_client._runtime.update({
            "chat_url": "https://example/v1/chat",
            "api_key": "sk-test",
            "model": "gpt-4.1-mini",
            "backend": "newapi",
            "before_request": None,
            "enforce_model": False,
        })
        llm_client._contract_model = ""

        call_count = {"n": 0}

        def _raise_500(req, timeout=60):  # noqa: ARG001
            call_count["n"] += 1
            raise _make_http_error(500, '{"error":"transient"}')

        monkeypatch.setattr("urllib.request.urlopen", _raise_500)
        mock_opener = MagicMock()
        mock_opener.open.side_effect = _raise_500
        monkeypatch.setattr(
            "urllib.request.build_opener", lambda *a, **kw: mock_opener
        )
        # Speed up the test: no actual sleep.
        monkeypatch.setattr("time.sleep", lambda s: None)

        with pytest.raises(RuntimeError):
            call_llm([{"role": "user", "content": "x"}], max_tokens=1, retries=3)
        # Legacy behavior: 3 retries, then RuntimeError.
        assert call_count["n"] == 3, (
            f"Non-quota 500 should retry 3x; got {call_count['n']}"
        )


# =============================================================================
# E-020.2 — RoundRunner halts on N consecutive F1=0 samples
# =============================================================================


class TestE020_2_ConsecutiveZeroF1Halt:
    """RoundRunner.run raises ConsecutiveZeroF1Halt + writes _ckpt_meta.json."""

    def test_halt_at_threshold_3(self, tmp_path, monkeypatch, _reset_llm_runtime):
        """With threshold=3, runner halts after exactly 3 consecutive F1=0.

        Uses a low threshold (3) to make the test fast and deterministic.
        The halt path is identical for production default (50).
        """
        # Stub configure_runtime so it does not require real LLM config.
        monkeypatch.setattr(
            llm_client, "configure_runtime", lambda *a, **kw: None
        )
        from workspace.idea04_core import runner as runner_mod
        from workspace.idea04_core.contracts import (
            AgentOutput,
            TraceEntry,
            CompetenceUpdate,
            HandoffPacket,
        )

        def _stub_step(
            agent_name,
            agent_input,
            hop_index,
            gold_answer,
            answer_f1_feedback,
        ):  # noqa: ARG001
            comp_before = agent_input.local_state.get("self_claim", 0.5)
            return AgentOutput(
                decision="accept",
                generated_answer="___wrong___",  # guaranteed F1=0 vs real gold
                raw_response="mock",
                usage_calls=[{"prompt_tokens": 1, "completion_tokens": 1,
                              "total_tokens": 2}],
                trace=TraceEntry(
                    task_id=agent_input.task_id,
                    hop_index=hop_index,
                    node_name=agent_name,
                    chosen_target="",
                    decision="accept",
                    reason="test_stub_always_accept",
                ),
                outgoing_packet=HandoffPacket(
                    task_id=agent_input.task_id,
                    question=agent_input.question,
                    current_subgoal="",
                    evidence_so_far=[],
                    uncertainty=0.0,
                    reason_for_forward="",
                    recommended_next_skill="",
                    visited_nodes=[],
                    hop_count=hop_index,
                    last_actor=agent_name,
                    candidate_answer="___wrong___",
                    published_competence={},
                ),
                competence_update=CompetenceUpdate(
                    before={agent_name: comp_before},
                    after={agent_name: comp_before},
                    signal="test_stub",
                ),
            )

        monkeypatch.setattr(runner_mod, "run_method_step", _stub_step)

        run_dir = tmp_path / "run"
        samples = [
            {"task_id": f"q{i}", "question": "Q?", "answer": "real_gold"}
            for i in range(10)
        ]
        run_config = {
            "main_model": "gpt-4.1-mini",
            "n_workers": 1,
            "progress_every": 0,
            "max_handoff": 2,
            "consecutive_zero_halt_threshold": 3,
        }

        runner = RoundRunner(topology="chain", max_handoff=2)
        with pytest.raises(ConsecutiveZeroF1Halt) as excinfo:
            runner.run("single_agent", samples, run_config, run_dir)

        assert "consecutive F1=0 for 3 samples" in str(excinfo.value)
        # Meta breadcrumb must exist for scheduler hand-off.
        meta_path = run_dir / "_ckpt_meta.json"
        assert meta_path.is_file(), "_ckpt_meta.json must be written on halt"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        assert meta["status"] == "halted"
        assert meta["reason"] == "consecutive_zero_f1_threshold"
        assert meta["threshold"] == 3
        assert meta["counter"] == 3
        assert meta["last_sample_id"] == "q2", (
            "Halt should fire on the 3rd consecutive F1=0 (task id q2)"
        )
        # Checkpoint should contain exactly 3 valid predictions — the ones
        # that triggered the halt. Fresh resume will append from #3 onwards.
        ckpt_path = run_dir / "_ckpt_preds.jsonl"
        assert ckpt_path.is_file()
        ckpt_lines = [
            ln for ln in ckpt_path.read_text(encoding="utf-8").splitlines() if ln
        ]
        assert len(ckpt_lines) == 3, (
            f"Expected 3 ckpt lines before halt, got {len(ckpt_lines)}"
        )

    def test_halt_disabled_when_threshold_zero(
        self, tmp_path, monkeypatch, _reset_llm_runtime
    ):
        """Setting ``consecutive_zero_halt_threshold=0`` disables the guard
        (used by unit tests that deliberately produce all F1=0 samples)."""
        monkeypatch.setattr(
            llm_client, "configure_runtime", lambda *a, **kw: None
        )
        from workspace.idea04_core import runner as runner_mod
        from workspace.idea04_core.contracts import (
            AgentOutput,
            TraceEntry,
            CompetenceUpdate,
            HandoffPacket,
        )

        def _stub_step(agent_name, agent_input, hop_index, gold_answer,
                       answer_f1_feedback):  # noqa: ARG001
            return AgentOutput(
                decision="accept",
                generated_answer="___wrong___",
                raw_response="mock",
                usage_calls=[],
                trace=TraceEntry(
                    task_id=agent_input.task_id,
                    hop_index=hop_index,
                    node_name=agent_name,
                    chosen_target="",
                    decision="accept",
                    reason="",
                ),
                outgoing_packet=HandoffPacket(
                    task_id=agent_input.task_id,
                    question=agent_input.question,
                    current_subgoal="",
                    evidence_so_far=[],
                    uncertainty=0.0,
                    reason_for_forward="",
                    recommended_next_skill="",
                    visited_nodes=[],
                    hop_count=hop_index,
                    last_actor=agent_name,
                    candidate_answer="___wrong___",
                    published_competence={},
                ),
                competence_update=CompetenceUpdate(
                    before={agent_name: 0.5},
                    after={agent_name: 0.5},
                    signal="",
                ),
            )
        monkeypatch.setattr(runner_mod, "run_method_step", _stub_step)

        run_dir = tmp_path / "run"
        samples = [
            {"task_id": f"q{i}", "question": "Q?", "answer": "real_gold"}
            for i in range(5)
        ]
        run_config = {
            "main_model": "gpt-4.1-mini",
            "n_workers": 1,
            "progress_every": 0,
            "max_handoff": 2,
            "consecutive_zero_halt_threshold": 0,
        }
        runner = RoundRunner(topology="chain", max_handoff=2)
        metrics = runner.run("single_agent", samples, run_config, run_dir)
        assert metrics["sample_count"] == 5
        assert metrics["answer_f1"] == 0.0
        # No halt artifact must exist.
        assert not (run_dir / "_ckpt_meta.json").is_file()

    def test_halt_not_swallowed_by_except_exception(self):
        """ConsecutiveZeroF1Halt inherits BaseException (like QuotaExhausted
        and ModelDrift) so it propagates past method-code exception handlers.
        """
        assert not issubclass(ConsecutiveZeroF1Halt, Exception), (
            "ConsecutiveZeroF1Halt must inherit from BaseException, not "
            "Exception, to prevent being swallowed."
        )


# =============================================================================
# E-020.3 — run_e017_fullval_seed.py pre-flight quota probe
# =============================================================================


class TestE020_3_PreflightQuotaProbe:
    """Pre-flight probe blocks launch when newapi quota is not ACTIVE."""

    def test_preflight_blocks_launch_on_depleted(self, monkeypatch):
        """Simulated probe returning ``STATUS: QUOTA STILL DEPLETED`` must
        cause ``_run_quota_preflight`` to ``sys.exit(2)``.
        """
        import importlib
        e017 = importlib.import_module("scripts.run_e017_fullval_seed")

        def _fake_run(cmd, capture_output, text, timeout):  # noqa: ARG001
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=(
                    "key len: 48, prefix: sk-bSS5YkaXd...\n\n"
                    "=== probe newapi POST /v1/chat/completions ===\n"
                    "STATUS: QUOTA STILL DEPLETED — need U-EXEC-007 recharge\n"
                ),
                stderr="",
            )

        monkeypatch.setattr(subprocess, "run", _fake_run)
        monkeypatch.setattr(e017.Path, "is_file", lambda self: True)

        with pytest.raises(SystemExit) as excinfo:
            e017._run_quota_preflight()
        assert excinfo.value.code == 2

    def test_preflight_allows_launch_on_active(self, monkeypatch, capsys):
        """Simulated probe returning ``STATUS: newapi ACTIVE`` must return
        without exit."""
        import importlib
        e017 = importlib.import_module("scripts.run_e017_fullval_seed")

        def _fake_run(cmd, capture_output, text, timeout):  # noqa: ARG001
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=(
                    "key len: 48, prefix: sk-bSS5YkaXd...\n\n"
                    "=== probe ===\n"
                    'response (first 500 char): {"content":"Hello"}\n\n'
                    "STATUS: newapi ACTIVE (quota OK, ready to resume)\n"
                ),
                stderr="",
            )

        monkeypatch.setattr(subprocess, "run", _fake_run)
        monkeypatch.setattr(e017.Path, "is_file", lambda self: True)
        # Should not raise; prints OK message.
        e017._run_quota_preflight()
        captured = capsys.readouterr()
        assert "pre-flight OK" in captured.out

    def test_preflight_skippable_via_env(self, monkeypatch, capsys):
        """Setting SKIP_QUOTA_PREFLIGHT=1 short-circuits the probe for
        smoke / tests (per E-020.3 spec)."""
        import importlib
        e017 = importlib.import_module("scripts.run_e017_fullval_seed")
        monkeypatch.setenv("SKIP_QUOTA_PREFLIGHT", "1")
        # Subprocess.run should NOT be called; if it is, the test fails.
        def _fail_if_called(*a, **kw):  # noqa: ARG001
            raise AssertionError(
                "subprocess.run should not be called when SKIP_QUOTA_PREFLIGHT=1"
            )
        monkeypatch.setattr(subprocess, "run", _fail_if_called)
        e017._run_quota_preflight()
        captured = capsys.readouterr()
        assert "SKIP_QUOTA_PREFLIGHT" in captured.out

    def test_preflight_timeout_aborts(self, monkeypatch):
        """Probe timing out ``sys.exit(2)``s (server likely unreachable)."""
        import importlib
        e017 = importlib.import_module("scripts.run_e017_fullval_seed")

        def _raise_timeout(cmd, capture_output, text, timeout):  # noqa: ARG001
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout)

        monkeypatch.setattr(subprocess, "run", _raise_timeout)
        monkeypatch.setattr(e017.Path, "is_file", lambda self: True)

        with pytest.raises(SystemExit) as excinfo:
            e017._run_quota_preflight(timeout_s=1)
        assert excinfo.value.code == 2
