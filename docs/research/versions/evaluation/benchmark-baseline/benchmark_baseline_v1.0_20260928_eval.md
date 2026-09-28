# Benchmark 与 baseline 评价标准 v1.0

- **状态**：`ACTIVE`
- **评价对象**：[`benchmark_baseline_v1.0_20260928.md`](../../benchmark-baseline/benchmark_baseline_v1.0_20260928.md)
- **用途**：判断实验是否真正能回答故事和方法问题。

## Benchmark 必须通过

1. 至少两个结构不同 root；改 seed/改名不算独立样本。
2. 有真实 producer→recipient 依赖、独立 producer contract、recipient use/rework 和 sink adoption。
3. task/source/tests/expected/scorer/operator ledger/candidate workspace 的可见性和权限运行前冻结。
4. development/confirmation 按 root 划分；不看结果后重切 split、label 或指标。
5. 责任、评分覆盖或隔离不完整时为 UNKNOWN，不能补成负例。

## Baseline 必须通过

`uniform`、`no_update`、`raw_acceptance`、`terminal_only`、同信息 `contextual_trust/bandit`、`pooled_controller` 和主方法共享候选、信息、propensity、预算、成本口径和独立 live-history 规则。训练 updater 的比较必须另列，不能让主方法获得额外记忆。

## 结果必须报告

信息价值、future assignment、官方质量、返工/通信/API/token/tool/scorer/replay 成本、UNKNOWN 分母、update/service latency、状态大小、漂移恢复、旧任务峰值/平均遗忘和失败归因。单一成功率、单一 episode 或零 LLM fixture 不能回答主问题。

## 停止规则

任何 root qualification、scorer/ledger replay 或同信息 baseline 失败，停止该 root 的真实链并保留日志。RARE 未超过 contextual trust 或成本—质量目标不成立时，停止扩展模型/A800，报告未支持的机制。
