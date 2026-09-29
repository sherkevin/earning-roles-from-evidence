# Closest published adapter audit — 2026-09-30

## 结论

严格按 ArtifactRole 主轨的因果单位审查，没有找到一个可以直接复现、无需新增责任协议的已发表 drop-in baseline。必须同时具备真实 artifact handoff、recipient judgment/use/rework、producer attribution、selected-only denominator、arrival/correction 语义和 later assignment 的候选目前为 `NO-GO`。这不是把 Goal 降级，而是把“closest published”从一个名称要求收紧成可执行的同信息资格门。

允许对论文语义做独立、可审计的 adapter 时，唯一值得进入候选表的近邻是 **Meta-Team L2-style downstream reflection/profile**：

- 论文：`arXiv:2605.29790v1`；本地一手材料见 `references/aamas/acquisition_followup_20260922/`。
- 代码锚点：`36dc85d9dc2219d292fa180f347479738a84acb2`。本地源码未发现明确 LICENSE/COPYING，因此不复制代码，只按论文公开语义独立重实现。
- 语义：L2 在任务后基于交互轨迹和终局结果更新 teammate profile，L3 可修改 team scaffold/组织，开放 roster 可用于后续 recruitment/structure。
- 当前状态：`NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`，不是已通过的 baseline，也不能把独立 adapter 写成 upstream reproduction。

## 为什么 Meta-Team 最接近但还不能直接当作公平 baseline

| 维度 | Meta-Team 原生语义 | ArtifactRole 所需的公平 adapter | 缺口/风险 |
|---|---|---|---|
| 反馈来源 | 交互轨迹与任务终局 `r_k` | 公开 delivery → recipient judgment/use/repair → arrival 事件 | 原生会看到终局和整段轨迹，不能直接放入主同信息比较 |
| 状态 | teammate profile、team scaffold | 绑定 `source_event_id`、producer/recipient、arrival watermark 的 profile | 需要冻结 schema、容量和更新摘要；不能让 profile 自由读 hidden scorer |
| 传播 | 后续 recruitment/组织结构 | 下一 episode 执行前的 future assignment | 必须证明 assignment 只读已到 watermark 的 profile |
| 责任 | pair/team 级反思，不是 producer defect 的独立归因 | producer contract、recipient 自有工作、adoption 分开计分 | 没有原生责任归因、selected-only 分母 |
| 时序 | 任务完成后更新 | selected-only、延迟、乱序、correction/replay | 需要公共 sidecar 和不可回写的 decision cut |
| 成本 | 原论文可记录调用预算/轨迹成本 | producer、recipient、judge、通信、返工、scorer、replay 全成本 | 需统一成本账和相同预算 |

因此候选必须拆成三个明确层级：

1. `MetaTeam-L2-original-info`：保留论文原生终局/轨迹信息，只做信息上限诊断，不进入主同信息效果比较。
2. `MetaTeam-L2-public`：只读 ArtifactRole 的公开 delivery、recipient judgment/use/repair、arrival/correction 事件；profile schema、摘要规则、调用上限和 assignment 解析必须预注册。
3. `MetaTeam-L2-ablation`：profile-only/no-L3，用来区分 qualitative profile 与 team-structure effect。

若不能固定 profile parser、摘要预算和信息边界，宁可将该候选标为 `NO-GO`，不能用手写 trust score 或确定性规则冒充 Meta-Team。

## 其他候选的定位

- **DecisionBench**（论文 `arXiv:2605.19099v1`，代码 `08da513de448610cbe2f824989203edd73451f3c`，数据 `614f9ef2aa06ba6dffbe539bf31a36e36ad4557c`）：可作 delegation/selector control；没有执行中 recipient adoption、producer attribution 和 later duty update，不能承担 closest ArtifactRole causal unit。
- **CooperBench**（固定仓库版本见 `references/aamas/cooperbench_20260923/`）：适合作 code-collaboration engineering substrate；原生没有 recipient verdict/adoption/later assignment，且存在 `solo-agent1` fallback，不能承担主轨 closest claim。
- **graph-ipd/PeerSelect**（MIT，固定 commit `00ef417f60053569175b2b50d0f0e25ff8eb7007`）：适合作 PeerSelect 机制副轨，不是 ArtifactRole 的 published closest。

## 主轨冻结前的 NO-GO 闸门

Meta-Team-style public adapter 只有在下列条件都通过后，才可进入主轨 baseline cell；否则保持 `NOT_FROZEN`：

- 共享同一公开 delivery/judgment/action/terminal sidecar，但不读取 hidden grader/private policy state。
- 只对 selected interaction 更新，明确 eligible、UNKNOWN、unselected 分母；UNKNOWN 不作为负例。
- profile 每条记录绑定 source event、producer、recipient、arrival index 和 model/config digest，并可从 snapshot 恢复。
- profile schema、摘要模型/规则、调用上限和 profile→assignment 映射在执行前封存。
- assignment 在执行前消费已到 watermark 的 profile，不能读当前 episode 结果或未来 terminal outcome。
- 支持迟到、乱序、correction、duplicate 和 replay；已封存 decision 不回写。
- 记录并对齐完整 producer/recipient/judge/scorer/repair/replay 成本。
- 每个 arm 使用独立 live history、同一 root/schedule 和相同公开信息，后续 assignment 真正作用于下一 episode。

## 对 Goal 和下一步的影响

本审计没有改写故事线、方法或 Goal，也没有启动 API/GPU。它把 benchmark 文档中的“closest published adapter”从占位符变成了可审查的候选与严格失败边界。下一小任务是只做 `MetaTeam-L2-public` 的零调用 schema/信息边界 qualification；在该 qualification、PIPE3 live runner、独立 history、later assignment 和完整成本都通过前，不启动正式效果流或 A800。
