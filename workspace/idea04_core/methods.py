import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any

from .contracts import AgentInput, AgentOutput, CompetenceUpdate, HandoffPacket, TraceEntry
from .llm_client import call_llm, extract_text, extract_usage

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_PROMPT_PATH = _REPO_ROOT / "prompts" / "main_agent_prompt.txt"


def _parse_prompt_sections(text: str) -> dict[str, str]:
    parts: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("<<<") and s.endswith(">>>"):
            if current is not None:
                parts[current] = "\n".join(buf).strip()
            current = s[3:-3].strip()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        parts[current] = "\n".join(buf).strip()
    if not parts and text.strip():
        return {"SHARED": text.strip()}
    return parts


@lru_cache(maxsize=1)
def _load_prompt_sections() -> dict[str, str]:
    path = _DEFAULT_PROMPT_PATH
    if not path.is_file():
        return {}
    return _parse_prompt_sections(path.read_text(encoding="utf-8"))

METHOD_NAMES = [
    "single_agent",
    "central_orchestrator",
    "central_orchestrator_with_reflection",
    "fixed_static_roles",
    "fixed_self_claim",
    "fixed_random_forward",
    "fixed_peer_calibrated",
    "fixed_self_calibrated",
]

ROLE_DESCRIPTIONS = {
    "decomposer": "You break down complex multi-hop questions into sub-questions.",
    "evidence_seeker": "You find and extract factual evidence from provided passages to answer the question.",
    "verifier": "You verify whether the collected evidence is sufficient and correct to answer the question.",
    "synthesizer": "You synthesize all evidence into a final, concise answer.",
}

# HotpotQA-oriented answer style: short span / entity / yes-no (Round1 prompt lift).
ANSWER_STYLE_BY_ROLE = {
    "decomposer": (
        "If you must answer (not forward), output one HotpotQA-style short answer: "
        "a name, place, date, number, or yes/no under 12 words. No explanation."
    ),
    "evidence_seeker": (
        "Read every evidence line. Output the minimal span that directly answers the question: "
        "prefer copying the exact entity, number, or date from the text; use yes or no only when the question is binary."
    ),
    "verifier": (
        "From the evidence only: if the question is yes/no, answer exactly yes or no. "
        "Otherwise output the single verified fact in the shortest phrase that matches the gold-answer style."
    ),
    "synthesizer": (
        "Merge all evidence into one final answer string as HotpotQA expects: "
        "short proper-noun phrase, number, date, or yes/no—no reasoning, no preamble, no quotes."
    ),
}

ACCEPT_THRESHOLD = {
    "fixed_peer_calibrated": 0.62,
    "fixed_self_calibrated": 0.55,  # slightly laxer — self-reflection is weaker signal
    "fixed_self_claim": 0.50,
    "fixed_static_roles": None,
}

# Decomposer forced-forward gate (fixed_peer_calibrated only):
# Even if decomposer self-competence >= threshold, force forward when multi-hop/multi-entity
# signals are detected in the question.  Only allow accept on clear single-hop questions.
DECOMPOSER_FORCE_FORWARD_THRESHOLD = 0.90  # competence must exceed THIS to bypass multi-hop gate

# Keywords suggesting a multi-hop or comparative question
_MULTIHOP_INDICATORS = [
    "both", "and", "as well as", "either", "neither",
    "compared", "comparison", "differ", "difference",
    "same", "which of", "are both", "were both",
    "what do", "what did",
]

# Post-sample peer competence (runner): damp oscillation on synthesizer-heavy accepts
PEER_POST_SAMPLE_MOMENTUM = 0.5
PEER_POST_SAMPLE_MAX_DELTA = 0.06

METHOD_DEFAULT_KNOBS = {
    "non_synth_evidence_cap": 14,
    "synth_evidence_cap": 60,
    "forward_evidence_cap": 8,
    "peer_update_enabled": True,
    "decomposer_force_forward_enabled": True,
    "decomposer_force_forward_threshold": DECOMPOSER_FORCE_FORWARD_THRESHOLD,
    "accept_margin": 0.02,
    "loop_penalty": 0.35,
    "star_leaf_accept_bonus": 0.55,
}


