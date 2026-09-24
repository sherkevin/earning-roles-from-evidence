#!/usr/bin/env python3
"""Reconcile sealed A0 v3 raw task evidence without changing experiment inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/aamas2027/peer_judgment_a0_v3.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    cfg = json.loads(CONFIG.read_text())
    out = ROOT / cfg["output_root"]
    manifest = json.loads((out / "source_manifest.json").read_text())
    run_result = json.loads((out / "results.json").read_text())
    expect(manifest["config_sha256"] == digest(CONFIG), "config source hash mismatch")
    expect(manifest["runner_sha256"] == digest(out / "runner_at_execution.py"),
           "executed runner snapshot mismatch")
    expect(json.loads((out / "frozen_config.json").read_text()) == cfg,
           "frozen config content mismatch")
    expect(manifest["protocol_sha256"] == digest(ROOT / cfg["protocol_path"]),
           "pinned protocol hash mismatch")
    expect(manifest["public_inventory_sha256"] == digest(ROOT / cfg["public_inventory_path"]),
           "pinned candidate inventory mismatch")
    for key, receipt in manifest["preflight"].items():
        path = ROOT / receipt["result_path"]
        expect(digest(path) == receipt["sha256"], f"{key} preflight result hash mismatch")
        p = json.loads(path.read_text())
        expect(p["ok"] and p["config_sha256"] == manifest["config_sha256"] and
               p["runner_sha256"] == manifest["runner_sha256"],
               f"{key} preflight result differs from executed runner")
    scheduled = [job["task_id"] for job in cfg["episodes_in_order"]]
    expect(run_result["attempted_ids"] == scheduled and not run_result["unstarted_ids"],
           "scheduled A0 task order/completion mismatch")
    run_events = rows(out / "run_raw.jsonl")
    collected = [event["payload"]["task_id"] for event in run_events
                 if event["event"] == "episode_collected"]
    expect(collected == scheduled and sum(e["event"] == "run_final" for e in run_events) == 1,
           "run_raw collection/finalization chronology mismatch")
    cases = []
    for job in cfg["episodes_in_order"]:
        task_id = job["task_id"]
        episode_dir = out / "episodes" / task_id
        result = json.loads((episode_dir / "result.json").read_text())
        raw = rows(episode_dir / "raw.jsonl")
        starts = [event for event in raw if event["event"] == "request_start"]
        responses = [event for event in raw if event["event"] == "response"]
        errors = [event for event in raw if event["event"] == "request_error"]
        observations = [event for event in raw if event["event"] == "environment_observation"]
        api_calls = [event["payload"] for event in raw if event["event"] == "public_api_call"]
        source_reads = [call for call in api_calls if call.get("phase") == "producer"
                        and call.get("public_read_observation")]
        actor_writes = [call for call in api_calls if call.get("phase") == "producer"
                        and call["method"] != "get" and
                        not call["api_path"].endswith("/auth/token")]
        phase_cost = result["phase_costs"]["producer"]
        expect(result["task_id"] == task_id and result["status"] == "UNKNOWN",
               f"{task_id} unexpected result state")
        expect(result["attempted_task_calls"] == len(starts) == phase_cost["attempts"] == 8,
               f"{task_id} attempted-call accounting mismatch")
        expect(len(responses) + len(errors) == len(starts),
               f"{task_id} response/error accounting mismatch")
        expect(result["world_execute_count"] == len(observations),
               f"{task_id} executed world-step accounting mismatch")
        expect(not actor_writes, f"{task_id} producer task write in public audit")
        expect(not any((episode_dir / name).exists() for name in (
            "proposal.json", "pre_action_judgment.json", "actual_use.json",
            "role_event.json", "evaluator_only.json")),
            f"{task_id} unexpected sealed/evaluator artifact")
        expect(result["official_final_success"] is None and
               not result["valid_complete_observation_chain"],
               f"{task_id} missing outcome incorrectly scored")
        cases.append({"task_id": task_id, "family": job["family"],
            "producer_id": job["producer_id"], "consumer_id": job["consumer_id"],
            "result_sha256": digest(episode_dir / "result.json"),
            "raw_sha256": digest(episode_dir / "raw.jsonl"),
            "status": result["status"], "stop_phase": result["stop_phase"],
            "stop_type": result["error"]["type"],
            "stop_reason": result["stop_reason"],
            "attempts": len(starts), "returned_responses": len(responses),
            "request_errors": len(errors), "world_steps": len(observations),
            "public_task_data_gets": len(source_reads),
            "producer_task_write_calls": len(actor_writes),
            "consumer_model_calls": 0, "proposal_sealed": False,
            "pre_action_judgment_sealed": False, "actual_use_sealed": False,
            "official_score_available": False,
            "tokens": phase_cost["tokens"],
            "unknown_usage_attempts": phase_cost["unknown_usage_attempts"],
            "api_seconds": phase_cost["api_seconds"],
            "wall_seconds": result["wall_seconds"],
            "last_event_timestamp_utc": raw[-1]["timestamp"]})
    total_attempts = sum(row["attempts"] for row in cases)
    token_keys = ("input_tokens", "output_tokens", "cache_read_input_tokens",
                  "cache_creation_input_tokens")
    totals = {key: sum(row["tokens"][key] for row in cases) for key in token_keys}
    expect(total_attempts == run_result["task_llm_attempts"] == 32,
           "A0 global call count mismatch")
    expect(sum(row["returned_responses"] for row in cases) == 31 and
           sum(row["request_errors"] for row in cases) == 1,
           "A0 response/timeout counts mismatch")
    expect(sum(row["world_steps"] for row in cases) == 31,
           "A0 world-step count mismatch")
    expect(run_result["complete_observation_chains"] == 0 and
           run_result["A1_observation_gate"] == "stop_or_incomplete_A0",
           "A0 observation gate mismatch")
    summary = {"status": "AUDITED_A0_V3_DEVELOPMENT_ONLY", "config_sha256": digest(CONFIG),
        "executed_runner_sha256": manifest["runner_sha256"],
        "source_manifest_sha256": digest(out / "source_manifest.json"),
        "run_raw_sha256": digest(out / "run_raw.jsonl"),
        "results_sha256": digest(out / "results.json"),
        "ordered_native_ids": scheduled,
        "all_four_scheduled_episodes_naturally_completed": True,
        "manual_termination_changed_execution": False,
        "task_model_attempts": total_attempts,
        "separate_health_model_attempts": 1,
        "returned_task_model_responses": 31,
        "task_model_request_errors": 1,
        "producer_world_steps": 31,
        "producer_public_task_data_gets": sum(r["public_task_data_gets"] for r in cases),
        "producer_task_write_calls": 0,
        "sealed_proposals": 0, "consumer_model_calls": 0,
        "pre_action_judgments": 0, "actual_use_records": 0,
        "role_events": 0, "official_scores": 0,
        "complete_observation_chains": 0,
        "gate": "STOP_OBSERVATION_PROTOCOL_BEFORE_A1_B",
        "aggregate_reported_tokens": totals,
        "unknown_usage_attempts": sum(r["unknown_usage_attempts"] for r in cases),
        "task_api_seconds": sum(r["api_seconds"] for r in cases),
        "task_wall_seconds_sum": sum(r["wall_seconds"] for r in cases),
        "usd_cost": None,
        "limitations": [
            "Three producer phases exhausted eight attempts; one eighth request timed out after seven public world steps.",
            "No producer deliverable, consumer judgment/action, role update, or official score exists in this A0 batch.",
            "UNKNOWN is censored observation, not semantic task failure or evidence against role learning.",
            "The A0 controller is stateless instrumentation; A/B/C/D are scheduling labels, not learned roles.",
            "All tasks are known train development material; 6ea6792_1 had earlier R0 single-agent exposure.",
            "No price is verified; token usage for the timeout attempt is unknown."
        ],
        "cases": cases}
    (out / "processed_results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    table = "\n".join(f"| `{r['task_id']}` | {r['attempts']} | {r['world_steps']} | "
                      f"{r['public_task_data_gets']} | {r['stop_type']} |" for r in cases)
    report = f"""# A0 开发诊断：真实 API 的四例观察链未形成

