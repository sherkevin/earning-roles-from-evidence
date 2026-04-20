"""MAD HotpotQA driver — adapt Du et al. 2024 multi-agent-debate to HotpotQA.

Modelled after ``external_baselines/mad/math/gen_math.py`` (Du et al.'s math
driver).  Differences:

  - Question source: HotpotQA validation seed (our raw_inputs.jsonl head-N)
    instead of randomly-generated arithmetic problems.
  - Context: each HotpotQA question comes with gold ``context_passages``
    (per ``raw_inputs.jsonl`` schema from ``artifacts/round2_gpt41mini_fullval/
    run_20260414_135408/fixed_peer_calibrated/``).  Feed those to every agent.
  - Answer extraction: HotpotQA answers are short spans (entity / yes-no /
    number), not floats.  Use a "FINAL ANSWER:" marker instead of
    ``parse_answer``'s float-extraction heuristic.
  - Aggregation: majority vote of the last-round text answers, ties broken by
    frequency (same as MAD's ``most_frequent``).
  - Eval: HotpotQA EM + F1 (via our ``workspace/idea04_core/evaluation.py``).
  - Endpoint: newapi (``xh.v1api.cc``) via ``openai_compat_shim`` — **MUST be
    imported FIRST**, before ``openai`` or any MAD module.

Usage (on server)::

    cd /media/data3/dengkw/idea04
    source external_baselines/mad/venv_mad/bin/activate
    python external_baselines/mad/hotpotqa/gen_hotpotqa.py \
        --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
        --n 50 \
        --agents 3 --rounds 2 \
        --out-dir artifacts/external_baselines/mad/baseline_smoke_$(date +%Y%m%d_%H%M%S)/

Budget estimate: n × agents × rounds × ~1500 tokens/call.
  50 × 3 × 2 = 300 calls × ~1500 tokens = 450 K tokens ≈ $0.50 on gpt-4.1-mini.

Engineer-handoff pinned cautions (per ``[sota_full_system_workstream_20260420]``
E-015/E-016 spec):

  - **C-1**: newapi PRIMARY only; ``openai_compat_shim`` enforces this.
  - **C-3**: isolated venv; do NOT pollute our production path.
  - **C-5**: budget < $5 for smoke; cut --n to 10 if first few samples OOB.
"""

from __future__ import annotations

# ─── MUST be first: redirects legacy openai 0.27.6 → newapi ──────────────
import sys
from pathlib import Path

# Make the shim discoverable when running from this directory.
_HERE = Path(__file__).resolve().parent
_MAD_ROOT = _HERE.parent  # external_baselines/mad/
sys.path.insert(0, str(_MAD_ROOT))

from openai_compat_shim import shim_active, RESOLVED_MODEL, coerce_model  # noqa: F401, E402
assert shim_active, "openai_compat_shim must activate before any MAD call"

# ─── stdlib + openai (now redirected to newapi) ───────────────────────────
import argparse  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
import string  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

import openai  # noqa: E402  (already patched by shim)


# ─── Evaluation (copy-paste from workspace/idea04_core/evaluation.py so we
# don't need to add idea04_core to the MAD venv's sys.path) ───────────────

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def exact_match(prediction: str, gold: str) -> float:
    return 1.0 if _normalize(prediction) == _normalize(gold) else 0.0


def token_f1(prediction: str, gold: str) -> float:
    pred_tokens = _normalize(prediction).split()
    gold_tokens = _normalize(gold).split()
    if not pred_tokens or not gold_tokens:
        return 0.0
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common.values())
    if num_common == 0:
        return 0.0
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


# ─── MAD-style debate, adapted for HotpotQA ───────────────────────────────

FINAL_ANSWER_MARKER = "FINAL ANSWER:"


def _format_context(passages: list[str]) -> str:
    lines = []
    for p in passages:
        p = p.strip()
        if p:
            lines.append(f"  - {p}")
    return "\n".join(lines) if lines else "  (no passages provided)"