def apply_peer_post_sample_competence(prev_self: float, answer_f1: float) -> float:
    """Cross-sample self-competence for accepted_node: capped step + exponential smoothing."""
    raw = 0.06 if answer_f1 >= 0.5 else -0.10
    if raw > PEER_POST_SAMPLE_MAX_DELTA:
        raw = PEER_POST_SAMPLE_MAX_DELTA
    elif raw < -PEER_POST_SAMPLE_MAX_DELTA:
        raw = -PEER_POST_SAMPLE_MAX_DELTA
    target = max(0.05, min(0.95, prev_self + raw))
    blended = PEER_POST_SAMPLE_MOMENTUM * prev_self + (1.0 - PEER_POST_SAMPLE_MOMENTUM) * target
    return round(max(0.05, min(0.95, blended)), 3)

TASK_ROLE_MAP = {
    "who": "evidence_seeker",
    "what": "evidence_seeker",
    "where": "evidence_seeker",
    "when": "evidence_seeker",
    "how many": "evidence_seeker",
    "how much": "evidence_seeker",
    "which": "evidence_seeker",
    "are": "verifier",
    "is": "verifier",
    "were": "verifier",
    "was": "verifier",
    "did": "verifier",
    "do": "verifier",
}


def default_competence(agent_name: str) -> dict[str, float]:
    base = {
        "decomposer": 0.5,
        "evidence_seeker": 0.5,
        "verifier": 0.5,
        "synthesizer": 0.5,
    }
    if agent_name in base:
        base[agent_name] = 0.7
    return base


def default_method_knobs(method_name: str, override: dict[str, Any] | None = None) -> dict[str, Any]:
    knobs = dict(METHOD_DEFAULT_KNOBS)
    if method_name in {"fixed_static_roles", "central_orchestrator", "central_orchestrator_with_reflection"}:
        knobs["peer_update_enabled"] = False
    if method_name == "fixed_random_forward":
        knobs["decomposer_force_forward_enabled"] = False
    if override:
        knobs.update(override)
    return knobs


def _is_multihop_question(question: str) -> bool:
    """Heuristic: return True if the question shows multi-hop / multi-entity signals.

    Criteria (OR-combined):
    1. Contains one of the explicit multi-hop keyword phrases.
    2. Contains two or more capitalised proper-noun tokens (rough named-entity count >= 2)
       — a proxy for dual-entity bridge questions common in HotpotQA.
    """
    lower_q = question.lower()
    for kw in _MULTIHOP_INDICATORS:
        if kw in lower_q:
            return True
    # Count capitalised tokens (skip first token which is always capitalised)
    tokens = question.split()
    cap_count = sum(1 for t in tokens[1:] if t and t[0].isupper() and t.strip("?.,;:") != "I")
    if cap_count >= 2:
        return True
    return False


def _infer_preferred_role(question: str) -> str:
    lower_q = question.lower().strip()
    for kw, role in TASK_ROLE_MAP.items():
        if lower_q.startswith(kw):
            return role
    return "synthesizer"


def _estimate_neighbor_beliefs(
    agent_name: str,
    neighbor_list: list[str],
    competence_map: dict[str, dict[str, float]],
    packet: HandoffPacket,
) -> dict[str, float]:
    beliefs: dict[str, float] = {}
    published = packet.published_competence or {}
    for n in neighbor_list:
        beliefs[n] = round(
            float(
                published.get(
                    n,
                    competence_map.get(n, default_competence(n)).get(n, 0.5),
                )
            ),
            3,
        )
    return beliefs


