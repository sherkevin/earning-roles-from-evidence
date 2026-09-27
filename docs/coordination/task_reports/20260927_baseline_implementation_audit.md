# 2026-09-27 baseline implementation audit

## 任务对应的 Goal 硬标准

本任务对应 Goal v1.0 的 benchmark/baseline 真实性、同信息公平比较和“不能把方法名字当成结果”三条标准。它也为 N04/N05 提供入口条件。

## 运行前冻结与实际证据

本任务在审计前固定读取 candidate manifest v2、Stream-JEV reference runtime、当前 DIST1 runner 和 PIPE3 adapter；没有新增 LLM API、没有 GPU、没有修改历史实验结果。执行了：

```text
python3 -m pytest -q references/aamas/streamjev_20260924
```

结果为 `15 passed`。原始历史 logs 仍保留在 `references/aamas/streamjev_20260924/experiments/logs/`，本任务报告不将其重算为新的论文结果。

## 结论

审计报告见 [`docs/research/n03_baseline_implementation_audit_20260927.md`](../../research/n03_baseline_implementation_audit_20260927.md)。结论是：manifest 的 baseline 矩阵在设计层面完整，但代码层面只有 RLS、均匀/无反馈 synthetic control、terminal feedback 协议和历史 challenger；`raw_acceptance`、`contextual_trust`、`pooled_controller`、RARE、online logistic、periodic refit 尚未成为可运行的 peer-role policy。当前不能冻结 benchmark/baseline，也不能启动新的真实 API 或 A800。

## Goal 对照

| 标准 | 状态 | 原因 |
|---|---|---|
| situated judgment→role evidence 主线 | `MAINTAINED` | 没有改动故事或 RARE 候选合同 |
| 权威 benchmark 与双 root | `OPEN` | PIPE3 runner/scorer 过程隔离仍未资格化 |
| baseline 足以排除替代解释 | `PARTIAL` | 名单已定义，多个条件没有统一 runner 实现 |
| 实时性/稳定性/准确率科学证据 | `OPEN` | 现有 15 项是 runtime 回归；历史 synthetic 不是 role efficacy |
| Goal/创新点不静默降级 | `UNCHANGED` | `goal_change_requested=false` |

## 下一步

先实现并审计统一 `BaselinePolicy` 接口下的 uniform、真正 no-update、terminal-only 和 same-information contextual trust；再把 RLS/RARE 接入同一 ledger。没有信息公平和责任归因通过，不启动新的真实 API 或 A800。

## 用户决定

不需要用户决定；本任务只是证据审计，不新增或修改决议文件。
