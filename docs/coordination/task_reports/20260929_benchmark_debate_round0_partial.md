# 2026-09-29 benchmark/baseline debate — Round 0 partial

## 任务

在不改变 Goal、active benchmark plan 或 primary/secondary 关系的前提下，完成一次
结构化 Round 0 独立审查，检查 ArtifactRole/PeerRoleBench-TB 与 PeerSelect/IPD 的
主张适配、标签可识别性、baseline parity、在线角色学习和实验停止条件。

## 实际完成

- Orca Run `run_e313af962946` 已存在，配置为只读 B-stage debate；两个 Codex dispatch
  仍为 `start_unknown/unverifiable`，没有可用 worker 报告。
- Claude dispatch 返回 `agent_unconfigured`，没有把它当成实验失败或科学结论。
- 收到两份互相独立的 Round 0 报告：devil's-advocate 与 methods/baseline audit，分别保存为
  `docs/research/debates/benchmark_baseline_lock_20260929/round0_devils_advocate.md`。
- methods/baseline audit 保存为
  `docs/research/debates/benchmark_baseline_lock_20260929/round0_methods_auditor.md`。
- 报告将当前最强拒稿风险收敛为：责任标签不可识别、root/benchmark 未冻结、baseline
  不可执行或不公平、peer 可交换、updater 没有实时性/遗忘证据、scorer 漏检、时间
  泄漏、完整成本缺失，以及组合创新可被强同信息基线解释。

## Goal / 验收标准对照

| Goal / 门 | 当前状态 | 证据与含义 |
|---|---|---|
| situated judgment → role evidence → future assignment | `MAINTAINED` | 本轮没有改变故事；明确当前证据尚未闭合该链 |
| benchmark authority/root 独立性 | `OPEN` | 复核 active evaluation 的 NOT_READY 判定 |
| baseline 同信息、可执行、公平 | `OPEN` | raw projection、RARE adapter、closest published adapter 与统一 runner 仍未齐 |
| 责任归因与 scorer 覆盖 | `OPEN` | 需要 producer/recipient 2×2 factorial 与 mutation matrix |
| 实时训练/稳定/时效 | `OPEN` | 需要具体 updater 和延迟、漂移、遗忘的独立测试 |
| 多 agent debate 可追溯 | `PARTIAL` | 一份独立报告已落盘；Orca worker 尚无可用输出 |
| 是否启动新 API/A800 | `NO` | 仍未达到 benchmark/baseline/scientific signal gate |

## 结果解释

本轮没有产生“主 benchmark 已确定”或“方法有效”的结论。下一步先完成剩余 Round 0
角色报告，再围绕 objection 开 Round 1 交叉挑战；只有 baseline/root/label 三个硬门
通过后，才生成完整 cell manifest 并讨论新的真实流。

## 未完成与原因

- Orca worker 的 turn start 未被观察到，终端仍显示自更新/缺失状态；按 Orca recovery
  规则不能把 `unverifiable` 当成成功或失败，也不能无证据重放 mutation。
- 首次方法审计 worker 因模型容量错误未产出，随后以独立只读审计重试成功；feasibility
  角色仍未产出。因此本报告仍标记为 partial，不提前综合。

## 下一步

1. 获取剩余 Round 0 独立意见，保持报告互相不可见。
2. 建立 support/objection/decision-test matrix，标出所需 artifact 和 kill rule。
3. 只在矩阵完成后开 Round 1；没有用户确认不改变 active primary/secondary。
4. 继续不启动 A800/新效果 API；先完成 baseline adapter 与责任标签资格。