def _build_routing_features(
    *,
    agent_name: str,
    question: str,
    packet: HandoffPacket,
    competence_score: float,
    threshold: float | None,
    method_knobs: dict[str, Any],
) -> dict[str, Any]:
    evidence_count = len(packet.evidence_so_far)
    preferred_role = _infer_preferred_role(question)
    is_multihop = _is_multihop_question(question)
    visited_nodes = list(packet.visited_nodes or [])
    hop_count = int(packet.hop_count or 0)
    revisit_risk = 1.0 if agent_name in visited_nodes else 0.0
    loop_risk = 1.0 if len(set(visited_nodes)) < len(visited_nodes) else 0.0
    evidence_sufficiency = min(1.0, evidence_count / 12.0)
    accept_margin = (
        round(competence_score - threshold, 3) if threshold is not None else None
    )
    topology = str(packet.published_competence.get("_topology", "")) if packet.published_competence else ""
    return {
        "agent_name": agent_name,
        "preferred_role": preferred_role,
        "question_is_multihop": is_multihop,
        "evidence_count": evidence_count,
        "evidence_sufficiency": round(evidence_sufficiency, 3),
        "packet_uncertainty": round(float(packet.uncertainty), 3),
        "hop_count": hop_count,
        "visited_nodes": visited_nodes,
        "revisit_risk": revisit_risk,
        "loop_risk": loop_risk,
        "self_competence": round(float(competence_score), 3),
        "accept_threshold": threshold,
        "accept_margin_to_threshold": accept_margin,
        "accept_margin_knob": float(method_knobs.get("accept_margin", 0.02)),
        "topology": topology,
        "is_star_leaf": topology == "star" and agent_name != "decomposer",
    }


def _score_accept(
    *,
    method_name: str,
    agent_name: str,
    routing_features: dict[str, Any],
    neighbor_list: list[str],
    method_knobs: dict[str, Any],
) -> float:
    if method_name == "single_agent":
        return 1.0
    if method_name in {"central_orchestrator", "central_orchestrator_with_reflection", "fixed_static_roles"}:
        return 1.0 if agent_name == routing_features["preferred_role"] else 0.0
    threshold = routing_features.get("accept_threshold")
    if threshold is None:
        threshold = 0.5
    score = (
        0.55 * routing_features["self_competence"]
        + 0.20 * routing_features["evidence_sufficiency"]
        + 0.10 * (1.0 - routing_features["packet_uncertainty"])
        - 0.10 * routing_features["loop_risk"]
        - 0.05 * routing_features["revisit_risk"]
    )
    if not neighbor_list:
        score += 0.05
    if method_name in {"fixed_peer_calibrated", "fixed_self_calibrated"} and agent_name == "decomposer":
        if routing_features["question_is_multihop"]:
            score -= 0.30
        if routing_features["self_competence"] < float(
            method_knobs.get("decomposer_force_forward_threshold", DECOMPOSER_FORCE_FORWARD_THRESHOLD)
        ):
            score -= 0.15
    if (
        routing_features.get("is_star_leaf")
        and agent_name == routing_features["preferred_role"]
    ):
        score += float(method_knobs.get("star_leaf_accept_bonus", 0.55))
    return round(score - threshold, 3)


def _score_neighbors(
    *,
    method_name: str,
    neighbor_list: list[str],
    preferred_role: str,
    neighbor_beliefs: dict[str, float],
    packet: HandoffPacket,
) -> list[dict[str, Any]]:
    scores: list[dict[str, Any]] = []
    if not neighbor_list:
        return scores
    for n in sorted(neighbor_list):
        self_est = float(neighbor_beliefs.get(n, 0.5))
        role_match = 1.0 if n == preferred_role else 0.0
        revisit_penalty = 0.25 if n in (packet.visited_nodes or []) else 0.0
        structural_prior = 0.05 if method_name == "fixed_peer_calibrated" else 0.0
        score = 0.60 * self_est + 0.25 * role_match + structural_prior - revisit_penalty
        scores.append(
            {
                "neighbor": n,
                "neighbor_self_belief": round(self_est, 3),
                "role_match": role_match,
                "revisit_penalty": revisit_penalty,
                "score": round(score, 3),
            }
        )
    return scores


