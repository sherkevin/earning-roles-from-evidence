# 三份审核标准当前 gate 审计 — 2026-10-01

状态：`PARTIAL`。本报告只更新证据状态，不修改 Goal、active storyline、active method 或
active benchmark/baseline 版本，也不把工程资格升级为科学结果。

## 审计输入

- 故事线与创新评价：`storyline_v1.3`；
- 方法论评价：`method_v1.2`；
- benchmark + baseline 评价：`benchmark_baseline_v1.2`；
- 最新真实 CPU 资格回执：
  [`n03_pipe3_two_stage_composition_20261001_v4`](../../../experiments/logs/n03_pipe3_two_stage_composition_20261001_v4/);
- 过程与失败回执：[`PIPE3 P0 report`](20261001_pipe3_p0_repairs.md)。

## 当前判定

| 审核文档 | 已关闭的门 | 仍未通过的硬门 | 当前状态 |
|---|---|---|---|
| 故事线与创新点 | 问题对象、责任边界、两阶段时序和可证伪边界已在文档中明确；P0 资格回执补强了因果链的可审计性 | 尚无独立 root 上的真实 recipient judgment→future assignment→unseen utility 证据；同信息替代解释尚未被排除 | `NOT_READY` |
| 方法论 | source attribution、public evidence、assignment-before-selection、terminal delayed credit、UNKNOWN/no-update、native/auxiliary replay 在同 root qualification 中可重放 | 没有独立 live histories、四格科学消融、真实 judgment 生成质量、在线延迟/吞吐/遗忘测量；因此实时角色学习效果未被识别 | `NOT_READY` |
| Benchmark + baseline | TeamBench authority、ArtifactRole/PeerSelect 轨道边界、baseline 角色和 cell manifest 要求已明确；v4 验证了一个 root 的 runner 接缝 | benchmark root 尚未冻结；第二 root authority 未确认；closest published adapter、live same-information parity、完整成本、precision gate 和科学结果均未通过 | `NOT_READY` |

## v4 能支持什么

`producer_owned` control 真实调用 pinned CPU sandbox scorer，获得 producer objective
`FAIL`，随后完成责任合格、不可变公开 evidence、隔离读取、执行前 assignment、下一次
selection、terminal outcome 和一次 delayed update。`recipient_owned` 与 `mixed` controls
都被责任门保护性地停在 `UNKNOWN/no-update`。native manifest root 和 auxiliary manifest
root 均通过 replay；runner 报告 `QUALIFIED_OFFLINE`、`contract_passed=true`、0 LLM API、
0 GPU、`scientific_claim_allowed=false`。

这证明的是候选协议在同一 structural root 上的工程可重放性。它没有证明判断模型的质量、
角色专长、跨任务迁移、实时训练收益或团队质量—成本改善。

## 三份文档离通过还差什么

1. **Benchmark 先于效果实验冻结**：解决第二 structural root 的 authority 选择，写入
   root/source/generator/scorer/seed split manifest，并完成 contamination、可见性和
   clean replay 审计。没有这一步不能把 `PeerRoleBench-TB` 写成已通过 benchmark。
2. **Baseline 先于真实比较冻结**：统一 runner 必须在相同 menu、事件、propensity、成本和
   UNKNOWN 规则下可执行 `uniform`、`no_update`、`raw_acceptance`、`terminal_only`、
   strong contextual trust、closest published adapter 和 RARE；离线 matrix 通过不等于
   live parity 通过。
3. **方法科学识别**：在确认 root 上生成独立 live histories，先做 information-value
   （situated judgment 对 later-use/contract 的增量），再做 future assignment/utility，
   最后测 update latency、backlog、state size、drift recovery 和 forgetting。每格必须有
   预注册 primary endpoint、失败/UNKNOWN 分母和 95% 区间。
4. **故事线证据闭环**：只有 `judgment → attributable evidence → pre-execution assignment
   → unseen outcome` 在独立 root 和强同信息 baseline 下成立，才能把“自进化角色学习”写成
   结果；否则只能声称协议和责任安全边界。

## 下一步唯一短路径

不再重跑已经通过的 v1.2 local transport。先完成第二 root authority 的共同决策材料和
baseline live-runner parity qualification；随后才提交一条有明确成本上限的真实 API 小流。
在这些门通过前不启动 A800，也不修改 Goal 的标准或把 `QUALIFIED_OFFLINE` 写成科学效果。

## 2026-10-02 反馈通道与 evidence-consumption 复核

v1.3 的显式 policy factory 已经接入，但独立 parity review 发现两个不能忽略的识别问题：

1. `credit_committed` 不能单独作为通过条件。当前 composition 固定构造
   `terminal_outcome`；因此声明 `recipient_judgment` 或 `raw_acceptance` 的 arm 若没有实际
   对应 update，必须是 `UNKNOWN`。这一点已由 contextual-trust 负向测试固定，历史回执不变。
2. 当前 target selection 仍使用 hand-authored base-score overlay，role evidence 只检查
   最终 selected candidate 有 published evidence。把同一 candidate 的 evidence
   `quality_score` 从 1.0 改为 0.0，在 menu/base-score/RNG/state 全部不变时，chosen index 和
   probabilities 不变。因此这条 composition 只能证明 lineage 和 assignment 顺序，不能证明
   selector 消费 evidence，更不能识别 update→future choice 的效果。

这两个问题没有降低任何验收标准；它们把 baseline live parity 的前置门收紧为“每个 arm 的
合法 public feedback adapter + 可识别的 evidence-to-decision mutation”。详见
[`PIPE3 feedback-channel gate`](20261002_pipe3_feedback_channel_gate.md)。三份科学 gate 仍为
`NOT_READY`，不启动 live parity cell 或 A800。

一个无状态 `role-evidence-judgment-beta-v1` assignment comparator 已作为可复用的 public
judgment 输入适配器实现，但只完成离线定向测试。它不改变持久状态，也没有接入七 arm live
runner；因此不能关闭同信息 baseline、独立 live history 或 evidence-to-decision 因果门。
