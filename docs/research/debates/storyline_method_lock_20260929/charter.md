# Storyline–method lock debate charter

- **日期**：2026-09-29
- **状态**：`OPEN / Round 0 complete; Round 1 pending`
- **目的**：审查当前生效故事线与方法论是否已经组成一个 sharp、可识别、可运行、可证伪的 AAMAS 贡献。
- **范围**：只审查故事线—方法论的一致性及其对 benchmark/baseline 的后果；不在本轮冻结新算法、benchmark 轨道、backbone 或实验结果。
- **禁止事项**：不把协议 qualification 写成科学效果；不把缺失的 worker 输出当证据；不因负面审查自动降低 `GOAL.md`。

## 规范依据

1. [storyline v1.1](../../versions/storyline/storyline_v1.1_20260928.md)
2. [method v1.0](../../versions/method/method_v1.0_20260928.md)
3. [storyline evaluation v1.3](../../versions/evaluation/storyline/storyline_v1.3_20260928_eval.md)
4. [method evaluation v1.1](../../versions/evaluation/method/method_v1.1_20260928_eval.md)
5. [benchmark/baseline evaluation v1.2](../../versions/evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md)
6. [project goal](../../../coordination/GOAL.md)

## 中心问题

现有闭环能否把真实 recipient 对具体交付的、责任可归因且绑定实际使用的 situated judgment，转化为可传播 role evidence，由未来 owner 在执行前用于 assignment，并在未见任务上改善质量与完整成本；同时，方法是否给出了唯一可重放的更新与选择算法，使这一增量不能被同信息 contextual trust/bandit 解释。

## 待审查命题

- **C1 sharpness**：问题切口是 MAS 必要的单一问题，而非“互评/信誉/工作流/训练”并列包装。
- **C2 novelty**：责任归因、实际使用、跨 owner 传播和迟到纠错形成的整体有可识别增量。
- **C3 algorithm**：RARE 是否已从接口合同闭合为唯一可执行算法，包含目标、状态、更新和 assignment。
- **C4 signal**：situated judgment 对独立 producer contract/later-use 目标具有非循环的信息增量。
- **C5 persistence**：peer 的持久经验/能力差异使 role evidence 有机会改变未来产出，而非只改变身份偏好。
- **C6 online properties**：realtime、timeliness、stability 和完整成本能被分别测量。
- **C7 benchmark alignment**：ArtifactRole 主链与 PeerSelect 机制轨道分开，benchmark、baseline、root 和 cell manifest 能识别 C1–C6。
- **C8 writing logic**：标题、摘要、引言、方法、实验和讨论沿同一条因果链推进，不把未证实结果写成贡献。

## 辩论协议

- **Round 0**：独立报告，不看其他报告；每份使用 `POSITION/TARGET/EVIDENCE/REASONING/DECISION TEST/CONFIDENCE`。
- **Round 1**：逐项交叉质疑，要求回应最强反对意见并区分事实、推论、待测假设。
- **Round 2**：管理者综合；保留少数意见，提出不改 active 文档的最小修正卡与 kill criteria。

本轮使用本地独立审查 agent 和 Orca orchestration。Orca 只能作为过程证据：worker 必须有可验证输出才能进入科学综合。

**Provider constraint**：所有后续科学子 agent 必须使用 Codex `gpt-6-sol`，并继承主 agent 的 AK/权限。Orca 的 `opencode`、MiniMax 或其他 provider 输出不进入科学证据；如果平台默认路由到这些 provider，只记录为过程失败。

## 决策门

本轮不会自动修改六份 canonical active 文档。若形成需要改变研究含义的共识，先写候选变更与 ADR，等待用户和助手双重确认；工程性任务可直接写 task report 并保持 active 文档不变。