def _pick_best_neighbor(neighbor_scores: list[dict[str, Any]], preferred: str) -> str:
    if not neighbor_scores:
        return ""
    best = sorted(
        neighbor_scores,
        key=lambda row: (float(row["score"]), 1 if row["neighbor"] == preferred else 0, row["neighbor"]),
        reverse=True,
    )[0]
    return str(best["neighbor"])


def _llm_self_reflect(
    agent_name: str,
    question: str,
    decision_taken: str,
    generated_answer: str,
    usage_accum: list[dict[str, Any]] | None = None,
) -> float:
    """Ask the agent to reflect on its own decision and return a competence delta [-0.10, +0.06].

    Used exclusively by `fixed_self_calibrated` to update self-competence without any
    peer / downstream signals.  Returns the raw delta so the caller can apply it.
    """
    system_msg = (
        f"You are the '{agent_name}' agent. You recently made the decision to '{decision_taken}' "
        f"the following question.\n"
        f"Critically assess: was this the right decision for your role?  "
        f"Reply with ONLY one word: 'optimal' if yes, or 'suboptimal' if not."
    )
    user_msg = f"Question: {question}\nYour answer/contribution: {generated_answer[:200]}\nAssessment:"
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]
    try:
        resp = call_llm(messages=messages, temperature=0.0, max_tokens=8)
        if usage_accum is not None:
            u = extract_usage(resp)
            if u:
                usage_accum.append(u)
        verdict = extract_text(resp).lower()
        # If 'optimal' → positive signal (+0.06); anything else ('suboptimal', or hedged) → negative
        return 0.06 if "optimal" in verdict and "sub" not in verdict else -0.10
    except Exception:
        return 0.0  # neutral on error — no update


def _llm_orchestrator_reflect(
    question: str,
    initial_assignment: str,
    available_roles: list[str],
    usage_accum: list[dict[str, Any]] | None = None,
) -> str:
    """Second-pass reassessment for central_orchestrator_with_reflection.

    Returns the (possibly revised) role assignment after the orchestrator reflects on
    its own initial delegation decision.  This makes the central baseline maximally strong.
    """
    system_msg = (
        "You are a central orchestrator managing a multi-agent QA system. "
        "You initially assigned a question to the role below.  "
        "Critically reflect: given the question type, is this truly the best role?  "
        f"Available roles: {', '.join(available_roles)}.  "
        "Reply with ONLY the role name — nothing else."
    )
    user_msg = (
        f"Question: {question}\n"
        f"Initial assignment: {initial_assignment}\n"
        "Your re-assessed best role:"
    )
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]
    try:
        resp = call_llm(messages=messages, temperature=0.0, max_tokens=16)
        if usage_accum is not None:
            u = extract_usage(resp)
            if u:
                usage_accum.append(u)
        candidate = extract_text(resp).lower()
        # Validate: must be a known role; fall back to initial assignment on hallucination
        for role in available_roles:
            if role in candidate:
                return role
        return initial_assignment
    except Exception:
        return initial_assignment