def _build_opening_prompt(question: str, passages: list[str]) -> str:
    return (
        "You are answering a HotpotQA multi-hop question using the given "
        "passages.  The answer is short: a name, place, date, number, or "
        "yes/no under 12 words.  Reason step by step, then END your response "
        f"with a line '{FINAL_ANSWER_MARKER} <your short answer>'.\n\n"
        f"PASSAGES:\n{_format_context(passages)}\n\n"
        f"QUESTION: {question}"
    )


def _build_debate_prompt(
    question: str,
    passages: list[str],
    other_agent_responses: list[str],
) -> str:
    prefix = (
        "You previously answered a HotpotQA question.  Here are the recent "
        "answers from the other agents in this debate:\n"
    )
    for i, resp in enumerate(other_agent_responses):
        prefix += f"\n  Agent {i+1} response:\n    ```{resp.strip()}```\n"
    prefix += (
        "\nUse these other agents' reasoning carefully.  Do they "
        "identify evidence you missed?  Do you disagree on the final "
        "answer?  Update your answer or defend it.  End your response "
        f"with a line '{FINAL_ANSWER_MARKER} <your short answer>'.\n\n"
        f"PASSAGES:\n{_format_context(passages)}\n\n"
        f"QUESTION: {question}"
    )
    return prefix


def _extract_final_answer(response_text: str) -> str:
    """Pull the short-form answer after the FINAL ANSWER: marker, or fall back
    to the last non-empty line."""
    for line in response_text.strip().splitlines()[::-1]:
        stripped = line.strip()
        if not stripped:
            continue
        low = stripped.lower()
        if "final answer" in low:
            idx = low.find("final answer")
            tail = stripped[idx + len("final answer"):]
            tail = tail.lstrip(":").strip()
            if tail:
                return tail
        # otherwise, last non-empty line is a reasonable fallback
        return stripped
    return ""


def _chat_complete(messages: list[dict], max_retries: int = 3) -> str:
    """Thin wrapper around MAD's legacy openai.ChatCompletion.create with
    newapi + RESOLVED_MODEL + bounded retry."""
    for attempt in range(max_retries):
        try:
            resp = openai.ChatCompletion.create(
                model=RESOLVED_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=512,
                n=1,
            )
            return resp["choices"][0]["message"]["content"]
        except Exception as e:  # noqa: BLE001
            if attempt == max_retries - 1:
                raise
            wait_s = 2 ** attempt + 1
            print(f"[mad_hotpotqa] retry {attempt+1} after {wait_s}s: {e}",
                  file=sys.stderr)
            time.sleep(wait_s)
    return ""


def _majority_vote(final_answers: list[str]) -> str:
    """MAD's `most_frequent` but string-aware using our normalize."""
    if not final_answers:
        return ""
    norm = [_normalize(a) for a in final_answers]
    counts = Counter(norm)
    winner_norm, _ = counts.most_common(1)[0]
    for original, normed in zip(final_answers, norm, strict=False):
        if normed == winner_norm:
            return original
    return final_answers[-1]