2026-09-23。四个预先固定的 AppWorld train ID 按冻结顺序自然运行完毕，任务模型调用 **32/80** 次预算，另有单独的 provider 健康调用 1 次。四例都停在生产者阶段：三例在 **8/8** 次预算耗尽，`6ea6792_1` 在完成 7 个公开世界步骤后第 8 次请求 **120 秒超时**。合计 31 条真实响应、1 次请求错误、31 个生产者世界步骤，**0/4** 完整交付→行动前判断→实际使用链。没有接收者模型调用、角色更新或官方评分；这批 UNKNOWN 不能解释成任务失败或方法无效。预设 3/4 观察门未过，A1/B 不启动。

| 原生 ID | 尝试 | 世界步骤 | 公开任务数据 GET | 结束原因 |
|---|---:|---:|---:|---|
{table}

四例中生产者审计没有任务写调用；零 LLM native fixture 另验证了真实 Venmo 登录/GET、生产者写阻断、初始世界 model hashes 相等、读后状态未变与接收者可写。个别未封存的生产者世界没有运行读后完整状态比较，因此这里不把审计零写上升为全面状态不变证明。任务用量中，已知输入 {totals['input_tokens']:,}、输出 {totals['output_tokens']:,}、cache-read 输入 {totals['cache_read_input_tokens']:,} tokens；超时那次用量未知，美元价格未知。

