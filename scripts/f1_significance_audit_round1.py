#!/usr/bin/env python3
"""
F1 显著性卡点 — 四项底层自查（run_20260411_102202 peer vs static）。

用法（仓库根目录）:
  python scripts/f1_significance_audit_round1.py

依赖: 仅标准库 + 将 workspace 加入 path 以复用 evaluation / methods。
"""
from __future__ import annotations

import json
import random
import re
import string
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from idea04_core.evaluation import token_f1  # noqa: E402
from idea04_core.methods import _is_multihop_question  # noqa: E402


RUN = ROOT / "artifacts" / "round1" / "run_20260411_102202"
PEER = RUN / "fixed_peer_calibrated"
STATIC = RUN / "fixed_static_roles"


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def gold_in_evidence(gold: str, evidence_lines: list[str]) -> bool:
    """Heuristic: gold (normalized) appears as substring in joint evidence, or high token recall in evidence."""
    g = _normalize(gold)
    if not g:
        return False
    blob = _normalize("\n".join(evidence_lines))
    if len(g) >= 3 and g in blob:
        return True
    gt = g.split()
    if not gt:
        return False
    bt = blob.split()
    if not bt:
        return False
    common = Counter(gt) & Counter(bt)
    recall = sum(common.values()) / len(gt)
    return recall >= 0.85


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def last_packet_by_task(packets: list[dict]) -> dict[str, dict]:
    """Per task_id, keep packet with largest hop index (numeric only)."""
    best: dict[str, tuple[int, dict]] = {}
    for p in packets:
        tid = p["task_id"]
        sub = p.get("current_subgoal", "")
        hop = -1
        m = re.search(r"_step_(\d+)$", sub)
        if m:
            hop = int(m.group(1))
        if tid not in best or hop > best[tid][0]:
            best[tid] = (hop, p)
    return {k: v[1] for k, v in best.items()}


def audit1_synthesizer_black_hole() -> dict:
    preds = {p["task_id"]: p for p in read_jsonl(PEER / "parsed_predictions.jsonl")}
    packets = read_jsonl(PEER / "handoff_packets.jsonl")
    lastp = last_packet_by_task(packets)

    def collect(min_hops: int, synth_only: bool) -> list[dict]:
        hits = []
        for tid, pr in preds.items():
            if pr.get("answer_f1", 1.0) >= 0.2:
                continue
            hc = int(pr.get("hop_count", 0))
            if hc < min_hops:
                continue
            if synth_only and pr.get("accepted_node") != "synthesizer":
                continue
            p = lastp.get(tid)
            if not p:
                continue
            ev = p.get("evidence_so_far") or []
            if not gold_in_evidence(pr.get("gold_answer", ""), ev):
                continue
            hits.append(
                {
                    "task_id": tid,
                    "hop_count": hc,
                    "accepted_node": pr.get("accepted_node"),
                    "answer_f1": pr.get("answer_f1"),
                    "gold": (pr.get("gold_answer") or "")[:80],
                    "final": (pr.get("final_answer") or "")[:80],
                    "n_evidence_lines": len(ev),
                    "chars_total_evidence": sum(len(x) for x in ev),
                }
            )
        return hits

    strict = collect(min_hops=3, synth_only=False)
    synth_ge2 = collect(min_hops=2, synth_only=True)
    any_ge2 = collect(min_hops=2, synth_only=False)
    return {
        "tier_A": "hop_count>=3, answer_f1<0.2, gold_in_evidence",
        "tier_A_count": len(strict),
        "tier_A_samples": strict[:15],
        "tier_B": "hop_count>=2, accepted_node=synthesizer, answer_f1<0.2, gold_in_evidence",
        "tier_B_count": len(synth_ge2),
        "tier_B_samples": synth_ge2[:15],
        "tier_C": "hop_count>=2, answer_f1<0.2, gold_in_evidence (any acceptor)",
        "tier_C_count": len(any_ge2),
        "tier_C_samples": any_ge2[:15],
    }


def audit2_route_homogeneity() -> dict:
    peer = {p["task_id"]: p for p in read_jsonl(PEER / "parsed_predictions.jsonl")}
    static = {p["task_id"]: p for p in read_jsonl(STATIC / "parsed_predictions.jsonl")}
    common = set(peer) & set(static)
    same_both = 0
    same_acceptor = 0
    same_hops = 0
    for tid in sorted(common):
        a, b = peer[tid], static[tid]
        if a["accepted_node"] == b["accepted_node"] and a["hop_count"] == b["hop_count"]:
            same_both += 1
        if a["accepted_node"] == b["accepted_node"]:
            same_acceptor += 1
        if a["hop_count"] == b["hop_count"]:
            same_hops += 1
    n = len(common)
    return {
        "n": n,
        "same_acceptor_and_hops": same_both,
        "pct_same_both": round(100 * same_both / n, 2) if n else 0,
        "same_acceptor_only": same_acceptor,
        "pct_same_acceptor": round(100 * same_acceptor / n, 2) if n else 0,
        "same_hops_only": same_hops,
        "pct_same_hops": round(100 * same_hops / n, 2) if n else 0,
    }


