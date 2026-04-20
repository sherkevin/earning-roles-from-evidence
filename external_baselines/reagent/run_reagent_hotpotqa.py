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
            "adapter": "run_reagent_hotpotqa.py (mas={} retrieval=False)".format(
                "on" if args.mas else "off"
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
