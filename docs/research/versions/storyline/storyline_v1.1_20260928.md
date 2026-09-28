# 故事线与创新点 v1.1

- **状态**：`ACTIVE`
- **生效日期**：2026-09-28
- **类别**：storyline
- **前一版本**：storyline_v1.0_20260928.md
- **权威入口**：[`docs/research/canonical/README.md`](../../canonical/README.md)
- **目标约束**：[`docs/coordination/GOAL.md`](../../../coordination/GOAL.md) v1.0

## 1. 一句话问题

在没有预先指定专家身份的协作流中，真实接收并使用交付物的 agent，对这份具体交付的情境化判断，能否成为可归因的 producer role evidence，改变下一次执行开始前的责任分派，并在未见任务上改善团队质量与完整成本？

这条问题把“别人评价过 agent”收紧为：谁在什么依赖情境下看到了哪份交付、采取了什么行动、这个行动是否能归因给 producer，以及证据是否在下一次执行前被合法使用。

## 2. 故事链

```text
真实 producer 交付
  → 真实 recipient 读取并使用/修改/拒绝
  → 带交付、任务、版本和动作绑定的 situated judgment
  → responsibility-aware role evidence
  → 尚未执行前的 future peer/responsibility assignment
  → 未见 task/root 上的质量、返工与完整成本
```

故事必须同时保留三点：agent 的能力和 workflow 可以随共同规则自然变化；不存在预设的专家身份；局部判断只有在责任和使用证据可追溯时才可影响未来职责。一个独立 judge 分数、acceptance rate、终局成功率或 prompt 中的角色名都不能单独完成这条链。

## 3. 核心创新主张（目标，尚未被实验确认）

本项目只把一个机制作为主创新目标：**把真实 recipient 的、带责任归属和实际使用证据的 situated judgment，转成可以在未来职责机会中使用的 role evidence，并允许后来的可观测结果安全地修正它。**

论文对外不把机制拆成若干互不相关的工程组件，而是把 situated judgment、责任过滤、延迟更新和 future assignment 写成一个有机闭环：它的创新主张是，这个闭环在同样信息、预算和候选集合下产生了单个组件或已有组合无法产生的可验证系统性质。内部仍须用 matched composition baseline、留一模块消融和交互效应检验这个主张；论文正文只呈现已经被证据支持的整体机制、设计动机和后果，不主动用组件清单削弱贡献。

当前创新的三个可检验面：

1. **责任面**：recipient 自己的正常 integration 不会被误当成 producer 缺陷；producer contract、recipient action、later outcome 和 `UNKNOWN` 分开记录。
2. **传播面**：证据能在直接评价者之外被合法的 future owner 使用；否则只是私有信任 `B_u(v,c)`，不是公共角色证据 `P_v(c)`。
3. **时间面**：每条合法 selected-only feedback 能低成本生效，同时测量 drift 响应、旧任务保持、延迟/乱序反馈和完整更新成本。

这三面是创新的验收维度，不是三个并列算法。任何新增模块必须说明它属于哪个面，并用消融证明不是它偷偷提供了全部收益。


## 3.1 有机整体的创新判定（内部验证，论文正文不直接呈现审计语言）

“组合形成创新”必须落到系统性质，而不是命名。设完整机制模块集合为 F，候选模块子集为 S，在完全相同的信息、候选集合、探索机会、模型/API、成本和任务流下，令 M(S) 为预注册的质量—成本主指标。

内部至少报告：

1. **整体增量**：Delta_F = M(F) - M(empty)，并与最强同信息 baseline 的增量比较；
2. **留一必要性**：对每个模块 i，报告 N_i = M(F) - M(F without i)，检验移除该模块是否破坏对应的责任、传播或时间性质；
3. **组合交互**：对预先指定的模块对，报告 I_ij = M(F) - M(F without i) - M(F without j) + M(F without i and j)。正的、跨 root 稳定的 I_ij 才能支持“有机协同”，不能只凭模块数量或命名；
4. **匹配组合对照**：把已有组件按最有利方式组合成 control，并保持输入、预算和状态容量一致；整体机制必须在至少一个未见 root 上保留增量；
5. **闭环完整性**：situated judgment、attributable evidence、future assignment 和 unseen utility 四个箭头分别有证据，任何箭头缺失都不能把整体写成已验证。

论文正文中的表述应围绕“完整机制解决了什么可识别限制、产生了什么新的系统性质、何种条件下失效”，而不是罗列组件来源。上述量化审计保留在内部实验报告和 supplementary，避免把诚实的内部边界审计写成主动削弱贡献的正文句子。

## 4. 明确不主张

当前不主张已经实现实时训练、已经形成 peer 专长、已经冻结 PeerRoleBench-TB、已经证明 RARE 优于 trust/bandit，或已经有 A800 方法效果。workflow 搜索、能力学习、贡献分配和信誉传播只有在它们共同构成并支撑这个闭环时才作为整体机制的一部分出现；不能把它们写成互不相干的多个贡献。若 workflow 在实验中实际被冻结，结论必须收窄为固定任务图上的职责选择。

## 5. 反驳条件与范围

以下任一结果会否定当前主张而不会自动降低 Goal：recipient judgment 与独立 later-use/contract 结果没有增量信息；第三方 owner 不能据此改变合法 assignment；同信息 trust/bandit 在相同预算下复现全部收益；或更新成本、遗忘和错误归因抵消质量收益。此时保留真实失败证据，并由用户决定是否修改研究问题。

## 6. 当前状态

故事线已收敛；核心机制仍是待验证目标。N02 的两条有限真实链没有产生选择概率变化，N03 的 benchmark、强 baseline 和最终 updater 仍未冻结。任何论文摘要或标题不得把候选机制写成已证实结论。

## 7. 对照标准

审查本文件使用 [`storyline_v1.2_20260928_eval.md`](../evaluation/storyline/storyline_v1.2_20260928_eval.md)。方法细节只见 [`method_v1.0_20260928.md`](../method/method_v1.0_20260928.md)，实验对象只见 [`benchmark_baseline_v1.0_20260928.md`](../benchmark-baseline/benchmark_baseline_v1.0_20260928.md)。
