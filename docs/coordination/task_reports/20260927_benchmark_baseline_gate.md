# Task report：benchmark / baseline freeze gate / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## Goal 对照

- **ER-G3**：把两个 root、信息边界、baseline 和 split 的硬门写成候选 manifest；尚未取得两个 root 的运行资格。
- **ER-G4**：固定主指标、成本和 UNKNOWN/停止规则；没有新的 LLM、GPU 或科学结果。
- **ER-G1/ER-G2**：故事和 RARE 方法合同保持不变；backbone/update 仍未锁定。

## 本轮输入与证据

本轮只使用固定 TeamBench 源码静态审查、PIPE3 材料适配器和
[`20260927_second_root_audit.md`](20260927_second_root_audit.md)。没有调用 LLM/API、
没有启动 Nebula/A800，也没有修改历史日志。候选合同见
[`n03_benchmark_baseline_freeze_candidate_20260927.md`](../../research/n03_benchmark_baseline_freeze_candidate_20260927.md)，
决策见 [ADR 0034](../../user/decisions/0034-benchmark-baseline-freeze-gate.md)。

## 结论

当前不能声称 benchmark 或 baseline 已冻结。PIPE3 仍是条件性主候选，MULTI3 是低优先级
fallback；DIST1 仅作 development/诊断候选。首轮 baseline 必须共享候选集合、propensity、
任务/模型/API 预算、合法信息、延迟事件和完整成本，至少包含 uniform、no-update、raw
acceptance、terminal-only、同信息 contextual trust/bandit、pooled controller 和 RARE。

下一小任务是补齐 root manifest 与权限/评分/ledger 的实际边界，然后在看到 confirmation
结果前封存一张小批量开发卡；资格门失败时保留 UNKNOWN，不降级 Goal，不开 A800。