受控信息流、逐项公开来源和两个独立世界的控制器是在本次运行前冻结的，但尚未被任何交付案例检验。A/B/C/D 只用于固定配对；A0 没有跨任务私有记忆、角色更新或后续职责选择。`6ea6792_1` 在此前 R0 单代理开发中已接触，所有四例都只能作为开发诊断。前两个预算耗尽已经使 3/4 门槛无法达到；冻结配置没有提前无望停机条款，所以后两例仍执行。第三例超时后配置规定连续两例同类基础设施故障才停；更保守的人工即时停机指令到达时第四例已自然完成，TERM 未命中运行进程，原始 `run_final` 无人工中断。

下一轮只能作为**独立、前瞻的控制器诊断**：更明确提示公开登录、打印探索返回值与及时封存，并在相同证据条件下扩大生产者探索预算；若仍没有足够的真实交付/判断/使用事件，应停止这种观察器，而不是把失败改写为原研究问题的否定。改版需新协议、配置、runner 与单独日志，保留本次原始记录，不用结果挑换任务。AppWorld 原生是单用户任务；把它拆为生产者准备和接收者执行，不自动形成真实协作需求。先前 v5 的接收者独立复查也未证明交付的边际价值。即使 v4 打通观察链，下一步仍须在同一接收者条件下比较“交付可见/不可见”的成本与质量，不能直接宣称角色学习。现有数据既不能计算同伴判断质量，也不能检验判断→角色→后续职责，更不能支持中稿率结论。

可复核入口：[冻结配置](../../../../configs/aamas2027/peer_judgment_a0_v3.json)、[运行源码快照](runner_at_execution.py)、[源码/前置证据清单](source_manifest.json)、[运行事件流](run_raw.jsonl)、[逐例原始记录](episodes/)、[逐例汇总](results.json)、[处理数据](processed_results.json)。配置 SHA256 `{digest(CONFIG)}`；运行源码 SHA256 `{manifest['runner_sha256']}`；四例每次请求、响应、错误和公开 API 调用均在各 `episodes/<ID>/raw.jsonl`。本报告是开发诊断，未运行官方 evaluator。
"""
    (out / "report.md").write_text(report)
    print(json.dumps({"status": summary["status"], "attempts": total_attempts,
                      "responses": 31, "complete_chains": 0,
                      "processed_sha256": digest(out / "processed_results.json")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
