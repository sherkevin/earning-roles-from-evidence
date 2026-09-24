#!/usr/bin/env python3
"""Read-only reconciliation of the completed A0 v4 development diagnostic.

Only processed_results.json and report.md are written. Frozen config, runner,
episode evidence and native AppWorld outputs are never altered.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/aamas2027/peer_judgment_a0_v4.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def check(ok: bool, explanation: str) -> None:
    if not ok:
        raise RuntimeError(explanation)


def main() -> None:
    cfg = json.loads(CONFIG.read_text())
    out = ROOT / cfg["output_root"]
    manifest = json.loads((out / "source_manifest.json").read_text())
    results = json.loads((out / "results.json").read_text())
    expected = [job["task_id"] for job in cfg["episodes_in_order"]]
    check(manifest["config_sha256"] == sha(CONFIG), "config hash mismatch")
    check(manifest["runner_sha256"] == sha(out / "runner_at_execution.py") ==
          sha(ROOT / "scripts/aamas_peer_judgment_a0_v4.py"), "executed runner hash mismatch")
    check(json.loads((out / "frozen_config.json").read_text()) == cfg,
          "frozen config contents mismatch")
    check(manifest["protocol_sha256"] == cfg["protocol_sha256"] ==
          sha(ROOT / cfg["protocol_path"]), "protocol hash mismatch")
    check(manifest["public_inventory_sha256"] == cfg["public_inventory_sha256"] ==
          sha(ROOT / cfg["public_inventory_path"]), "public inventory hash mismatch")
    for pinned in cfg["v3_completed_run_pins"].values():
        if isinstance(pinned, dict) and "path" in pinned:
            check(sha(ROOT / pinned["path"]) == pinned["sha256"],
                  "preserved v3 evidence changed")
    for key, receipt in manifest["preflight"].items():
        source = ROOT / receipt["result_path"]
        check(sha(source) == receipt["sha256"], f"{key} preflight hash mismatch")
        value = json.loads(source.read_text())
        check(value["ok"] and value["runner_sha256"] == manifest["runner_sha256"]
              and value["config_sha256"] == manifest["config_sha256"],
              f"{key} belongs to another or failed runner")
    check(results["attempted_ids"] == expected[:2]
          and results["unstarted_ids"] == expected[2:], "attempted/unstarted order differs")
    check(not any((out / "episodes" / task).exists() for task in expected[2:]),
          "an unstarted task has a directory")
    run_events = rows(out / "run_raw.jsonl")
    collected = [r["payload"]["task_id"] for r in run_events
                 if r["event"] == "episode_collected"]
    stopped = [r for r in run_events if r["event"] == "run_stopped"]
    finals = [r for r in run_events if r["event"] == "run_final"]
    check(collected == expected[:2] and len(stopped) == len(finals) == 1,
          "run chronology incomplete")
    check(stopped[0]["payload"].get("category") == "provider_transport"
          and stopped[0]["payload"].get("consecutive_count") == 2
          and run_events.index(stopped[0]) < run_events.index(finals[0]),
          "frozen repeated-infrastructure stop not observed")

    cases = []
    for job in cfg["episodes_in_order"][:2]:
        task = job["task_id"]
        directory = out / "episodes" / task
        result_file = directory / "result.json"
        raw_file = directory / "raw.jsonl"
        result = json.loads(result_file.read_text())
        events = rows(raw_file)
        starts = [r for r in events if r["event"] == "request_start"]
        responses = [r for r in events if r["event"] == "response"]
        errors = [r for r in events if r["event"] == "request_error"]
        observations = [r for r in events if r["event"] == "environment_observation"]
        api_calls = [r["payload"] for r in events if r["event"] == "public_api_call"]
        public_reads = [call for call in api_calls
                        if call.get("phase") == "producer" and call.get("public_read_observation")]
        writes = [call for call in api_calls if call.get("phase") == "producer"
                  and call["method"] != "get"
                  and not call["api_path"].endswith("/auth/token")]
        phase = result["phase_costs"]["producer"]
        check(result["task_id"] == task and result["status"] == "UNKNOWN"
              and result["stop_phase"] == "producer"
              and result["infrastructure_error_category"] == "provider_transport",
              f"{task}: not a producer transport UNKNOWN")
        check(len(starts) == result["attempted_task_calls"] == phase["attempts"]
              and len(starts) <= cfg["attempted_call_caps_per_episode"]["producer"],
              f"{task}: attempt accounting or cap mismatch")
        check(len(responses) + len(errors) == len(starts)
              and all(e["payload"]["error_type"] == "TimeoutError" for e in errors),
              f"{task}: response/error accounting mismatch")
        check(len(observations) == result["world_execute_count"] and not writes,
              f"{task}: world-step mismatch or producer task write")
        check(not any((directory / name).exists() for name in (
              "proposal.json", "pre_action_judgment.json", "actual_use.json",
              "role_event.json", "evaluator_only.json")),
              f"{task}: unexpected seal or evaluator file")
        check(result["official_final_success"] is None
              and not result["valid_complete_observation_chain"]
              and result["validation_rejections"]["producer"] == 0,
              f"{task}: missing observation misclassified")
        request_bytes = {r["payload"]["attempt"]:
                         len(json.dumps(r["payload"]["request"]).encode()) for r in starts}
        message_content_chars = {r["payload"]["attempt"]:
                                 sum(len(m["content"]) for m in r["payload"]["request"]["messages"])
                                 for r in starts}
        feedback = starts[-1]["payload"]["request"]["messages"][-1]["content"]
        marker = "\nPublic source receipts (JSON Pointer paths refer to response):\n"
        last_feedback_receipt_chars = (len(feedback.split(marker, 1)[1])
                                       if marker in feedback else 0)
        cases.append({
            "task_id": task, "producer_id": job["producer_id"],
            "consumer_id": job["consumer_id"], "status": "UNKNOWN",
            "stop_reason": result["stop_reason"], "stop_category": "provider_transport",
            "attempts": len(starts), "responses": len(responses),
            "timeouts": len(errors), "world_steps": len(observations),
            "public_task_data_gets": len(public_reads), "public_api_calls": len(api_calls),
            "venmo_feed_calls": sum(call["app"] == "venmo" and
                                    call["api"] == "show_social_feed" for call in api_calls),
            "producer_task_write_calls": len(writes),
            "request_bytes_by_attempt": request_bytes,
            "message_content_chars_by_attempt": message_content_chars,
            "max_request_bytes": max(request_bytes.values()),
            "last_user_feedback_chars": len(feedback),
            "last_feedback_receipt_chars": last_feedback_receipt_chars,
            "timeout_retry_used": result["timeout_retry_used"],
            "unknown_usage_attempts": phase["unknown_usage_attempts"],
            "reported_tokens": phase["tokens"],
            "api_seconds": phase["api_seconds"], "wall_seconds": result["wall_seconds"],
            "raw_sha256": sha(raw_file), "result_sha256": sha(result_file),
            "consumer_model_calls": 0, "official_score_available": False,
        })
    first_events = rows(out / "episodes" / expected[0] / "raw.jsonl")
    first_requests = [r["payload"]["request"] for r in first_events
                      if r["event"] == "request_start"]
    first_backoffs = [r["payload"] for r in first_events
                      if r["event"] == "transport_backoff"]
    check(len(first_requests) == 8 and first_requests[6] == first_requests[7]
          and len(first_backoffs) == 1
          and first_backoffs[0]["retry_kind"] == "same_request_unreturned_timeout",
          "first-case timeout retry was not one identical unreturned request")
    check(cases[0]["attempts"] == 8 and cases[0]["timeouts"] == 2
          and cases[0]["venmo_feed_calls"] == 55 and cases[0]["timeout_retry_used"]
          and cases[1]["attempts"] == 12 and cases[1]["timeouts"] == 1
          and not cases[1]["timeout_retry_used"], "expected case chronology differs")
    attempts = sum(r["attempts"] for r in cases)
    responses = sum(r["responses"] for r in cases)
    timeouts = sum(r["timeouts"] for r in cases)
    steps = sum(r["world_steps"] for r in cases)
    check(attempts == results["task_llm_attempts"] == 20
          and responses == 17 and timeouts == 3 and steps == 17,
          "batch request/world counts differ")
    check(results["complete_observation_chains"] == 0
          and results["A1_observation_gate"] == "stop_or_incomplete_A0", "gate differs")
    token_names = ("input_tokens", "output_tokens", "cache_read_input_tokens",
                   "cache_creation_input_tokens")
    tokens = {name: sum(r["reported_tokens"][name] for r in cases) for name in token_names}
    summary = {
        "status": "AUDITED_A0_V4_DEVELOPMENT_ONLY_STOPPED_BY_PREDECLARED_RULE",
        "config_sha256": sha(CONFIG), "executed_runner_sha256": manifest["runner_sha256"],
        "protocol_sha256": cfg["protocol_sha256"],
        "source_manifest_sha256": sha(out / "source_manifest.json"),
        "run_raw_sha256": sha(out / "run_raw.jsonl"),
        "results_sha256": sha(out / "results.json"),
        "scheduled_native_ids": expected,
        "attempted_ids": results["attempted_ids"],
        "unstarted_ids": results["unstarted_ids"],
        "stop_rule": "two consecutive provider_transport infrastructure categories",
        "task_model_attempts": attempts,
        "returned_task_model_responses": responses,
        "task_model_timeouts": timeouts,
        "separate_v4_health_model_attempts": 1,
        "producer_world_steps": steps,
        "producer_public_task_data_gets": sum(r["public_task_data_gets"] for r in cases),
        "producer_task_write_calls_in_public_audit": 0,
        "sealed_proposals": 0, "consumer_model_calls": 0,
        "pre_action_judgments": 0, "actual_use_records": 0,
        "role_events": 0, "official_scores": 0,
        "complete_observation_chains_attempted_denominator": "0/2",
        "complete_observation_chains_scheduled_denominator": "0/4; two unstarted",
        "A1_B_gate": "STOP_OBSERVATION_PROTOCOL_BEFORE_A1_B",
        "aggregate_reported_tokens": tokens,
        "unknown_usage_attempts": sum(r["unknown_usage_attempts"] for r in cases),
        "task_api_seconds": sum(r["api_seconds"] for r in cases),
        "task_wall_seconds_sum": sum(r["wall_seconds"] for r in cases),
        "usd_cost": None,
        "limitations": [
            "V4 repeats known v3 train IDs after observing v3 and is instrument development, not independent confirmation or method-effect evidence.",
            "Only two of four scheduled IDs started because the frozen consecutive-infrastructure stop rule fired.",
            "Both attempted cases are producer transport UNKNOWN, not official task failures; no deliverable, consumer use, role update or evaluator result exists.",
            "The first case made 55 public Venmo feed calls; unbounded controller receipts inflated the next feedback to over 410k content characters before two identical-request timeouts. This is a measured instrument burden, not proved sole cause of timeout.",
            "The second case timed out on its twelfth attempt; the phase cap prevented retry. Three timed-out calls have unknown token usage and verified USD price is unavailable.",
            "Native AppWorld tasks are single-user. Splitting preparation and action between actors alone does not establish a natural collaboration need or marginal value of delivery.",
            "A0 is stateless instrumentation; A/B/C/D are schedule labels, not learned roles. A later same-consumer delivery-visible/hidden paired test is needed before role-learning claims."
        ],
        "cases": cases,
    }
    (out / "processed_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    table = "\n".join(
        f"| `{row['task_id']}` | {row['attempts']} | {row['responses']} | "
        f"{row['timeouts']} | {row['world_steps']} | {row['public_task_data_gets']} | "
        f"{row['max_request_bytes']:,} |"
        for row in cases)
    report = f"""# A0 v4 开发诊断：两例传输 UNKNOWN 后按预定规则停机

