# Task report：parent-side ledger replay gate / 2026-09-27

状态：`PARTIAL`。`goal_change_requested=false`。本任务对应 Goal v1.0 的 ER-G3、ER-G4，
不修改 Goal 标准。

## 目标与冻结条件

目标是让 parent 在任何在线更新前拒绝不可审计的事件链，并把真正中断与错误链区分开。
实现文件为 [`peerrolebench_ledger_replay.py`](../../scripts/peerrolebench_ledger_replay.py)，
运行时不调用 LLM、GPU 或 native grader。真实回放输入冻结为 N02 v3 的
[`ledger.json`](../../experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json)；其摘要和
变异矩阵分别记录在
[`n03_ledger_replay_validation_20260927`](../../experiments/logs/n03_ledger_replay_validation_20260927/)
与 [`n03_ledger_replay_validation_20260927_v2`](../../experiments/logs/n03_ledger_replay_validation_20260927_v2/)。

验证器要求严格的事件 schema 和 hash chain，并回放 selection、task start、delivery、
judgment、action、terminal outcome、role evidence 与 later assignment。默认不完整链为
`INVALID`；只有调用方显式允许时才返回带缺失阶段的 `UNKNOWN`。

## 证据

- 真实 v3 ledger 的 15 个事件完整回放为 `PASS`，两次 delivery、judgment、action、
  outcome、evidence 和一次未来 assignment 的引用关系均重建成功。
- 8 个基于真实 ledger 的变异案例全部符合预期：合法链 `PASS`；重复 ID、record/previous
  hash 篡改、未知事件、retry 和乱序被拒；中断链只在显式允许时为 `UNKNOWN`。
- 主回执使用真实 v3 ledger，并在 v2 配置中记录 validator 与 matrix 的源码 hash；synthetic
  fixture 仅用于单元测试，不进入科学结果。
- 测试命令通过：85 项定向回归测试；`py_compile`；`git diff --check`。

## Goal 对照

| Goal | 状态 | 结论 |
|---|---|---|
| ER-G3 事件可追溯、UNKNOWN 与错误分离 | `PARTIAL` | parent replay gate 已可执行；真实 scorer/operator IPC、完整 runner 和第二结构 root 仍未过门 |
| ER-G4 可审计实验 | `PARTIAL` | config/raw/summary 与逐 case 变异证据已保存；本轮没有真实模型结果 |
| ER-G2 在线更新 | `OPEN` | 验证器不等于更新器，未测实时性、时效性、稳定性或遗忘 |
| ER-G1 科学链条 | `OPEN` | 未证明 judgment 的信息价值、责任归因或未见任务质量/成本收益 |

## 根因、边界与下一步

本轮解决的是“坏账本会污染学习”的工程缺口，不是 benchmark 评分缺口。验证器仍无法
替代 hidden scorer/operator 的独立 IPC，也无法从中断事件推断负标签；异常、retry 和
partial delivery 需要在实际 runner 中定义后再纳入科学实验。

下一步把该 gate 接到真实 producer→recipient runner：每次 role update 前保存 replay
result、ledger hash 和 UNKNOWN 原因，再用同一信息约束比较 no-update、terminal-only、
contextual trust/bandit 与候选更新器。未完成这些资格前不启动 A800，也不写方法效果数字。