def _policy_decision(
    *,
    method_name: str,
    agent_name: str,
    neighbor_list: list[str],
    routing_features: dict[str, Any],
    neighbor_scores: list[dict[str, Any]],
    method_knobs: dict[str, Any],
) -> tuple[str, str]:
    """Deterministic local policy with explicit routing features and neighbor scores."""
    if method_name == "fixed_random_forward":
        if not neighbor_list:
            return "accept", "random baseline has no neighbor"
        return "forward", "random baseline always forwards when neighbors exist"

    if method_name == "single_agent":
        return "accept", "single-agent baseline always accepts"

    if not neighbor_list:
        return "accept", "terminal node with no outgoing neighbors"

    accept_score = _score_accept(
        method_name=method_name,
        agent_name=agent_name,
        routing_features=routing_features,
        neighbor_list=neighbor_list,
        method_knobs=method_knobs,
    )
    best_forward = max((float(row["score"]) for row in neighbor_scores), default=-1.0)
    margin = float(method_knobs.get("accept_margin", 0.02))

    if method_name in {"central_orchestrator", "central_orchestrator_with_reflection", "fixed_static_roles"}:
        if agent_name == routing_features["preferred_role"]:
            return "accept", f"preferred role {agent_name} matches question type"
        return "forward", f"preferred role is {routing_features['preferred_role']}"

    if method_name in {"fixed_peer_calibrated", "fixed_self_calibrated"}:
        if (
            agent_name == "decomposer"
            and bool(method_knobs.get("decomposer_force_forward_enabled", True))
            and routing_features["question_is_multihop"]
        ):
            return "forward", "decomposer multi-hop gate forces delegation"
        if (
            agent_name == "decomposer"
            and bool(method_knobs.get("decomposer_force_forward_enabled", True))
            and routing_features["self_competence"]
            < float(method_knobs.get("decomposer_force_forward_threshold", DECOMPOSER_FORCE_FORWARD_THRESHOLD))
        ):
            return "forward", "decomposer competence below bypass threshold"

    if accept_score >= best_forward + margin:
        return "accept", f"accept_score={accept_score:.3f} beats best_forward={best_forward:.3f}"
    return "forward", f"best_forward={best_forward:.3f} exceeds accept_score={accept_score:.3f}"


def _llm_generate_answer(
    agent_name: str,
    question: str,
    evidence_so_far: list[str],
    evidence_cap: int | None = None,
    usage_accum: list[dict[str, Any]] | None = None,
) -> str:
    if evidence_cap is None:
        evidence_cap = 60 if agent_name == "synthesizer" else 14
    if agent_name == "synthesizer":
        ev_slice = evidence_so_far[-evidence_cap:] if len(evidence_so_far) > evidence_cap else list(evidence_so_far)
    else:
        ev_slice = evidence_so_far[:evidence_cap]
    evidence_text = "\n".join(ev_slice) if ev_slice else "None."
    sections = _load_prompt_sections()
    shared = sections.get("SHARED", "").strip()
    role_block = sections.get(agent_name, "").strip()
    style = ANSWER_STYLE_BY_ROLE.get(
        agent_name,
        "Using ONLY the evidence, output the shortest correct answer. No explanation.",
    )
    spec_parts = [
        f"You are the '{agent_name}' agent. {ROLE_DESCRIPTIONS.get(agent_name, '')}",
    ]
    if shared:
        spec_parts.append(shared)
    if role_block:
        spec_parts.append(role_block)
    else:
        spec_parts.append(style)
    spec_parts.append("Rules: use ONLY the given evidence; output a single line with no 'Answer:' prefix.")
    system_content = "\n\n".join(spec_parts)
    ev_label = (
        "Evidence (full packet, earliest passages first, then hop contributions — read all lines)"
        if agent_name == "synthesizer"
        else "Evidence"
    )
    messages = [
        {
            "role": "system",
            "content": system_content,
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\n{ev_label}:\n{evidence_text}\n\nYour single-line answer:",
        },
    ]
    try:
        _max_tok = 256 if agent_name == "synthesizer" else 128
        resp = call_llm(messages=messages, temperature=0.0, max_tokens=_max_tok)
        if usage_accum is not None:
            u = extract_usage(resp)
            if u:
                usage_accum.append(u)
        raw_text = extract_text(resp)
        # Strip CoT scaffolding emitted by synthesizer two-stage prompt:
        # e.g. "Key facts: ...\nAnswer: Paris" → "Paris"
        # Also handles cases where model outputs just "Answer: Paris"
        lines = raw_text.splitlines()
        answer_lines = [ln for ln in lines if ln.lower().startswith("answer:")]
        if answer_lines:
            raw_text = answer_lines[-1][len("answer:"):].strip().strip('"').strip("'")
        elif any(ln.lower().startswith("key facts:") for ln in lines):
            # CoT emitted key facts but no "Answer:" line — take the last non-empty line
            non_empty = [ln.strip() for ln in lines if ln.strip() and not ln.lower().startswith("key facts:")]
            raw_text = non_empty[-1] if non_empty else raw_text
        return raw_text
    except Exception as exc:
        return f"[ERROR: {exc}]"


