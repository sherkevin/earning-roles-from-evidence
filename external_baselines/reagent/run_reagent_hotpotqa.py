"""ReAgent HotpotQA adapter — thin wrapper around Moderator2, our seed JSONL.

Per ``docs/paper/e018_reagent_adapter_inspection.md`` spec (R41 engineer
inspection). Corrections from the spec file after deeper code reading on
server (R41, this session):

  1. ReAgent's api_call reads ``config/env.yaml`` (relative to repo root),
     not ``services.yaml``; this file must be written BEFORE we import any
     ReAgent module (``backend.api`` loads it at import time).
  2. ``Moderator2.__init__(name, model)`` takes only 2 args, not the
     ``name/model/args/group`` signature suggested by main.py's usage.
  3. ``Moderator2.o1think(task, knowledges, group, args)`` returns
     ``(final_ans, steps)`` (not a dict).
  4. ``GroupChatEnvironment(people, args)`` takes ``people=`` (not
     ``agents=``); wraps ``build_agents()``'s list.
  5. ``args`` must have ``.temperature``, ``.mas``, ``.retrieval``,
     ``.truth``, ``.model``, ``.dataset_path``, ``.debug`` attributes.

Writes results to ``--out-dir`` in a minimal ``predictions.jsonl`` +
``metrics.json`` pair compatible with our
``workspace/idea04_core/evaluation.py`` scorers.

Usage (on server)::

    source external_baselines/reagent/venv_reagent/bin/activate
    python external_baselines/reagent/run_reagent_hotpotqa.py \\
        --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \\
        --n 5 \\
        --out-dir artifacts/external_baselines/reagent/smoke_$(date +%Y%m%d_%H%M%S)/

Budget estimate: 5 samples × ~6 steps × ~800 tokens ≈ $0.20 on gpt-4.1-mini.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAGENT_ROOT = Path(__file__).resolve().parent

# idea04_core evaluation lives in workspace/; we need the real scorers, not
# ReAgent's own evaluation (which has stricter exact-match semantics).
sys.path.insert(0, str(_REPO_ROOT / "workspace"))
from idea04_core.evaluation import exact_match, token_f1  # noqa: E402

# ReAgent's repo is a sibling dir; add it to sys.path AFTER env.yaml is ready.
# We defer the ReAgent imports to _import_reagent() below.


_TITLE_RE = re.compile(r"^\[([^\]]+)\]\s*(.*)$", re.DOTALL)


def _convert_sample_to_reagent_schema(seed_row: dict) -> dict:
    """Convert one row of our raw_inputs.jsonl to ReAgent's native HotpotQA schema.

    Our schema:
        {"task_id", "question", "answer", "context_passages": list[str]}

    ReAgent expects:
        {"_id", "type", "level", "question", "answer",
         "context": list[[title, list[sentence]]],
         "supporting_facts": list[[title, sent_idx]]}
    """
    ctx: list[list] = []
    for passage in seed_row.get("context_passages", []):
        m = _TITLE_RE.match(passage)
        if m:
            title, body = m.group(1).strip(), m.group(2)
        else:
            title, body = "UnknownTitle", passage
        # Split body into sentences: HotpotQA canonical raw uses double-space
        # between sentences; fall back to single-space split.
        sentences = re.split(r"\.\s{2,}", body)
        if len(sentences) == 1:
            sentences = body.split(". ")
        sentences = [
            (s.rstrip() + ("." if not s.endswith(".") else "")).strip()
            for s in sentences
            if s.strip()
        ]
        ctx.append([title, sentences])

    return {
        "_id": seed_row["task_id"],
        "type": "bridge",   # safe default: used only for logging in ReAgent
        "level": "medium",  # safe default: same
        "question": seed_row["question"],
        "answer": seed_row.get("answer", ""),
        "context": ctx,
        "supporting_facts": seed_row.get("supporting_facts", []),
    }


def _write_env_yaml(config_dir: Path, llm_json_path: Path) -> None:
    """Write ReAgent's ``config/env.yaml`` with newapi credentials.

    ReAgent's ``backend.api`` calls ``load_env()`` at import time which reads
    ``config/env.yaml`` relative to the current working directory — so we must
    write this file AND chdir to the reagent repo root before importing.
    """
    import yaml
    cfg = json.loads(llm_json_path.read_text(encoding="utf-8"))
    nb = cfg.get("newapi") or cfg.get("providers", {}).get("newapi", {})
    if not nb:
        raise RuntimeError(
            f"[reagent_hotpotqa] newapi block not found in {llm_json_path}. "
            "Expected configs/llm.json to have a 'newapi' or "
            "'providers.newapi' entry with key + url fields."
        )
    key = nb["key"]
    url = str(nb.get("url") or nb.get("base_url") or "https://xh.v1api.cc/v1").rstrip("/")
    services = {
        "services": {
            # ReAgent's api_call() routes on substring: "gpt"/"o1" → openai,
            # "qwen" → qwen, "deepseek" → deepseek, "claude" → claude.
            # We wire the openai block to newapi; other blocks are stubs so
            # import doesn't fail.
            "openai": {"api_key": key, "base_url": url},
            "qwen": {"api_key": "stub", "base_url": "https://stub.invalid"},
            "deepseek": {"api_key": "stub", "base_url": "https://stub.invalid"},
            "claude": {"api_key": "stub", "base_url": "https://stub.invalid"},
        }
    }
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "env.yaml").write_text(
        yaml.safe_dump(services, sort_keys=False), encoding="utf-8"
    )


def _preflight_quota(timeout_s: int = 30) -> None:
    """E-020.3-style pre-flight quota probe. Abort with exit 2 on non-ACTIVE.

    Honors ``SKIP_QUOTA_PREFLIGHT=1`` env var for unit / smoke tests.
    """
    if os.environ.get("SKIP_QUOTA_PREFLIGHT", "").strip().lower() in (
        "1", "true", "yes",
    ):
        print("[reagent_hotpotqa] SKIP_QUOTA_PREFLIGHT set — skipping probe.",
              flush=True)
        return
    probe = _REPO_ROOT / "workspace/tmp/newapi_quota_probe.sh"
    if not probe.is_file():
        print(f"[reagent_hotpotqa] WARNING: probe not found at {probe}",
              flush=True)
        return
    try:
        r = subprocess.run(
            ["bash", str(probe)], capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        print(f"[reagent_hotpotqa] FATAL: probe timed out after {timeout_s}s",
              file=sys.stderr, flush=True)
        sys.exit(2)
    if "newapi ACTIVE" not in (r.stdout or ""):
        print(
            "[reagent_hotpotqa] FATAL PRE-FLIGHT: newapi quota not ACTIVE.\n"
            f"  stdout: {r.stdout[-400:]}\n  stderr: {r.stderr[-400:]}",
            file=sys.stderr, flush=True,
        )
        sys.exit(2)
    print("[reagent_hotpotqa] pre-flight OK: newapi ACTIVE", flush=True)


class _ReAgentArgs:
    """Args surface expected by ReAgent's Moderator2 + build_agents.

    Mirrors ``external_baselines/reagent/main.py`` ``Args`` class but lets
    caller override each field.
    """

    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        temperature: float = 1.0,
        mas: bool = True,
        truth: bool = False,
        retrieval: bool = False,
        debug: bool = False,
        dataset_path: str = "",
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.mas = mas
        self.truth = truth
        self.retrieval = retrieval
        self.debug = debug
        self.dataset_path = dataset_path


def _monkey_patch_api_call():
    """W3 workaround — use our own llm_client.call_llm instead of openai SDK.

    Root cause (diagnosed R41c, 2026-04-20): the newapi endpoint
    (xh.v1api.cc/v1) returns an HTML error page (its web dashboard landing
    page, starts ``<!doctype html><html lang="zh">``) for certain payloads
    — likely a WAF / size-limit trigger — and ``openai==2.32.0`` silently
    returns the HTML as a Python str from ``client.chat.completions.create``
    instead of raising. ReAgent's ``api_call`` then crashes with
    ``'str' object has no attribute 'choices'`` and retries 10× without
    progress.

    W3 fix: replace ReAgent's ``backend.api.api_call`` with a wrapper that
    uses our ``workspace/idea04_core/llm_client.call_llm`` (urllib-based,
    preserves E-020 QuotaExhaustedError guard, handles HTML-response
    gracefully because urllib raises on non-200). For ``json_format=True``
    we add a strict "Output ONLY JSON" reminder + parse the response with
    ``json.loads``.

    Per `docs/paper/e018_reagent_adapter_inspection.md §11.3 W3`.
    """
    import backend.api as _api
    import time as _time
    import logging
    import json as _json
    _log = logging.getLogger(__name__)

    # Import our canonical llm_client (urllib-based, E-020 protected).
    from idea04_core.llm_client import (  # noqa: E402
        call_llm as _our_call_llm,
        extract_text as _our_extract_text,
        configure_runtime as _our_configure_runtime,
        QuotaExhaustedError as _OurQuotaError,
    )
    # Configure once with the canonical model. enforce_model=False because
    # ReAgent may pass variants (o1/deepseek/etc) during exploratory calls.
    _our_configure_runtime("gpt-4.1-mini", enforce_model=False)

    def _safe_api_call(
        messages, model="deepseek", temperature=1.0, max_tokens=4096,
        max_retries=10, json_format=False, stream=False,
    ):
        # W3: we always route through our newapi-wired llm_client (per
        # configure_runtime above), ignoring ReAgent's service routing.
        # ReAgent passes model="gpt-4.1-mini" (from our --model flag) so
        # this matches the intent anyway; other models would need
        # ReAgent-side config changes we don't support.
        # We still cap max_tokens to prevent HTML-dashboard-response trigger.
        # Empirically n=5 smokes work with max_tokens <= 1024; ReAgent's
        # default 2048 is safely above our observed bound but we cap to
        # 1024 defensively for long-HotpotQA-context calls.
        effective_max_tokens = min(int(max_tokens or 1024), 1024)

        # Build messages; for json_format add strict JSON-only reminder.
        msgs = list(messages)
        if json_format:
            reminder = (
                " Respond with ONLY a single valid JSON object. "
                "No markdown fences, no prose, no explanation outside the JSON."
            )
            if msgs and msgs[0].get("role") == "system":
                msgs[0] = dict(msgs[0])
                msgs[0]["content"] = msgs[0].get("content", "") + reminder
            else:
                msgs = [{"role": "system", "content": reminder.strip()}] + msgs

        last_err = None
        for attempt in range(max_retries):
            try:
                resp = _our_call_llm(
                    messages=msgs,
                    model="gpt-4.1-mini",  # forced to our canonical backbone
                    temperature=float(temperature),
                    max_tokens=effective_max_tokens,
                    retries=2,  # our client's internal retries; outer loop is moderator's
                )
                content = _our_extract_text(resp)
                if not content:
                    continue
                if not json_format:
                    return content
                # Parse JSON ourselves
                content_stripped = content.strip()
                if content_stripped.startswith("```"):
                    # Strip markdown fences
                    lines = content_stripped.splitlines()
                    if lines and lines[0].startswith("```"):
                        lines = lines[1:]
                    while lines and lines[-1].strip().startswith("```"):
                        lines.pop()
                    content_stripped = "\n".join(lines).strip()
                try:
                    return _json.loads(content_stripped)
                except Exception as parse_exc:
                    # Extract the largest balanced {...} block and retry parse
                    first = content_stripped.find("{")
                    last = content_stripped.rfind("}")
                    if 0 <= first < last:
                        try:
                            return _json.loads(content_stripped[first:last + 1])
                        except Exception:
                            pass
                    print(
                        f"[safe_api_call] JSON parse fail attempt {attempt+1}: "
                        f"{parse_exc} content head: {content_stripped[:200]!r}",
                        flush=True,
                    )
                    _time.sleep(2 ** (attempt + 1))
                    continue
            except _OurQuotaError:
                # Propagate quota exhaustion immediately (E-020 contract)
                raise
            except Exception as e:
                last_err = e
                print(
                    f"[safe_api_call] attempt {attempt+1}/{max_retries} "
                    f"failed: {type(e).__name__}: {str(e)[:200]}",
                    flush=True,
                )
                _time.sleep(2 ** (attempt + 1))
                continue
        raise Exception(
            f"Max retries reached. API call failed. Last error: {last_err}"
        )

    _api.api_call = _safe_api_call
    # Also patch in every module that did `from backend.api import api_call`
    # at import time. Those create LOCAL bindings which ignore _api.api_call
    # rebinding, so we must overwrite each module's own `api_call` attribute.
    # Modules known to bind api_call (from grep ./Agent/*.py):
    _candidate_modules = (
        "Agent.moderator2", "Agent.moderator", "Agent.agent",
        "Agent.blacksheep", "Agent.thinker", "Agent.human",
        "Environment.environment", "Environment.groupchat",
    )
    import importlib as _imp
    _patched = []
    for mname in _candidate_modules:
        try:
            mod = _imp.import_module(mname)
        except Exception:
            continue
        if hasattr(mod, "api_call"):
            mod.api_call = _safe_api_call
            _patched.append(mname)
    print(
        f"[reagent_hotpotqa] W1/W3 monkey-patch applied to: "
        f"{', '.join(_patched) if _patched else '(none found)'}",
        flush=True,
    )


def _apply_concise_answer_patch():
    """W(c) format-penalty workaround (R41f) — patch Moderator2.generate_o1_response
    so the final-answer request asks for a SHORT SPAN instead of a wordy COT summary.

    Root cause (R41c §12.4): ReAgent's Moderator2 final-answer prompt is
    "Now provide a final, plain-text answer. Avoid JSON. Summarize clearly
    without extraneous structure." — this invites 2-4 sentence COT
    summaries. On HotpotQA (gold answers are 1-5 tokens like "yes" / "Animorphs"
    / "Greenwich Village, New York City"), char-overlap F1 penalizes verbosity.

    Fix: rewrite the final-user-message content to: "Output ONLY the shortest
    possible answer span (typically 1-5 tokens). No explanation, no
    elaboration, no prefix/suffix. Use the exact wording from the passages
    where possible."

    Implementation: monkey-patch `generate_o1_response` to intercept the
    final ``messages.append({..."Now provide a final, plain-text answer..."})``
    step and replace the content string.
    """
    from Agent import moderator2 as _m2
    _orig_generate = _m2.Moderator2.generate_o1_response

    CONCISE_FINAL_PROMPT = (
        "Now provide a final answer. Output ONLY the shortest possible "
        "answer span (typically 1-5 tokens). No explanation, no elaboration, "
        "no markdown, no prefix like 'The answer is' — just the span itself. "
        "For yes/no questions reply with exactly 'yes' or 'no' (lowercase). "
        "For entity questions reply with just the entity name. "
        "Use the exact wording from the passages where possible."
    )

    def _concise_generate_o1_response(self, question):
        import json as _json
        # We intercept messages.append of the final-answer user message.
        # The cleanest approach: patch messages list mutation inside the
        # inner generator. Since generate_o1_response is a generator and
        # we can't easily wrap a single list operation, we instead replace
        # the method entirely with a near-identical copy that uses our
        # CONCISE_FINAL_PROMPT. We inline the upstream logic (copied from
        # Agent/moderator2.py lines 60-180 as of R41c).

        import time as _time
        step_count = 1
        total_thinking_time = 0
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert in multi-step reasoning tasks. The user has provided a question. "
                    "You must strictly return JSON outputs with keys: { \"step\", \"reasoning\", \"next_action\" }. "
                    "If you have a final answer, set \"next_action\" to \"final_answer\"."
                )
            },
            {"role": "user", "content": question},
            {
                "role": "assistant",
                "content": "Alright, I will proceed with multi-step JSON-based reasoning."
            }
        ]
        from backend.api import api_call  # this is our W3-patched safe_api_call

        while True:
            if self.user_message is not None:
                messages.append({
                    "role": "user",
                    "content": _json.dumps(self.user_message, ensure_ascii=False)
                })
            start_time = _time.time()
            step_data = None
            for attempt in range(10):
                try:
                    step_data = api_call(
                        messages,
                        model=self.model,
                        temperature=self.args.temperature if self.args else 1.0,
                        max_tokens=2048,
                        json_format=True,
                    )
                    if "step" in step_data and "reasoning" in step_data and "next_action" in step_data:
                        break
                except Exception:
                    _time.sleep(1)
            end_time = _time.time()
            step_time = end_time - start_time
            total_thinking_time += step_time
            if not step_data:
                break
            messages.append({
                "role": "assistant",
                "content": _json.dumps(step_data, indent=4, ensure_ascii=False)
            })
            self.steps.append(
                (f"Step {step_count}: {step_data['step']}", step_data['reasoning'], step_time)
            )
            step_count += 1
            ref = step_data.get("next_action", None)
            if ref and ref != "final_answer":
                messages.append({
                    "role": "user",
                    "content": (
                        f"Proceed with next action '{ref}' in JSON format. Do not produce an empty output."
                    )
                })
            else:
                break
            if step_count > 25:
                break
            yield self.steps, None

        # W(c) CHANGE: use concise final-answer prompt instead of
        # "Now provide a final, plain-text answer. ..."
        messages.append({"role": "user", "content": CONCISE_FINAL_PROMPT})
        start_time = _time.time()
        final_text = api_call(
            messages,
            self.model,
            self.args.temperature if self.args else 1.0,
            50,                # W(c) also caps at 50 tokens (short-span budget)
            json_format=False,
        )
        end_time = _time.time()
        final_time = end_time - start_time
        total_thinking_time += final_time
        self.steps.append(("Final Answer", final_text, final_time))
        yield self.steps, total_thinking_time

    _m2.Moderator2.generate_o1_response = _concise_generate_o1_response
    print(
        "[reagent_hotpotqa] W(c) concise-answer patch applied to Moderator2.generate_o1_response",
        flush=True,
    )


def _import_reagent() -> dict:
    """Import ReAgent modules. Must be called AFTER ``_write_env_yaml()`` +
    chdir to _REAGENT_ROOT (because ``backend.api`` reads ``config/env.yaml``
    via a relative path at import time).
    """
    sys.path.insert(0, str(_REAGENT_ROOT))
    from Agent.moderator2 import Moderator2              # noqa: E402
    from Agent.agent import BaseAgent                    # noqa: E402
    from Agent.blacksheep import BlackSheep              # noqa: E402
    from Agent.thinker import Thinker                    # noqa: E402
    from Agent.human import Human                        # noqa: E402
    from Environment.groupchat import GroupChatEnvironment  # noqa: E402
    from DataProcess.Dataset import HotpotqaDataset      # noqa: E402
    # W1: apply monkey-patch AFTER imports (so Moderator2.api_call ref points
    # to our safe wrapper — Moderator2 uses `from backend.api import api_call`
    # at module import time, so we must overwrite that reference explicitly).
    _monkey_patch_api_call()
    return {
        "Moderator2": Moderator2,
        "BaseAgent": BaseAgent,
        "BlackSheep": BlackSheep,
        "Thinker": Thinker,
        "Human": Human,
        "GroupChatEnvironment": GroupChatEnvironment,
        "HotpotqaDataset": HotpotqaDataset,
    }


def _build_people(mods, args: _ReAgentArgs) -> list:
    """Mirror main.py build_agents() but use our _ReAgentArgs shape."""
    core_roles = [
        "QuestionDecomposerAgent", "RetrieverAgent", "VerifierAgent",
        "AnswerAssemblerAgent", "SupervisorAgent", "ControllerAgent",
    ]
    people = [mods["BaseAgent"](name=r) for r in core_roles]
    # Optional specialized agents (only these have true vote() semantics).
    people.append(mods["Thinker"](name="ThinkerAgent", model=args.model, args=args))
    people.append(mods["BlackSheep"](name="BlackSheepAgent", model=args.model, args=args))
    people.append(mods["Human"](name="HumanAgent"))
    return people


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--samples-jsonl", required=True,
                   help="our raw_inputs.jsonl (head-N read as seed samples)")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--model", default="gpt-4.1-mini",
                   help="Must contain substring 'gpt' or 'o1' to route to "
                        "newapi via services.openai (ReAgent model routing).")
    p.add_argument("--llm-json", default=str(_REPO_ROOT / "configs/llm.json"))
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--mas", action="store_true", default=True,
                   help="Enable multi-agent voting (Moderator2 default true)")
    p.add_argument("--no-mas", dest="mas", action="store_false")
    p.add_argument("--skip-preflight", action="store_true")
    p.add_argument(
        "--concise",
        action="store_true",
        help=(
            "R41f W(c) format-penalty fix — patch Moderator2 to request a "
            "short-span final answer (1-5 tokens). Reduces HotpotQA F1 "
            "format penalty; see e018_reagent_adapter_inspection.md §12.4."
        ),
    )
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Pre-flight quota probe (per E-020.3 pattern).
    if not args.skip_preflight:
        _preflight_quota()

    # Write env.yaml BEFORE any ReAgent import (api_call loads it at import time).
    _write_env_yaml(_REAGENT_ROOT / "config", Path(args.llm_json))

    # chdir to reagent root so api_call's relative path `config/env.yaml` resolves.
    old_cwd = Path.cwd()
    os.chdir(_REAGENT_ROOT)
    try:
        # Load + convert our seed rows.
        rows: list[dict] = []
        seed_path = Path(args.samples_jsonl)
        if not seed_path.is_absolute():
            seed_path = (_REPO_ROOT / seed_path).resolve()
        with seed_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
                if len(rows) >= args.n:
                    break
        reagent_data = [_convert_sample_to_reagent_schema(r) for r in rows]
        tmp_json = out_dir / "reagent_input.json"
        # NOTE: out_dir was resolved relative to our ORIGINAL cwd; after
        # chdir, write the absolute form.
        tmp_json_abs = old_cwd / out_dir / "reagent_input.json" if not out_dir.is_absolute() else tmp_json
        tmp_json_abs.write_text(
            json.dumps(reagent_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        mods = _import_reagent()
        if args.concise:
            _apply_concise_answer_patch()
        rag_args = _ReAgentArgs(
            model=args.model,
            temperature=args.temperature,
            mas=args.mas,
            truth=False,
            retrieval=False,
            debug=False,
            dataset_path=str(tmp_json_abs),
        )
        dataset = mods["HotpotqaDataset"](dataset_path=str(tmp_json_abs))
        people = _build_people(mods, rag_args)
        group = mods["GroupChatEnvironment"](people=people, args=rag_args)

        moderator = mods["Moderator2"](name="R41Mod", model=args.model)

        preds: list[dict] = []
        t0 = time.time()
        for i, task in enumerate(dataset.tasks):
            try:
                knowledges = task.get_knowledge(rag_args)  # HotpotQA __str__
                final_ans, _steps = moderator.o1think(
                    task=task,
                    knowledges=knowledges,
                    group=group,
                    args=rag_args,
                )
                if not isinstance(final_ans, str):
                    final_ans = "" if final_ans is None else str(final_ans)
            except BaseException as exc:
                print(f"[reagent_hotpotqa] sample {i+1}/{len(dataset.tasks)} "
                      f"task={task.id} raised {type(exc).__name__}: {exc}",
                      flush=True)
                final_ans = ""

            em = exact_match(final_ans, task.answer)
            f1 = token_f1(final_ans, task.answer)
            pred = {
                "task_id": task.id,
                "question": task.question,
                "gold_answer": task.answer,
                "final_answer": final_ans[:500],  # truncate for readability
                "answer_em": em,
                "answer_f1": f1,
            }
            preds.append(pred)
            running_f1 = sum(p["answer_f1"] for p in preds) / len(preds)
            running_em = sum(p["answer_em"] for p in preds) / len(preds)
            print(
                f"[reagent_hotpotqa] {i+1}/{len(dataset.tasks)} "
                f"partial_F1={running_f1:.4f} partial_EM={running_em:.4f}",
                flush=True,
            )

        # Write predictions + metrics to out_dir (resolve again under original cwd).
        preds_path = old_cwd / out_dir / "predictions.jsonl" if not out_dir.is_absolute() else out_dir / "predictions.jsonl"
        metrics_path = old_cwd / out_dir / "metrics.json" if not out_dir.is_absolute() else out_dir / "metrics.json"
        preds_path.write_text(
            "\n".join(json.dumps(p, ensure_ascii=False) for p in preds) + "\n",
            encoding="utf-8",
        )
        metrics = {
            "host": "ReAgent (Moderator2, o1-style multi-agent)",
            "adapter": "run_reagent_hotpotqa.py (mas={} retrieval=False concise={})".format(
                "on" if args.mas else "off",
                "on" if args.concise else "off",
            ),
            "benchmark": "hotpotqa",
            "sample_count": len(preds),
            "answer_em": sum(p["answer_em"] for p in preds) / max(1, len(preds)),
            "answer_f1": sum(p["answer_f1"] for p in preds) / max(1, len(preds)),
            "wall_s": round(time.time() - t0, 2),
            "model": args.model,
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "notes": [
                "Thin wrapper invokes Moderator2.o1think(task, knowledges, group, args).",
                "mas=True enables BlackSheep/Thinker/Human voting per round; mas=False = pure o1 single-agent.",
                "retrieval=False: HotpotQA gold context is fed via get_knowledge() directly (no DPR).",
                "Per docs/paper/e018_reagent_adapter_inspection.md.",
            ],
        }
        metrics_path.write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("\n=== METRICS ===")
        print(json.dumps(metrics, indent=2))

    finally:
        os.chdir(old_cwd)

    return 0


if __name__ == "__main__":
    sys.exit(main())
