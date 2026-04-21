"""Prep MuSiQue validation.jsonl → our canonical raw_inputs.jsonl schema.

MuSiQue native schema (per `data/musique/validation.jsonl`):
    id, question, answer, paragraphs[{idx, title, paragraph_text, is_supporting}],
    question_decomposition[{id, question, answer, paragraph_support_idx}]

Our canonical schema (per `artifacts/round2_gpt41mini_fullval/.../raw_inputs.jsonl`):
    task_id, question, answer, context_passages: list[str], supporting_facts

Design choices:
  - task_id: "musique-" + zero-padded index (e.g. musique-0000).
  - context_passages: "[<title>] <paragraph_text>" format, matching HotpotQA
    "[<title>] <text>" convention used by all our adapters (TCPB + MAD + MA-RAG + ReAgent).
  - By default we use ONLY the ``is_supporting=True`` paragraphs as gold context
    (apples-to-apples with our HotpotQA gold-context runs). Use --all-paragraphs
    to include all 20 paragraphs (closer to retrieval-free 20-paragraph setting).
  - supporting_facts: preserved as list of (title, sent_idx=0) since MuSiQue
    does not track sentence-level supporting; is_supporting is paragraph-level.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "data/musique/validation.jsonl"


def _one_sample(row: dict, idx: int, all_paragraphs: bool) -> dict:
    paras = row.get("paragraphs", [])
    if all_paragraphs:
        selected = paras
    else:
        selected = [p for p in paras if p.get("is_supporting")]
    context_passages = [
        f"[{p['title']}] {p['paragraph_text']}" for p in selected
    ]
    supporting_facts = [[p["title"], 0] for p in paras if p.get("is_supporting")]
    return {
        "task_id": f"musique-{idx:04d}",
        "_musique_id": row.get("id", ""),
        "question": row["question"],
        "answer": row.get("answer", ""),
        "context_passages": context_passages,
        "supporting_facts": supporting_facts,
        "question_decomposition": row.get("question_decomposition", []),
        "level": (
            "2hop" if row.get("id", "").startswith("2hop")
            else "3hop" if row.get("id", "").startswith("3hop")
            else "4hop" if row.get("id", "").startswith("4hop")
            else "other"
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=200,
                   help="number of samples to emit (default: 200)")
    p.add_argument("--out", required=True, help="output jsonl path")
    p.add_argument("--src", default=str(_SRC), help="MuSiQue validation.jsonl")
    p.add_argument("--all-paragraphs", action="store_true",
                   help="keep all 20 paragraphs (default: only is_supporting)")
    p.add_argument("--level-filter", default="",
                   help="optional: '2hop' / '3hop' / '4hop' / '' (any)")
    args = p.parse_args()

    rows: list[dict] = []
    with Path(args.src).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if args.level_filter:
                mid = row.get("id", "")
                if not mid.startswith(args.level_filter):
                    continue
            rows.append(row)
            if len(rows) >= args.n:
                break
    print(f"[musique_prep] loaded {len(rows)} MuSiQue samples from {args.src}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for i, row in enumerate(rows):
            conv = _one_sample(row, i, args.all_paragraphs)
            fh.write(json.dumps(conv, ensure_ascii=False) + "\n")
    print(f"[musique_prep] wrote {len(rows)} rows to {out_path}")
    print(f"[musique_prep] gold-context mode: {not args.all_paragraphs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
