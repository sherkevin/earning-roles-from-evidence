import csv
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]

from .contracts import AgentInput, HandoffPacket, MethodState
from .evaluation import exact_match, token_f1
from .llm_client import ModelDriftError, _runtime as _llm_runtime, configure_runtime, resolved_model

# Stage-2 (E-005). Imports are top-level but only exercised when
# method_name == "edo_stage2_chain"; Stage-1 paths never touch these symbols.
from .persona_model import BeliefStore, serialize_v2 as serialize_belief_v2
from .task_tree import TaskNode, TaskTreeState


def _runtime_backend() -> str:
    return _llm_runtime.get("backend", "unknown")
from .methods import (
    METHOD_NAMES,
    apply_peer_post_sample_competence,
    default_method_knobs,
    default_competence,
    run_method_step,
)

# Methods that carry persistent competence state across samples.
_STATEFUL_METHODS = frozenset({"fixed_peer_calibrated", "fixed_self_calibrated"})


@dataclass
class _SampleResult:
    prediction: dict[str, Any]
    traces: list[dict[str, Any]]
    packets: list[dict[str, Any]]
    snaps: list[dict[str, Any]]
    raw_outputs: list[dict[str, Any]]
    is_premature_accept: bool
    is_dead_end: bool
    is_correction_forward: bool
    handoffs: list[int]
    token_cost: int
    api_prompt: int
    api_completion: int
    api_total: int
    # ── Stage-2 only (empty list for Stage-1 methods) ──
    task_tree_records: list[dict[str, Any]] = field(default_factory=list)
    audit_event_records: list[dict[str, Any]] = field(default_factory=list)
    belief_snapshot_records: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class _Counters:
    """Thread-safe accumulator protected by its own lock."""
    lock: threading.Lock = field(default_factory=threading.Lock)
    predictions: list[dict[str, Any]] = field(default_factory=list)
    dead_end: int = 0
    premature_accept: int = 0
    correction_forward: int = 0
    handoffs: list[int] = field(default_factory=list)
    token_costs: list[int] = field(default_factory=list)
    api_prompt: list[int] = field(default_factory=list)
    api_completion: list[int] = field(default_factory=list)
    api_total: list[int] = field(default_factory=list)