2026-09-23。v4 是看过 v3 结果后、在相同四个已知 AppWorld train ID 上冻结的**控制器开发重跑**。实际按序启动前两题，共 **20/96** 次真实任务模型请求（8+12），17 次返回、3 次 `TimeoutError`，17 个生产者世界步骤。两题都没有封存提案，观察链为 **0/2 已尝试**；另两题因冻结的“连续两例同类基础设施故障”规则未启动，因此不能把它们写成失败样本。单独 provider 健康检查另有 1 次成功真实调用。

| 原生 ID | 尝试 | 响应 | 超时 | 世界步骤 | 公开任务 GET | 最大请求字节 |
|---|---:|---:|---:|---:|---:|---:|
{table}

`2a163ab_1` 在第 6 个世界步骤中调用了 55 页 `venmo.show_social_feed`。原生 REPL 观察输出为 4,407 个字符，而控制器把每个 GET 的来源回执附在下一轮反馈中：回执部分 **{cases[0]['last_feedback_receipt_chars']:,} 个原始字符串字符**，整条反馈 **{cases[0]['last_user_feedback_chars']:,} 个原始字符串字符**，第 7 次请求所有消息内容合计 **{cases[0]['message_content_chars_by_attempt'][7]:,} 个原始字符串字符**。按实际 `RealAPI` 的 `json.dumps(request).encode()` 序列化口径，该请求为 **{cases[0]['request_bytes_by_attempt'][7]:,} bytes**；这些字符数与 JSON 字节数不应混用。第 7 次请求读超时，冻结规则只在无响应且消息不变时重试一次；第 8 次请求字节相同，再次超时，故为 `UNKNOWN/provider_transport`。无界回执膨胀是明确的控制器瓶颈，但仅凭时间相关性不能证明超时完全由长度导致。`afc0fce_1` 的第 12 次请求也超时，因生产者 12 次额度已尽而不能重试；其最大请求为 **{cases[1]['max_request_bytes']:,} JSON bytes**，更不能把所有超时简单归结为超长消息。两例连续同属 `provider_transport`，原始 `run_raw.jsonl` 随即记录 `run_stopped` 和 `run_final`；`6ea6792_1`、`60d0b5b_1` 无运行目录。

