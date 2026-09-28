# 2026-09-28 PIPE3 real smoke v3

- 状态：`COMPLETE`（工程链闭合；不是 benchmark、效能或角色学习结果）
- 对应 Goal：ER-G1、ER-G3、ER-G4 的接入证据；`goal_change_requested=false`
- 真实 API：3 次；GPU：0；policy update：0；`scientific_claim_allowed=false`

## 冻结卡与证据

卡片：[n03_pipe3_real_smoke_v3.json](/Users/jingwu/work/earning-roles/configs/aamas2027/n03_pipe3_real_smoke_v3.json)

完整证据：[n03_pipe3_real_smoke_20260928_v3](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_real_smoke_20260928_v3)

卡片 SHA-256 为 `f57d0f61ec6c17bdb1629e76b6b8604b670cf123ff419e0db2be50733cb5d268`；
运行代码提交为 `5dc57a6bc59f4dfa04281bd0684e5a6e3cde9655`；TeamBench 实际与声明 pin
均为 `d185aef1916fd86a9ba554d581fd256319a973af`，工作树干净。

## 真实运行结果

`内部/qwen3.8-max` 在 thinking disabled、temperature 0、无重试条件下完成 producer、
judgment、consumer 三次 HTTP 200/end-turn 请求。用量为 3,184 input tokens、1,407
output tokens，另有 1,024 cache-read tokens；三次墙钟时间合计约 25.42 秒。原始 SSE、
解析响应、用量、请求卡片和每阶段日志均已保存。

独立的版本化评分器均完成：

| 阶段 | 版本 | 状态 | 质量 | 覆盖/决策 |
|---|---|---:|---:|---|
| producer Qp | `pipe3-producer-objective-v2` | PASS | 1.0 | complete/complete |
| recipient Qr | `pipe3-recipient-objective-v2` | PASS | 1.0 | complete/complete |
| sink adoption | `pipe3-recipient-objective-v2` | PASS | 1.0 | complete/complete |

原生 ledger 严格回放为 `PASS`，包含 selection、task start、delivery、producer score、
judgment、consumer action、terminal outcome、role evidence 八个事件。consumer 确实使用
了 producer artifact，并只修改了 `processor.py`；adoption scorer 观察到最终输出可被 sink
读取。

## 不能从本次运行推出的结论

这只是一次 integration smoke。没有 later assignment、第二个独立 root、对照 policy、
统计重复或 policy update，因此不能证明角色形成、peer selection 改善、成本下降或任何
方法效果。

本次 judgment 的修复计划针对 `processor.py` 的编码和 envelope，而 producer Qp 已为
PASS；`processor.py` 属于 recipient 自己的工作边界。这暴露出当前“recipient 判断
producer 交付、随后 recipient 自己修复”的责任归因风险：链路可以闭合，但该反馈不能
直接作为上游 producer 的可学习标签。下一步必须在 N03 资格设计中显式区分 producer
artifact defect、recipient-owned integration defect 和 sink adoption defect，并让 eligible
role evidence 只使用归因可验证的标签。

## Goal 对照

| Goal 标准 | 本次状态 |
|---|---|
| 真 API、原始结果和失败可审计 | 满足本次 integration gate |
| situated judgment→action→outcome→evidence 链 | 满足一个受限 episode |
| attribution-valid role learning | 未满足，责任归因风险已确认 |
| benchmark/baseline/方法效果 | 未满足，不能宣称科研结果 |

Goal、benchmark、baseline 和创新标准均未降级。v3 之后不再追加同条件 API 冒烟；应先
修复责任标签与持久 peer state 设计，再进入 N03 的独立 root、strong same-information
baseline 和受控重复。