def _llm_forward_contribution(
    agent_name: str,
    question: str,
    evidence_so_far: list[str],
    evidence_cap: int | None = None,
    usage_accum: list[dict[str, Any]] | None = None,
) -> str:
    if evidence_cap is None:
        evidence_cap = 8
    evidence_text = "\n".join(evidence_so_far[:evidence_cap]) if evidence_so_far else "None."
    sections = _load_prompt_sections()
    shared = sections.get("SHARED", "").strip()
    fwd = sections.get("forward_contribution", "").strip()
    forward_rules = (
        fwd
        if fwd
        else (
            "You are forwarding this task to the next agent. "
            "Extract one key piece of evidence or insight from the passages to add to the packet. "
            "Output one sentence only."
        )
    )
    fc_parts = [
        f"You are the '{agent_name}' agent. {ROLE_DESCRIPTIONS.get(agent_name, '')}",
    ]
    if shared:
        fc_parts.append(shared)
    fc_parts.append(forward_rules)
    messages = [
        {
            "role": "system",
            "content": "\n\n".join(fc_parts).strip(),
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nPassages:\n{evidence_text}\n\nKey insight:",
        },
    ]
    try:
        resp = call_llm(messages=messages, temperature=0.0, max_tokens=60)
        if usage_accum is not None:
            u = extract_usage(resp)
            if u:
                usage_accum.append(u)
        return extract_text(resp)
    except Exception:
        return ""


def _competence_update_self_calibrated(
    before: dict[str, float],
    agent_name: str,
    delta: float,
) -> CompetenceUpdate:
    """Apply `delta` from LLM self-reflection to agent's own skill entry."""
    after = dict(before)
    bounded = max(0.05, min(0.95, after.get(agent_name, 0.5) + delta))
    after[agent_name] = round(bounded, 3)
    signal = "self_positive" if delta > 0 else "self_negative"
    return CompetenceUpdate(before=before, after=after, signal=signal)