def debate_one_sample(
    question: str,
    passages: list[str],
    gold_answer: str,
    *,
    agents: int,
    rounds: int,
) -> dict:
    """Run a single (agents × rounds) debate, return prediction + metrics."""
    opening = _build_opening_prompt(question, passages)
    agent_contexts: list[list[dict]] = [
        [{"role": "user", "content": opening}] for _ in range(agents)
    ]
    token_usage_proxy = 0  # proxy: prompt length chars (endpoint may not return usage consistently for old API)

    for round_idx in range(rounds):
        for i in range(agents):
            if round_idx > 0:
                other_responses = [
                    agent_contexts[j][-1]["content"]
                    for j in range(agents)
                    if j != i
                ]
                debate_msg = _build_debate_prompt(
                    question, passages, other_responses
                )
                agent_contexts[i].append({"role": "user", "content": debate_msg})

            reply = _chat_complete(agent_contexts[i])
            agent_contexts[i].append({"role": "assistant", "content": reply})
            token_usage_proxy += len(reply)

    final_answers = [
        _extract_final_answer(ctx[-1]["content"]) for ctx in agent_contexts
    ]
    prediction = _majority_vote(final_answers)
    return {
        "prediction": prediction,
        "final_answers_per_agent": final_answers,
        "f1": token_f1(prediction, gold_answer),
        "em": exact_match(prediction, gold_answer),
        "agent_transcripts": agent_contexts,
        "token_usage_proxy_chars": token_usage_proxy,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--samples-jsonl", required=True,
                   help="path to raw_inputs.jsonl (HotpotQA samples)")
    p.add_argument("--n", type=int, default=50, help="number of samples")
    p.add_argument("--agents", type=int, default=3)
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    random.seed(args.seed)

    rows: list[dict] = []
    with Path(args.samples_jsonl).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
            if len(rows) >= args.n:
                break

    print(f"[mad_hotpotqa] loaded {len(rows)} HotpotQA samples; "
          f"agents={args.agents} rounds={args.rounds} model={RESOLVED_MODEL}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_path = out_dir / "parsed_predictions.jsonl"
    metrics_path = out_dir / "metrics.json"
    transcripts_path = out_dir / "debate_transcripts.jsonl"

    em_sum = 0.0
    f1_sum = 0.0
    token_sum = 0
    t0 = time.time()
    with pred_path.open("w", encoding="utf-8") as fp_pred, \
         transcripts_path.open("w", encoding="utf-8") as fp_trans:
        for i, row in enumerate(rows):
            try:
                res = debate_one_sample(
                    question=row["question"],
                    passages=row["context_passages"],
                    gold_answer=row["answer"],
                    agents=args.agents,
                    rounds=args.rounds,
                )
            except Exception as e:  # noqa: BLE001
                print(f"[mad_hotpotqa] sample {i} ({row.get('task_id')}) "
                      f"failed: {e}", file=sys.stderr)
                res = {
                    "prediction": "",
                    "final_answers_per_agent": [],
                    "f1": 0.0,
                    "em": 0.0,
                    "agent_transcripts": [],
                    "token_usage_proxy_chars": 0,
                }
            em_sum += res["em"]
            f1_sum += res["f1"]
            token_sum += res["token_usage_proxy_chars"]
            fp_pred.write(json.dumps({
                "task_id": row["task_id"],
                "question": row["question"],
                "answer_gold": row["answer"],
                "answer_pred": res["prediction"],
                "answer_em": res["em"],
                "answer_f1": res["f1"],
                "token_cost_proxy": res["token_usage_proxy_chars"],
            }, ensure_ascii=False) + "\n")
            fp_trans.write(json.dumps({
                "task_id": row["task_id"],
                "final_answers_per_agent": res["final_answers_per_agent"],
                "agent_transcripts": res["agent_transcripts"],
            }, ensure_ascii=False) + "\n")
            fp_pred.flush()
            fp_trans.flush()
            if (i + 1) % max(1, args.n // 10) == 0:
                elapsed = time.time() - t0
                print(f"[mad_hotpotqa] {i+1}/{len(rows)} "
                      f"partial_F1={f1_sum/(i+1):.4f} "
                      f"partial_EM={em_sum/(i+1):.4f} "
                      f"elapsed={elapsed:.0f}s", flush=True)

    wall = time.time() - t0
    metrics = {
        "host": "MAD (Du et al. 2024, llm_multiagent_debate)",
        "adapter": "external_baselines/mad/hotpotqa/gen_hotpotqa.py",
        "benchmark": "hotpotqa",
        "seed": args.seed,
        "sample_count": len(rows),
        "agents": args.agents,
        "rounds": args.rounds,
        "model": RESOLVED_MODEL,
        "answer_em": em_sum / max(1, len(rows)),
        "answer_f1": f1_sum / max(1, len(rows)),
        "mean_token_cost_proxy_chars": token_sum / max(1, len(rows)),
        "wall_s": wall,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
    }
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    print("\n=== METRICS ===")
    print(json.dumps(metrics, indent=2))
    print(f"\n[mad_hotpotqa] Wrote:")
    print(f"  {pred_path}")
    print(f"  {metrics_path}")
    print(f"  {transcripts_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
