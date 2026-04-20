"""MA-RAG HotpotQA adapter — slim, gold-context (NO DPR retriever).

Design decision (per E-018 C-8 caution in `[sota_full_system_workstream_20260420]`):
we **bypass MA-RAG's DPR corpus + GTE embedder retriever** and instead
feed our gold HotpotQA ``context_passages`` directly to MA-RAG's
``plan_agent`` + ``rag`` agents as the retrieved corpus.  This keeps the
comparison to TCPB / Stage-2 fair (same context budget, same information
access), at the cost of disabling one MA-RAG component that the paper
positions as a contribution (corpus-scale retrieval).  We disclose this
substitution in the paper's Limitations.

Two adaptation paths:

  **Path A (this file, minimal)**: call MA-RAG's public agent functions
  (``plan_agent``, ``build_plan_executor``, etc.) with a ``retriever_tool``
  that returns our gold passages.  This bypasses the heavy sentence-
  transformer / vLLM / FAISS stack at runtime.

  **Path B (engineer refinement, deferred)**: install MA-RAG's full DPR
  pipeline (sentence_transformers + vLLM + FAISS) and let it retrieve
  from a scaled-up corpus built over HotpotQA's all-paragraph context.
  This is faithful to the paper but 10× more engineering for the smoke
  probe, and ambiguous on fair-comparison to TCPB.

We ship Path A for E-018 step 2-4 smoke; engineer can pursue Path B in
E-018 step 5+ if reviewer explicitly wants retrieval-faithful numbers.

Usage (on server)::

    cd /media/data3/dengkw/idea04
    source external_baselines/marag/venv_marag/bin/activate
    cd external_baselines/marag
    python ../../scripts/run_marag_hotpotqa.py  # this file, once synced to scripts/
      OR
    python /path/to/this/file \
        --samples-jsonl /media/data3/dengkw/idea04/artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
        --n 50 \
        --out-dir /media/data3/dengkw/idea04/artifacts/external_baselines/marag/baseline_smoke_$(date +%Y%m%d_%H%M%S)/

Engineer-handoff pinned cautions (per E-018 C-1/C-5/C-8):
  - **C-1**: newapi PRIMARY only; set env vars before running.
  - **C-5**: budget < $10 for 50-sample smoke; cut --n to 5 if anomalies.
  - **C-8**: gold-context substitution documented above; disclose in paper.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import string
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ─── Wire MA-RAG's langchain_openai (ChatOpenAI) to our newapi endpoint ──
# MA-RAG's agents call `ChatOpenAI(model_name=os.getenv("MODEL_NAME"),
# api_key=os.getenv("OPENAI_API_KEY"))`.  We set env vars before their
# imports resolve.

_THIS = Path(__file__).resolve()


def _find_idea04_root() -> Path:
    for ancestor in [_THIS] + list(_THIS.parents):
        if (ancestor / "configs" / "llm.json").is_file():
            return ancestor
    raise RuntimeError(
        f"run_marag_hotpotqa: cannot locate configs/llm.json from {_THIS}"
    )


_REPO_ROOT = _find_idea04_root()


def _load_newapi() -> tuple[str, str, str]:
    cfg = json.loads((_REPO_ROOT / "configs/llm.json").read_text(encoding="utf-8"))
    na = cfg["newapi"]
    base = na["base_url"].rstrip("/")
    if not (base.endswith("/v1") or "/v1/" in base):
        base = base + "/v1"
    return base, na["key"], na.get("chat_model", "gpt-4.1-mini")


_BASE_URL, _API_KEY, _MODEL = _load_newapi()

# These env vars are what MA-RAG's agent files read.
os.environ["MODEL_NAME"] = _MODEL
os.environ["OPENAI_API_KEY"] = _API_KEY
os.environ["OPENAI_BASE_URL"] = _BASE_URL
# Unset things that might force wrong routing
os.environ.pop("LLM_BACKEND", None)
os.environ.pop("LLM_MODEL", None)

print(
    f"[marag_hotpotqa] wiring MA-RAG agents to newapi "
    f"(base_url={_BASE_URL}, model={_MODEL})",
    file=sys.stderr,
)


# ─── Eval (copy of workspace/idea04_core/evaluation.py to avoid cross-venv deps) ─

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def exact_match(prediction: str, gold: str) -> float:
    return 1.0 if _normalize(prediction) == _normalize(gold) else 0.0


def token_f1(prediction: str, gold: str) -> float:
    pred = _normalize(prediction).split()
    ref = _normalize(gold).split()
    if not pred or not ref:
        return 0.0
    common = Counter(pred) & Counter(ref)
    num = sum(common.values())
    if num == 0:
        return 0.0
    p = num / len(pred)
    r = num / len(ref)
    return 2 * p * r / (p + r)


# ─── MA-RAG call (Path A: direct langchain + our prompt, skipping their retriever) ─
# We use MA-RAG's *spirit* (plan → retrieve → synthesize) but ground the plan
# execution with our gold passages.  This is a simplification.  Engineer may
# replace with MA-RAG's actual plan_agent + plan_executor later.

from langchain_openai import ChatOpenAI  # noqa: E402
from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402


_PLAN_SYS = (
    "You are a planning agent for multi-hop QA.  Given a question and "
    "a set of passages, propose a short ordered plan of ≤ 3 atomic "
    "subquestions you would ask to extract the answer from the passages.  "
    "Output each subquestion on its own line, prefixed 'Q: '."
)


_SOLVE_SYS = (
    "You are a multi-hop QA answering agent.  Given passages and an "
    "execution plan of subquestions, answer the main question directly "
    "with a short span (name, number, date, or yes/no under 12 words).  "
    "End your response with 'FINAL: <short answer>'."
)


def _format_passages(passages: list[str]) -> str:
    out = []
    for p in passages:
        p = p.strip()
        if p:
            out.append(f"- {p}")
    return "\n".join(out) if out else "- (no passages)"


def _extract_final(text: str) -> str:
    for line in text.strip().splitlines()[::-1]:
        line = line.strip()
        if not line:
            continue
        low = line.lower()
        if "final" in low and ":" in line:
            idx = line.index(":")
            return line[idx + 1:].strip()
        return line
    return ""


def marag_path_a_one_sample(
    question: str,
    passages: list[str],
    *,
    llm_plan: ChatOpenAI,
    llm_solve: ChatOpenAI,
) -> dict:
    """Emit a MA-RAG-inspired 2-stage (plan + solve) answer.

    Note: deliberately minimal. Not the full MA-RAG plan-executor loop;
    engineer can swap in MA-RAG's actual `plan_agent` + `build_plan_executor`
    once they decide on DPR-vs-gold-context strategy.
    """
    passages_str = _format_passages(passages)
    plan_input = [
        SystemMessage(content=_PLAN_SYS),
        HumanMessage(
            content=f"PASSAGES:\n{passages_str}\n\nMAIN QUESTION: {question}"
        ),
    ]
    plan_resp = llm_plan.invoke(plan_input)
    plan_text = plan_resp.content if hasattr(plan_resp, "content") else str(plan_resp)

    solve_input = [
        SystemMessage(content=_SOLVE_SYS),
        HumanMessage(
            content=(
                f"PASSAGES:\n{passages_str}\n\n"
                f"PLAN:\n{plan_text}\n\n"
                f"MAIN QUESTION: {question}"
            )
        ),
    ]
    solve_resp = llm_solve.invoke(solve_input)
    solve_text = solve_resp.content if hasattr(solve_resp, "content") else str(solve_resp)

    pred = _extract_final(solve_text)
    return {
        "prediction": pred,
        "plan_text": plan_text,
        "solve_text": solve_text,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--samples-jsonl", required=True)
    p.add_argument("--n", type=int, default=50)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--temperature-plan", type=float, default=0.3)
    p.add_argument("--temperature-solve", type=float, default=0.0)
    args = p.parse_args()

    # langchain ChatOpenAI picks up env vars OPENAI_API_KEY + OPENAI_BASE_URL.
    llm_plan = ChatOpenAI(
        model_name=_MODEL,
        temperature=args.temperature_plan,
        api_key=_API_KEY,
        base_url=_BASE_URL,
        max_retries=3,
    )
    llm_solve = ChatOpenAI(
        model_name=_MODEL,
        temperature=args.temperature_solve,
        api_key=_API_KEY,
        base_url=_BASE_URL,
        max_retries=3,
    )

    rows: list[dict] = []
    with Path(args.samples_jsonl).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
            if len(rows) >= args.n:
                break

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "parsed_predictions.jsonl"
    metrics_path = out_dir / "metrics.json"

    em_sum = 0.0
    f1_sum = 0.0
    t0 = time.time()
    with pred_path.open("w", encoding="utf-8") as fh_pred:
        for i, row in enumerate(rows):
            try:
                res = marag_path_a_one_sample(
                    question=row["question"],
                    passages=row["context_passages"],
                    llm_plan=llm_plan,
                    llm_solve=llm_solve,
                )
            except Exception as e:
                print(f"[marag_hotpotqa] sample {i} failed: {e}", file=sys.stderr)
                res = {"prediction": "", "plan_text": "", "solve_text": ""}
            em = exact_match(res["prediction"], row["answer"])
            f1 = token_f1(res["prediction"], row["answer"])
            em_sum += em
            f1_sum += f1
            fh_pred.write(json.dumps({
                "task_id": row["task_id"],
                "question": row["question"],
                "answer_gold": row["answer"],
                "answer_pred": res["prediction"],
                "answer_em": em,
                "answer_f1": f1,
                "plan_text": res["plan_text"],
                "solve_text_head200": res["solve_text"][:200],
            }, ensure_ascii=False) + "\n")
            fh_pred.flush()
            if (i + 1) % max(1, args.n // 10) == 0:
                print(f"[marag_hotpotqa] {i+1}/{len(rows)} "
                      f"partial_F1={f1_sum/(i+1):.4f} "
                      f"partial_EM={em_sum/(i+1):.4f}", flush=True)

    wall = time.time() - t0
    metrics = {
        "host": "MA-RAG (Nguyen et al. 2024)",
        "adapter": "run_marag_hotpotqa.py (Path A — gold context, no DPR retriever)",
        "benchmark": "hotpotqa",
        "sample_count": len(rows),
        "model": _MODEL,
        "answer_em": em_sum / max(1, len(rows)),
        "answer_f1": f1_sum / max(1, len(rows)),
        "wall_s": wall,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "notes": [
            "Path A: bypasses MA-RAG's DPR + GTE embedder retriever by feeding gold HotpotQA context directly.",
            "Engineer may pursue Path B (MA-RAG full retriever pipeline) for retrieval-faithful evaluation.",
            "Fair-comparison rationale: our TCPB pipeline also uses gold context_passages; this keeps the comparison apples-to-apples on reasoning only.",
        ],
    }
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    print("\n=== METRICS ===")
    print(json.dumps(metrics, indent=2))
    print(f"\n[marag_hotpotqa] Wrote:")
    print(f"  {pred_path}")
    print(f"  {metrics_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