class RoundRunner:
    def __init__(self, topology: str, max_handoff: int) -> None:
        if topology not in {"chain", "star"}:
            raise ValueError(f"Unsupported topology: {topology}")
        self.topology = topology
        self.max_handoff = max_handoff
        self.adjacency = self._build_adjacency(topology=topology)
        self.nodes = list(self.adjacency.keys())

    @staticmethod
    def _build_adjacency(topology: str) -> dict[str, list[str]]:
        if topology == "chain":
            return {
                "decomposer": ["evidence_seeker"],
                "evidence_seeker": ["verifier"],
                "verifier": ["synthesizer"],
                "synthesizer": [],
            }
        return {
            "decomposer": ["evidence_seeker", "verifier", "synthesizer"],
            "evidence_seeker": ["decomposer"],
            "verifier": ["decomposer"],
            "synthesizer": ["decomposer"],
        }

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(
        self,
        method_name: str,
        samples: list[dict[str, Any]],
        run_config: dict[str, Any],
        run_dir: Path,
    ) -> dict[str, Any]:
        if method_name not in METHOD_NAMES:
            raise ValueError(f"Unsupported method: {method_name}")
        run_dir.mkdir(parents=True, exist_ok=True)

        # Wire the LLM backbone from run_config["main_model"].
        # configure_runtime() selects provider (zhipu / oversea / gptplus5 / nvidia) via
        # llm_providers + configs/llm.json.  It raises RuntimeError immediately
        # if LLM_MODEL env var would silently redirect to a different backbone.
        main_model = run_config.get("main_model") or "glm-4-flash"
        configure_runtime(main_model)
        print(
            f"[runner] runtime contract: intended={main_model!r} "
            f"resolved={resolved_model()!r} backend={_runtime_backend()}",
            flush=True,
        )

        n_workers      = int(run_config.get("n_workers", 1))
        progress_every = int(run_config.get("progress_every", 50) or 50)

        # ----------------------------------------------------------------
        # Checkpoint detection
        # _ckpt_preds.jsonl  →  one JSON line per completed sample.
        # Resume if that file exists but metrics.json does NOT.
        # ----------------------------------------------------------------
        ckpt_path  = run_dir / "_ckpt_preds.jsonl"
        is_resume  = ckpt_path.exists() and not (run_dir / "metrics.json").exists()

        completed_predictions: list[dict[str, Any]] = []
        completed_ids: set[str] = set()

        if is_resume:
            with ckpt_path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        p = json.loads(line)
                        completed_predictions.append(p)
                        completed_ids.add(p["task_id"])
            print(
                f"[runner] {method_name}: checkpoint found — "
                f"{len(completed_ids)} done, "
                f"{len(samples) - len(completed_ids)} remaining",
                flush=True,
            )

        # ----------------------------------------------------------------
        # Persistent competence (stateful methods only).
        # On resume, replay competence updates in original sample order.
        # ----------------------------------------------------------------
        persistent_competence: dict[str, dict[str, float]] = {
            node: default_competence(node) for node in self.nodes
        }
        if is_resume and method_name in _STATEFUL_METHODS:
            id_to_idx = {s["task_id"]: i for i, s in enumerate(samples)}
            for p in sorted(
                completed_predictions,
                key=lambda x: id_to_idx.get(x["task_id"], len(samples)),
            ):
                self._replay_competence(
                    method_name, p["accepted_node"], p["answer_f1"],
                    persistent_competence,
                )

        competence_lock = threading.Lock()
        write_lock      = threading.Lock()

        # ----------------------------------------------------------------
        # Open incremental JSONL log files
        # ----------------------------------------------------------------
        log_mode  = "a" if is_resume else "w"
        f_traces  = (run_dir / "routing_traces.jsonl").open(log_mode, encoding="utf-8")
        f_packets = (run_dir / "handoff_packets.jsonl").open(log_mode, encoding="utf-8")
        f_snaps   = (run_dir / "competence_snapshots.jsonl").open(log_mode, encoding="utf-8")
        f_outputs = (run_dir / "raw_model_outputs.jsonl").open(log_mode, encoding="utf-8")
        f_ckpt    = ckpt_path.open("a", encoding="utf-8")   # always append

        # ── Stage-2 only: 3 additional jsonls (per pinned C-2 these are gated
        # by method_name so Stage-1 runs never see them on disk) ──────────────
        is_stage2 = method_name == "edo_stage2_chain"
        f_task_tree   = (run_dir / "task_tree.jsonl").open(log_mode, encoding="utf-8") if is_stage2 else None
        f_audit_evts  = (run_dir / "audit_events.jsonl").open(log_mode, encoding="utf-8") if is_stage2 else None
        f_belief_snap = (run_dir / "neighbor_belief_snapshots.jsonl").open(log_mode, encoding="utf-8") if is_stage2 else None

        counters   = _Counters()
        id_to_orig = {s["task_id"]: i for i, s in enumerate(samples)}

        # ----------------------------------------------------------------
        # Core per-sample function (pure, no shared-state writes)
        # ----------------------------------------------------------------
        def _process_one(sample: dict[str, Any]) -> _SampleResult:
            task_id     = sample["task_id"]
            question    = sample["question"]
            gold_answer = sample.get("answer", "")

            # Snapshot competence under lock (read only)
            with competence_lock:
                if method_name in _STATEFUL_METHODS:
                    init_comp = {k: dict(v) for k, v in persistent_competence.items()}
                else:
                    init_comp = {node: default_competence(node) for node in self.nodes}

            state = MethodState(
                method_name=method_name,
                topology=self.topology,
                max_handoff=self.max_handoff,
                competence_by_agent=init_comp,
                neighbor_beliefs_by_agent={},
                method_knobs=default_method_knobs(
                    method_name, run_config.get("method_knobs")
                ),
                seen_nodes=set(),
            )

            # Stage-2 only: per-sample TaskTreeState + per-agent BeliefStore
            if is_stage2:
                root_node = TaskNode(
                    task_id=f"{task_id}_root",
                    parent_task_id=None,
                    root_task_id=f"{task_id}_root",
                    task_text=question,
                    task_type_guess="composite",
                    depth=0,
                    owner_agent="decomposer",
                    executor_agent="decomposer",
                )
                state.task_tree_state_v2 = TaskTreeState(root_node)
                state.belief_store_by_agent_v2 = {n: BeliefStore() for n in self.nodes}

            packet = HandoffPacket(
                task_id=task_id,
                question=question,
                current_subgoal="decompose_question",
                evidence_so_far=sample.get("context_passages", []),
                uncertainty=0.6,
                reason_for_forward="",
                recommended_next_skill="decomposer",
                visited_nodes=[],
                hop_count=0,
                last_actor="",
                candidate_answer="",
                published_competence={"_topology": self.topology},
            )

            node               = "decomposer"
            termination_reason = "accepted"
            accepted_node      = ""
            final_answer       = ""
            hop_count          = 0

            sample_traces:  list[dict[str, Any]] = []
            sample_packets: list[dict[str, Any]] = []
            sample_raw_out: list[dict[str, Any]] = []
            sample_snaps:   list[dict[str, Any]] = []

            is_premature  = False
            is_dead_end   = False
            is_correction = False
            handoff_idxs: list[int] = []

            for hop_index in range(self.max_handoff + 1):
                state.seen_nodes.add(node)

                model_input = AgentInput(
                    task_id=task_id,
                    question=question,
                    incoming_packet=packet,
                    local_state={"self_claim": state.competence_by_agent[node].get(node, 0.5)},
                    neighbor_list=self.adjacency[node],
                    method_state=state,
                )

                # All LLM calls happen here — no locks held
                output = run_method_step(
                    agent_name=node,
                    agent_input=model_input,
                    hop_index=hop_index,
                    gold_answer=gold_answer,
                    answer_f1_feedback=-1.0,
                )

                sample_traces.append(output.trace.to_dict())
                sample_packets.append(output.outgoing_packet.to_dict())
                sample_raw_out.append({
                    "task_id": task_id,
                    "hop_index": hop_index,
                    "node_name": node,
                    "raw_response": output.raw_response,
                    "generated_answer": output.generated_answer,
                    "usage_calls": output.usage_calls,
                    "runtime_model": resolved_model(),
                })
                sample_snaps.append({
                    "task_id": task_id,
                    "hop_index": hop_index,
                    "node_name": node,
                    "update": output.competence_update.to_dict(),
                    "competence_after": dict(state.competence_by_agent[node]),
                })

                state.competence_by_agent[node] = output.competence_update.after
                state.neighbor_beliefs_by_agent[node] = dict(
                    output.outgoing_packet.published_competence
                )
                packet    = output.outgoing_packet
                hop_count = hop_index + 1

                if output.decision == "accept":
                    accepted_node = node
                    final_answer  = output.generated_answer
                    if (
                        node not in ("synthesizer",)
                        and hop_index == 0
                        and method_name not in ("single_agent", "central_orchestrator")
                    ):
                        is_premature = True
                    break

                handoff_idxs.append(hop_index + 1)
                next_node = output.trace.chosen_target

                if not next_node:
                    is_dead_end        = True
                    termination_reason = "dead_end"
                    accepted_node      = node
                    final_answer       = output.generated_answer
                    break

                if next_node not in self.adjacency[node]:
                    is_dead_end        = True
                    termination_reason = "topology_violation"
                    accepted_node      = node
                    final_answer       = output.generated_answer
                    break

                if next_node in state.seen_nodes and next_node != "synthesizer":
                    is_correction      = True
                    next_node          = "synthesizer"
                    termination_reason = "loop_protected_to_synthesizer"

                node = next_node

                if hop_index >= self.max_handoff:
                    is_dead_end        = True
                    termination_reason = "max_handoff_reached"
                    accepted_node      = "synthesizer"
                    break

            # self_calibrated: post-sample competence snapshot
            if method_name == "fixed_self_calibrated" and accepted_node in self.nodes:
                snap_comp = dict(state.competence_by_agent.get(accepted_node, {}))
                sample_snaps.append({
                    "task_id": task_id,
                    "hop_index": "post_sample",
                    "node_name": accepted_node,
                    "update": {"before": snap_comp, "after": snap_comp, "signal": "self_sync"},
                    "competence_after": snap_comp,
                })

            em = exact_match(final_answer, gold_answer)
            f1 = token_f1(final_answer, gold_answer)
            token_cost = 120 + hop_count * 180

            sp = sc = st = 0
            for ro in sample_raw_out:
                for u in ro.get("usage_calls") or []:
                    if not isinstance(u, dict):
                        continue
                    sp += int(u.get("prompt_tokens") or 0)
                    sc += int(u.get("completion_tokens") or 0)
                    tt  = u.get("total_tokens")
                    st += int(tt) if tt is not None else sp + sc

            prediction = {
                "task_id": task_id,
                "question": question,
                "gold_answer": gold_answer,
                "final_answer": final_answer,
                "accepted_node": accepted_node,
                "hop_count": hop_count,
                "answer_em": em,
                "answer_f1": f1,
                "termination_reason": termination_reason,
                "token_cost": token_cost,
            }

            # ── Stage-2 per-sample artefacts: snapshot tree + audit events + beliefs ──
            stage2_tree_records: list[dict[str, Any]] = []
            stage2_audit_records: list[dict[str, Any]] = []
            stage2_belief_records: list[dict[str, Any]] = []
            if is_stage2 and state.task_tree_state_v2 is not None:
                tt = state.task_tree_state_v2
                # one record per task node, all tied to this sample
                for nid, node in tt.nodes.items():
                    rec = node.to_jsonl_record()
                    rec["task_id"] = task_id  # sample id (carries the trace id mapping)
                    rec["tree_node_id"] = nid
                    stage2_tree_records.append(rec)
                for ev in state.audit_events_buffer_v2:
                    rec = ev.to_jsonl_record()
                    rec["task_id"] = task_id
                    stage2_audit_records.append(rec)
                for agent_name, store in state.belief_store_by_agent_v2.items():
                    rec = serialize_belief_v2(store)
                    rec["task_id"] = task_id
                    rec["agent_name"] = agent_name
                    stage2_belief_records.append(rec)

            return _SampleResult(
                prediction=prediction,
                traces=sample_traces,
                packets=sample_packets,
                snaps=sample_snaps,
                raw_outputs=sample_raw_out,
                is_premature_accept=is_premature,
                is_dead_end=is_dead_end,
                is_correction_forward=is_correction,
                handoffs=handoff_idxs,
                token_cost=token_cost,
                api_prompt=sp,
                api_completion=sc,
                api_total=st,
                task_tree_records=stage2_tree_records,
                audit_event_records=stage2_audit_records,
                belief_snapshot_records=stage2_belief_records,
            )

        # ----------------------------------------------------------------
        # Post-sample: update shared state and flush to disk
        # ----------------------------------------------------------------
        def _after_sample(result: _SampleResult) -> None:
            pred          = result.prediction
            accepted_node = pred["accepted_node"]

            # Update persistent competence (write lock)
            with competence_lock:
                if method_name == "fixed_peer_calibrated" and accepted_node in persistent_competence:
                    before_comp = dict(persistent_competence[accepted_node])
                    prev_self   = float(before_comp.get(accepted_node, 0.5))
                    after_val   = apply_peer_post_sample_competence(prev_self, pred["answer_f1"])
                    persistent_competence[accepted_node][accepted_node] = after_val
                    delta = after_val - prev_self
                    result.snaps.append({
                        "task_id": pred["task_id"],
                        "hop_index": "post_sample",
                        "node_name": accepted_node,
                        "update": {
                            "before": before_comp,
                            "after": dict(persistent_competence[accepted_node]),
                            "signal": "peer_positive" if delta > 0 else "peer_negative",
                        },
                        "competence_after": dict(persistent_competence[accepted_node]),
                    })

            # Persist one sample atomically under the lock: all JSONL rows first,
            # flush every handle, then append checkpoint line.  The checkpoint
            # line is only written after traces/packets/snaps/outputs are flushed
            # so a resume that reads _ckpt_preds.jsonl never skips a sample whose
            # artefacts were lost in a buffer.  (Killing the process can still lose
            # the in-flight sample; that sample is not in ckpt and will re-run.)
            with write_lock:
                for t in result.traces:
                    f_traces.write(json.dumps(t, ensure_ascii=False) + "\n")
                for p in result.packets:
                    f_packets.write(json.dumps(p, ensure_ascii=False) + "\n")
                for s in result.snaps:
                    f_snaps.write(json.dumps(s, ensure_ascii=False) + "\n")
                for o in result.raw_outputs:
                    f_outputs.write(json.dumps(o, ensure_ascii=False) + "\n")
                f_traces.flush()
                f_packets.flush()
                f_snaps.flush()
                f_outputs.flush()
                # Stage-2 only: persist tree + audit events + belief snapshots
                if is_stage2:
                    for r in result.task_tree_records:
                        f_task_tree.write(json.dumps(r, ensure_ascii=False) + "\n")
                    for r in result.audit_event_records:
                        f_audit_evts.write(json.dumps(r, ensure_ascii=False) + "\n")
                    for r in result.belief_snapshot_records:
                        f_belief_snap.write(json.dumps(r, ensure_ascii=False) + "\n")
                    f_task_tree.flush()
                    f_audit_evts.flush()
                    f_belief_snap.flush()
                f_ckpt.write(json.dumps(pred, ensure_ascii=False) + "\n")
                f_ckpt.flush()

            # Update counters
            with counters.lock:
                counters.predictions.append(pred)
                if result.is_dead_end:
                    counters.dead_end += 1
                if result.is_premature_accept:
                    counters.premature_accept += 1
                if result.is_correction_forward:
                    counters.correction_forward += 1
                counters.handoffs.extend(result.handoffs)
                counters.token_costs.append(result.token_cost)
                counters.api_prompt.append(result.api_prompt)
                counters.api_completion.append(result.api_completion)
                counters.api_total.append(result.api_total)

                done_count = len(completed_predictions) + len(counters.predictions)
                if progress_every > 0 and done_count % progress_every == 0:
                    all_preds = completed_predictions + counters.predictions
                    partial_f1 = mean(p["answer_f1"] for p in all_preds)
                    print(
                        f"[runner] {method_name}: {done_count}/{len(samples)} "
                        f"samples complete, partial_F1={partial_f1:.4f}",
                        flush=True,
                    )

        # ----------------------------------------------------------------
        # Execute samples
        # ----------------------------------------------------------------
        samples_to_run = [s for s in samples if s["task_id"] not in completed_ids]

        if n_workers > 1 and samples_to_run:
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                future_map = {executor.submit(_process_one, s): s for s in samples_to_run}
                for future in as_completed(future_map):
                    sample = future_map[future]
                    try:
                        _after_sample(future.result())
                    except ModelDriftError:
                        # Propagate immediately — do not swallow or continue.
                        # The checkpoint written so far is valid; only the
                        # in-flight sample is lost.
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise
                    except Exception as exc:
                        print(
                            f"[runner] WARNING: {sample.get('task_id')} raised {exc}",
                            flush=True,
                        )
        else:
            for sample in samples_to_run:
                _after_sample(_process_one(sample))

        # Close incremental files
        for fh in (f_traces, f_packets, f_snaps, f_outputs, f_ckpt):
            fh.close()
        if is_stage2:
            for fh in (f_task_tree, f_audit_evts, f_belief_snap):
                if fh is not None:
                    fh.close()

        # ----------------------------------------------------------------
        # Compute final metrics (new + checkpoint samples)
        # ----------------------------------------------------------------
        all_new = counters.predictions
        all_predictions = completed_predictions + all_new

        # Rebuild scalars for checkpoint predictions (no per-sample counters stored)
        ckpt_dead_end = ckpt_premature = ckpt_correction = 0
        ckpt_handoffs: list[int] = []
        ckpt_token:    list[int] = []
        for p in completed_predictions:
            tr = p.get("termination_reason", "accepted")
            if tr in ("dead_end", "topology_violation", "max_handoff_reached"):
                ckpt_dead_end += 1
            hc = p.get("hop_count", 1)
            if (
                hc == 1
                and p.get("accepted_node", "") not in ("synthesizer",)
                and method_name not in ("single_agent", "central_orchestrator")
            ):
                ckpt_premature += 1
            ckpt_handoffs.extend(range(1, hc))
            ckpt_token.append(p.get("token_cost", 300))

        total_dead_end    = ckpt_dead_end    + counters.dead_end
        total_premature   = ckpt_premature   + counters.premature_accept
        total_correction  = ckpt_correction  + counters.correction_forward
        all_handoffs      = ckpt_handoffs    + counters.handoffs
        all_token         = ckpt_token       + counters.token_costs
        all_api_prompt    = [0] * len(completed_predictions) + counters.api_prompt
        all_api_comp      = [0] * len(completed_predictions) + counters.api_completion
        all_api_total_list= [0] * len(completed_predictions) + counters.api_total

        n = len(all_predictions)
        answer_em   = mean(p["answer_em"] for p in all_predictions) if n else 0.0
        answer_f1   = mean(p["answer_f1"] for p in all_predictions) if n else 0.0
        mhc         = mean(all_handoffs) if all_handoffs else 0.0
        par         = total_premature   / n if n else 0.0
        der         = total_dead_end    / n if n else 0.0
        facr        = total_correction  / n if n else 0.0
        tc_avg      = mean(all_token)   if all_token else 0.0
        ap_avg      = mean(all_api_prompt)  if all_api_prompt  else 0.0
        ac_avg      = mean(all_api_comp)    if all_api_comp     else 0.0
        at_avg      = mean(all_api_total_list) if all_api_total_list else 0.0
        cost_norm   = answer_f1 / (tc_avg / 1000) if tc_avg else 0.0
        cost_norm_api = answer_f1 / (at_avg / 1000) if at_avg else 0.0
        fa_count    = sum(1 for p in all_predictions if p["hop_count"] == 1)
        fa_success  = (
            mean(p["answer_f1"] for p in all_predictions if p["hop_count"] == 1)
            if fa_count else 0.0
        )

        metrics = {
            "answer_em":                    round(answer_em, 4),
            "answer_f1":                    round(answer_f1, 4),
            "mean_handoff_count":           round(mhc, 4),
            "dead_end_rate":                round(der, 4),
            "premature_accept_rate":        round(par, 4),
            "forward_after_correction_rate":round(facr, 4),
            "token_cost_per_sample":        round(tc_avg, 2),
            "api_prompt_tokens_per_sample": round(ap_avg, 2),
            "api_completion_tokens_per_sample": round(ac_avg, 2),
            "api_total_tokens_per_sample":  round(at_avg, 2),
            "cost_normalized_f1":           round(cost_norm, 6),
            "cost_normalized_f1_api":       round(cost_norm_api, 6),
            "first_accept_success_rate":    round(fa_success, 4),
            "sample_count":                 n,
        }

        # Sort predictions to original sample order for deterministic output
        all_predictions_sorted = sorted(
            all_predictions,
            key=lambda p: id_to_orig.get(p["task_id"], n),
        )

        self._write_run_files(
            run_dir=run_dir,
            run_config=run_config,
            samples=samples,
            all_predictions=all_predictions_sorted,
            metrics=metrics,
        )
        return metrics

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _replay_competence(
        self,
        method_name: str,
        accepted_node: str,
        f1: float,
        competence: dict[str, dict[str, float]],
    ) -> None:
        if method_name == "fixed_peer_calibrated" and accepted_node in competence:
            prev = float(competence[accepted_node].get(accepted_node, 0.5))
            competence[accepted_node][accepted_node] = (
                apply_peer_post_sample_competence(prev, f1)
            )

    def _write_run_files(
        self,
        run_dir: Path,
        run_config: dict[str, Any],
        samples: list[dict[str, Any]],
        all_predictions: list[dict[str, Any]],
        metrics: dict[str, Any],
    ) -> None:
        """Write final summary files.  Incremental JSONL logs are already on
        disk (routing_traces.jsonl etc.); this writes the remaining artefacts."""

        (run_dir / "prompt_templates").mkdir(parents=True, exist_ok=True)
        tmpl_rel = run_config.get("shared_prompt_template") or "prompts/main_agent_prompt.txt"
        tmpl_path = Path(tmpl_rel)
        if not tmpl_path.is_absolute():
            tmpl_path = _REPO_ROOT / tmpl_path
        main_prompt_dst = run_dir / "prompt_templates" / "main_prompt.txt"
        main_prompt_dst.write_text(
            tmpl_path.read_text(encoding="utf-8") if tmpl_path.is_file()
            else f"Agent prompt: template not found at {tmpl_path}",
            encoding="utf-8",
        )

        with (run_dir / "run_config.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(run_config, f, allow_unicode=True, sort_keys=False)

        sample_ids = [s["task_id"] for s in samples]
        (run_dir / "sample_ids.json").write_text(
            json.dumps(sample_ids, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # raw_inputs.jsonl — complete, ordered
        raw_inputs = [{k: v for k, v in s.items() if k != "supporting_facts"} for s in samples]
        self._write_jsonl(run_dir / "raw_inputs.jsonl", raw_inputs)

        # parsed_predictions.jsonl — final ordered file
        self._write_jsonl(run_dir / "parsed_predictions.jsonl", all_predictions)

        (run_dir / "metrics.json").write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        with (run_dir / "main_table.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(metrics.keys()))
            writer.writeheader()
            writer.writerow(metrics)

        failures = [p for p in all_predictions if p["answer_f1"] < 0.5]
        failure_lines = ["# failure_cases\n"]
        for p in failures[:20]:
            failure_lines.append(
                f"## {p['task_id']}\n"
                f"- Q: {p['question'][:100]}\n"
                f"- Gold: {p['gold_answer']}\n"
                f"- Predicted: {p['final_answer'][:100]}\n"
                f"- F1: {p['answer_f1']:.3f}, EM: {p['answer_em']:.0f}\n"
                f"- Accepted by: {p['accepted_node']}, hops: {p['hop_count']}\n"
                f"- Termination: {p['termination_reason']}\n"
            )
        (run_dir / "failure_cases.md").write_text("\n".join(failure_lines), encoding="utf-8")

        good = [p for p in all_predictions if p["answer_f1"] >= 0.5]
        case_lines = ["# case_studies\n"]
        for p in good[:5]:
            case_lines.append(
                f"## {p['task_id']}\n"
                f"- Q: {p['question'][:120]}\n"
                f"- Gold: {p['gold_answer']}\n"
                f"- Predicted: {p['final_answer'][:120]}\n"
                f"- F1: {p['answer_f1']:.3f}, hops: {p['hop_count']}, node: {p['accepted_node']}\n"
            )
        (run_dir / "case_studies.md").write_text("\n".join(case_lines), encoding="utf-8")

        (run_dir / "run_notes.md").write_text(
            "# run_notes\n\n"
            f"- generated_at: {datetime.now(timezone.utc).isoformat()}\n"
            f"- topology: {self.topology}\n"
            f"- method: {run_config.get('method_name', 'unknown')}\n"
            f"- model_config_label: {run_config.get('main_model', 'unknown')}\n"
            f"- model_resolved_runtime: {resolved_model()}\n"
            f"- sample_count: {metrics['sample_count']}\n"
            f"- n_workers: {run_config.get('n_workers', 1)}\n",
            encoding="utf-8",
        )

    @staticmethod
    def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