def audit3_peer_negative_signal() -> dict:
    """post_sample peer_negative = gold F1<0.5 penalty on acceptor — not per-hop LLM s_peer."""
    snaps = read_jsonl(PEER / "competence_snapshots.jsonl")
    neg = [s for s in snaps if s.get("hop_index") == "post_sample" and s.get("update", {}).get("signal") == "peer_negative"]
    pos = [s for s in snaps if s.get("hop_index") == "post_sample" and s.get("update", {}).get("signal") == "peer_positive"]
    preds = {p["task_id"]: p for p in read_jsonl(PEER / "parsed_predictions.jsonl")}
    # Sample up to 20 negatives with gold-in-evidence check (last packet)
    packets = read_jsonl(PEER / "handoff_packets.jsonl")
    lastp = last_packet_by_task(packets)
    sample = neg[:]
    random.seed(42)
    random.shuffle(sample)
    sample = sample[:20]
    rows = []
    for s in sample:
        tid = s["task_id"]
        pr = preds.get(tid, {})
        ev = (lastp.get(tid) or {}).get("evidence_so_far") or []
        gin = gold_in_evidence(pr.get("gold_answer", ""), ev)
        rows.append(
            {
                "task_id": tid,
                "acceptor": s.get("node_name"),
                "parsed_accepted": pr.get("accepted_node"),
                "answer_f1": pr.get("answer_f1"),
                "gold_in_evidence": gin,
            }
        )
    return {
        "implementation_note": "No per-hop LLM peer score; peer_negative is post-sample rule from gold answer F1<0.5 (runner/methods).",
        "post_sample_peer_negative_count": len(neg),
        "post_sample_peer_positive_count": len(pos),
        "sampled_20_for_table": rows,
    }


def audit4_static_wins_peer_decomposer() -> dict:
    peer = {p["task_id"]: p for p in read_jsonl(PEER / "parsed_predictions.jsonl")}
    static = {p["task_id"]: p for p in read_jsonl(STATIC / "parsed_predictions.jsonl")}
    traces = read_jsonl(PEER / "routing_traces.jsonl")
    by_task: dict[str, list[dict]] = {}
    for t in traces:
        by_task.setdefault(t["task_id"], []).append(t)
    for tid in by_task:
        by_task[tid].sort(key=lambda x: x["hop_index"])

    losers = []
    for tid in sorted(set(peer) & set(static)):
        pf, sf = peer[tid].get("answer_f1", 0), static[tid].get("answer_f1", 0)
        if sf > pf + 1e-6:
            losers.append(tid)

    details = []
    for tid in losers:
        pr = peer[tid]
        q = pr.get("question", "")
        multihop = _is_multihop_question(q)
        hops = by_task.get(tid, [])
        first = hops[0] if hops else {}
        first_decision = first.get("decision", "")
        first_node = first.get("node_name", "")
        # decomposer forced forward: first hop decomposer + forward
        forced_fwd = (
            first_node == "decomposer"
            and first_decision == "forward"
            and multihop is False
        )
        details.append(
            {
                "task_id": tid,
                "peer_f1": pr.get("answer_f1"),
                "static_f1": static[tid].get("answer_f1"),
                "_is_multihop_question": multihop,
                "hop0_decision": first_decision,
                "hop0_target": first.get("chosen_target", ""),
                "singlehop_but_decomposer_forwarded": forced_fwd,
                "peer_hop_count": pr.get("hop_count"),
                "static_hop_count": static[tid].get("hop_count"),
                "question_prefix": q[:100],
            }
        )
    forced_count = sum(1 for d in details if d["singlehop_but_decomposer_forwarded"])
    return {
        "static_f1_gt_peer_f1_count": len(losers),
        "task_ids": losers,
        "among_these_singlehop_decomposer_forwarded": forced_count,
        "details": details,
    }


def main() -> None:
    if not PEER.is_dir():
        print("Missing peer run dir:", PEER, file=sys.stderr)
        sys.exit(1)
    out = {
        "run": str(PEER),
        "audit1_terminus_black_hole": audit1_synthesizer_black_hole(),
        "audit2_route_homogeneity": audit2_route_homogeneity(),
        "audit3_peer_signal_clarification": audit3_peer_negative_signal(),
        "audit4_static_beats_peer_decomposer": audit4_static_wins_peer_decomposer(),
        "code_facts": {
            "synthesizer_evidence_llm_input": "last 60 lines of evidence_so_far (methods._llm_generate_answer)",
            "other_roles_evidence_cap": "first 14 lines",
            "synthesizer_max_tokens": 256,
            "peer_competence_update": "post_sample only from gold answer F1>=0.5 (+) or <0.5 (-); hop snapshots mostly no_update",
        },
    }
    report_path = ROOT / "artifacts" / "round1" / "f1_significance_audit_run_20260411_102202.json"
    report_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