def run_method_step(
    agent_name: str,
    agent_input: AgentInput,
    hop_index: int,
    gold_answer: str = "",
    answer_f1_feedback: float = -1.0,
) -> AgentOutput:
    method_name = agent_input.method_state.method_name
    if method_name not in METHOD_NAMES:
        raise ValueError(f"Unsupported method: {method_name}")

    usage_accum: list[dict[str, Any]] = []

    packet = agent_input.incoming_packet
    competence_map = agent_input.method_state.competence_by_agent
    method_knobs = default_method_knobs(
        method_name,
        agent_input.method_state.method_knobs,
    )
    before = dict(competence_map.get(agent_name, default_competence(agent_name)))
    neighbor_list = agent_input.neighbor_list
    question = agent_input.question

    # Competence score used for policy decision
    competence_score = before.get(agent_name, 0.5)
    threshold = ACCEPT_THRESHOLD.get(method_name)
    neighbor_beliefs = _estimate_neighbor_beliefs(
        agent_name=agent_name,
        neighbor_list=neighbor_list,
        competence_map=competence_map,
        packet=packet,
    )
    routing_features = _build_routing_features(
        agent_name=agent_name,
        question=question,
        packet=packet,
        competence_score=competence_score,
        threshold=threshold,
        method_knobs=method_knobs,
    )
    neighbor_scores = _score_neighbors(
        method_name=method_name,
        neighbor_list=neighbor_list,
        preferred_role=routing_features["preferred_role"],
        neighbor_beliefs=neighbor_beliefs,
        packet=packet,
    )

    # ── central_orchestrator_with_reflection ──────────────────────────────────
    # For CO+Reflection we call a two-stage routing: first the fast heuristic,
    # then an LLM second-pass that may revise the assignment.
    if method_name == "central_orchestrator_with_reflection":
        heuristic_preferred = _infer_preferred_role(question)
        initial_decision = "accept" if agent_name == heuristic_preferred else "forward"

        if initial_decision == "forward":
            # Let LLM reflect on the delegation: it might change the target role
            all_roles = list(neighbor_list) + [agent_name]
            reflected_role = _llm_orchestrator_reflect(question, heuristic_preferred, all_roles, usage_accum)
            # If reflected role is this agent itself → override to accept
            if reflected_role == agent_name:
                decision = "accept"
            else:
                decision = "forward"
                heuristic_preferred = reflected_role  # update target for pick_best_neighbor
        else:
            decision = "accept"

        if decision == "accept":
            chosen_target = ""
            llm_answer = _llm_generate_answer(
                agent_name,
                question,
                packet.evidence_so_far,
                evidence_cap=int(
                    method_knobs["synth_evidence_cap"]
                    if agent_name == "synthesizer"
                    else method_knobs["non_synth_evidence_cap"]
                ),
                usage_accum=usage_accum,
            )
            raw_response = llm_answer
            reason = f"{method_name}: reflected assignment={agent_name}, accepting"
            contribution = ""
        else:
            chosen_target = _pick_best_neighbor(neighbor_scores, heuristic_preferred)
            contribution = _llm_forward_contribution(
                agent_name,
                question,
                packet.evidence_so_far,
                evidence_cap=int(method_knobs["forward_evidence_cap"]),
                usage_accum=usage_accum,
            )
            reason = (
                f"{method_name}: reflected assignment={heuristic_preferred}, "
                f"forwarding to {chosen_target}"
            )
            llm_answer = ""
            raw_response = f"[forward to {chosen_target}] {contribution}"

        new_evidence = list(packet.evidence_so_far)
        if contribution:
            new_evidence.append(f"[{agent_name}] {contribution}")

        outgoing = HandoffPacket(
            task_id=packet.task_id,
            question=packet.question,
            current_subgoal=f"{agent_name}_step_{hop_index}",
            evidence_so_far=new_evidence,
            uncertainty=round(
                max(0.0, packet.uncertainty - 0.08 if decision == "accept" else packet.uncertainty + 0.02), 3
            ),
            reason_for_forward=reason if decision == "forward" else "",
            recommended_next_skill=chosen_target if decision == "forward" else agent_name,
            visited_nodes=list(packet.visited_nodes) + [agent_name],
            hop_count=hop_index + 1,
            last_actor=agent_name,
            candidate_answer=llm_answer if decision == "accept" else "",
            published_competence={
                "_topology": routing_features.get("topology", ""),
                agent_name: round(float(before.get(agent_name, 0.5)), 3),
            },
        )
        competence_update = CompetenceUpdate(before=before, after=dict(before), signal="no_update")
        trace = TraceEntry(
            task_id=agent_input.task_id,
            hop_index=hop_index,
            node_name=agent_name,
            decision=decision,
            chosen_target=chosen_target,
            reason=reason,
            routing_features=routing_features,
            neighbor_scores=neighbor_scores,
        )
        return AgentOutput(
            decision=decision,
            outgoing_packet=outgoing,
            raw_response=raw_response,
            competence_update=competence_update,
            trace=trace,
            generated_answer=llm_answer,
            usage_calls=list(usage_accum),
        )

    # Hard-gate policy decision (no LLM for all other methods)
    decision, policy_reason = _policy_decision(
        method_name=method_name,
        agent_name=agent_name,
        neighbor_list=neighbor_list,
        routing_features=routing_features,
        neighbor_scores=neighbor_scores,
        method_knobs=method_knobs,
    )

    if method_name == "fixed_random_forward":
        if decision == "forward":
            rng = random.Random(f"{agent_input.task_id}-{agent_name}-{hop_index}")
            chosen_target = rng.choice(neighbor_list)
            reason = policy_reason
            llm_answer = ""
            raw_response = f"[random_forward] -> {chosen_target}"
            contribution = ""
        else:
            chosen_target = ""
            reason = policy_reason
            llm_answer = _llm_generate_answer(
                agent_name,
                question,
                packet.evidence_so_far,
                evidence_cap=int(
                    method_knobs["synth_evidence_cap"]
                    if agent_name == "synthesizer"
                    else method_knobs["non_synth_evidence_cap"]
                ),
                usage_accum=usage_accum,
            )
            raw_response = llm_answer
            contribution = ""
    elif decision == "accept":
        chosen_target = ""
        llm_answer = _llm_generate_answer(
            agent_name,
            question,
            packet.evidence_so_far,
            evidence_cap=int(
                method_knobs["synth_evidence_cap"]
                if agent_name == "synthesizer"
                else method_knobs["non_synth_evidence_cap"]
            ),
            usage_accum=usage_accum,
        )
        raw_response = llm_answer
        reason = f"{method_name}: {policy_reason}"
        contribution = ""
    else:
        preferred = routing_features["preferred_role"]
        chosen_target = _pick_best_neighbor(neighbor_scores, preferred)
        contribution = _llm_forward_contribution(
            agent_name,
            question,
            packet.evidence_so_far,
            evidence_cap=int(method_knobs["forward_evidence_cap"]),
            usage_accum=usage_accum,
        )
        reason = f"{method_name}: {policy_reason}; forwarding to {chosen_target}"
        llm_answer = ""
        raw_response = f"[forward to {chosen_target}] {contribution}"

    new_evidence = list(packet.evidence_so_far)
    if contribution:
        new_evidence.append(f"[{agent_name}] {contribution}")

    outgoing = HandoffPacket(
        task_id=packet.task_id,
        question=packet.question,
        current_subgoal=f"{agent_name}_step_{hop_index}",
        evidence_so_far=new_evidence,
        uncertainty=round(
            max(0.0, packet.uncertainty - 0.08 if decision == "accept" else packet.uncertainty + 0.02), 3
        ),
        reason_for_forward=reason if decision == "forward" else "",
        recommended_next_skill=chosen_target if decision == "forward" else agent_name,
        visited_nodes=list(packet.visited_nodes) + [agent_name],
        hop_count=hop_index + 1,
        last_actor=agent_name,
        candidate_answer=llm_answer if decision == "accept" else "",
        published_competence={
            "_topology": routing_features.get("topology", ""),
            agent_name: round(float(before.get(agent_name, 0.5)), 3),
        },
    )

    # ── Competence update logic ──────────────────────────────────────────────
    if method_name == "fixed_self_calibrated":
        # Self-reflection signal: agent introspects on its own decision
        verbose_answer = llm_answer if llm_answer else contribution
        self_delta = _llm_self_reflect(
            agent_name=agent_name,
            question=question,
            decision_taken=decision,
            generated_answer=verbose_answer,
            usage_accum=usage_accum,
        )
        competence_update = _competence_update_self_calibrated(
            before=before,
            agent_name=agent_name,
            delta=self_delta,
        )
    else:
        competence_update = CompetenceUpdate(before=before, after=dict(before), signal="no_update")

    trace = TraceEntry(
        task_id=agent_input.task_id,
        hop_index=hop_index,
        node_name=agent_name,
        decision=decision,
        chosen_target=chosen_target,
        reason=reason,
        routing_features=routing_features,
        neighbor_scores=neighbor_scores,
    )

    return AgentOutput(
        decision=decision,
        outgoing_packet=outgoing,
        raw_response=raw_response,
        competence_update=competence_update,
        trace=trace,
        generated_answer=llm_answer,
        usage_calls=list(usage_accum),
    )