两例的公开 API 审计共记录 {sum(r['public_api_calls'] for r in cases)} 次调用、{summary['producer_public_task_data_gets']} 次公开任务数据 GET，没有发现生产者任务写；未封存的生产者世界没有执行读后全模型哈希比较，因此不能由“审计零写”推断全面状态不变。没有消费者模型调用、事前判断、实际使用、角色事件或官方 evaluator 分数；所有结果都是**观察删失 UNKNOWN**，不代表任务语义失败，更不能代表“同伴评判学习角色”有效或无效。已报告的输入 {tokens['input_tokens']:,}、输出 {tokens['output_tokens']:,}、cache-read 输入 {tokens['cache_read_input_tokens']:,} tokens；3 次超时的用量未知，美元价格未知。

本次 v4 的通用登录、`print` 探索输出与 12 次额度没有打通交付链；但样本仅两例且由传输规则截断，不能以此估计提示的独立效果。AppWorld 原生是单用户任务，生产者准备→接收者执行的切分本身没有证明自然协作需求；此前 v5 的接收者独立复查也没有证明交付的边际价值。若以后能形成可审计交付链，应先对同一接收者做“交付可见/不可见”的配对成本和质量比较，再谈判断→角色→后续职责。A0 的 A/B/C/D 仍只是排班标签，A1/B 未启动；不能借本次失败直接改变研究假设或宣称提高中稿率。

可复核入口：[v4 冻结配置](../../../../configs/aamas2027/peer_judgment_a0_v4.json)、[独立协议](../../../../docs/scientist/analysis/AAMAS_PEER_JUDGMENT_A0_V4_PROTOCOL_20260923.md)、[执行源码快照](runner_at_execution.py)、[源码/前置证据清单](source_manifest.json)、[运行事件流](run_raw.jsonl)、[逐例原始记录](episodes/)、[逐例汇总](results.json)、[处理数据](processed_results.json)。配置 SHA256 `{sha(CONFIG)}`，runner SHA256 `{manifest['runner_sha256']}`，协议 SHA256 `{cfg['protocol_sha256']}`。每次真实请求、响应、异常和公开 API 审计均保存在逐例 `raw.jsonl`；本报告没有用官方评分修正在线行为。
"""
    (out / "report.md").write_text(report)
    print(json.dumps({"status": summary["status"], "attempts": attempts,
                      "responses": responses, "timeouts": timeouts,
                      "unstarted": results["unstarted_ids"],
                      "processed_sha256": sha(out / "processed_results.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
