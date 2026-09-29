# 2026-09-29 Orca paper-research debate infrastructure

## 任务

调查并启用适合 AAMAS 主线的多 agent paper research / debate 工作流，重点服务当前
benchmark/baseline lock，而不是继续润色摘要。

## 核验到的能力

- `paper-research-pipeline` 明确覆盖 B（benchmark/baseline）、M（method/story）、E（experiment）、D（drafting）、R（revision）阶段；要求至少三个非等价方向、独立角色、最多三轮结构化辩论、证据与 kill criterion、人类决策门。
- `debate_protocol.md` 固定每条意见的 `POSITION/TARGET/EVIDENCE/REASONING/DECISION TEST/CONFIDENCE`，并要求 Round 0 独立、Round 1 交叉挑战、Round 2 回应与综合时保留未决异议。
- Orca runtime `/Applications/Orca.app/Contents/Resources/bin/orca` 版本 `1.4.215`，状态 `ready/connected`，支持 Run、Task、Dispatch、worker lifecycle、消息和 decision gate。
- `paper-reviewer` 适合后期投稿前五角色终审，不替代当前 B-stage debate；`deep-research` 适合来源/证据账本；`storm-research` 适合早期扫描，不作为最终证据。

## 外部调研结果

- 2026 MAD survey 将 debate 拆成参与者、交互机制、协议/裁决等多个维度，并指出若不显式控制这些设计，跨论文比较不可靠。
- ICML 2024 的 MAD 比较研究报告：MAD 不会稳定优于 self-consistency/ensemble，结果对协议和超参敏感。因此我们不能把“多 agent 辩论”本身当成质量保证，必须有同成本对照和停止规则。
- Orca 的公开讨论说明其 coordinator/parallel specialist/worktree 模式与我们的需求相符；这只是工具能力参考，不是论文科学证据。

来源和证据已登记在：
[`docs/research/debates/benchmark_baseline_lock_20260929/sources.jsonl`](../../research/debates/benchmark_baseline_lock_20260929/sources.jsonl)
和 `evidence.jsonl`。

## 实际 Orca 运行

创建了研究 Run：`run_e313af962946`。

- Codex methods worker：Dispatch `ctx_ca4a0507fd7e`，终端接受输入但 turn start 未被观察到，状态为 `start_unknown/unverifiable`；终端尾部显示 Codex self-update 后回到 shell。
- Codex feasibility worker：Dispatch `ctx_f4796d04045b`，同样为 `start_unknown/unverifiable`。
- Claude devil-advocate worker：未创建，Orca 返回 `agent_unconfigured`。

按 Orca recovery contract，这些状态不能被写成成功，也不能把缺失输出当作失败结论；当前 Run 保留为未决状态，不重放同一 mutation，不关闭未证实存活的 worker。

## 结论

最适合项目的不是另造一个“论文辩论 skill”，而是：

```text
paper-research-pipeline/debate_protocol
    + Orca Run/Task/Dispatch/gate
    + deep-research evidence ledger
    + paper-reviewer final five-role review
```

当前 B-stage debate charter 已落盘，但科学辩论尚未完成。不能因为工具链已配置就提前确认
ArtifactRole primary 或冻结 benchmark。

## Goal 对照

| 项目目标 | 状态 | 说明 |
|---|---|---|
| 故事线和方法论不漂移 | `MAINTAINED` | 未修改 active 文档和 Goal |
| benchmark/baseline 选择经过严格审查 | `OPEN` | 只有 charter 与工具协议，尚无完整独立 Round 0/1/2 |
| 多 agent 结论可追溯 | `PARTIAL` | Orca Run/dispatch 已有审计记录；worker 输出未形成科学证据 |
| 不把多数票当创新或真理 | `PASS` | 已写入协议和 claims ledger |
| 是否进入 API/A800 | `NO` | B-stage benchmark/baseline gate 仍未通过 |

## 下一步

在 Orca worker launcher 可用后，继续同一个主题但使用新的、可验证的 worker dispatch；先完成
Round 0，再做交叉挑战和 synthesis。若 launcher 长期不可用，使用本地只读 research agents
完成同一协议，但明确记录不是 Orca worker 结果。无论使用哪种执行器，都必须先完成用户决策门，
再修改 active benchmark plan。
