# 2026-09-28 故事线与创新点评分

- 状态：PARTIAL
- 评价对象：docs/research/versions/storyline/storyline_v1.0_20260928.md
- 对照标准：docs/research/versions/evaluation/storyline/storyline_v1.2_20260928_eval.md
- goal_change_requested：false
- 评分性质：当前研究文档的标准符合度，不是录用概率，也不是实验效果分数。

## 当前故事复述

我们研究的问题是：

> 在没有预先指定专家身份的协作流中，真正接收并使用交付物的 agent，能否把对某次具体交付的情境化判断，转成可归因的 producer role evidence，在下一次任务执行前改变责任分派，并在未见任务上改善团队质量与完整成本？

故事链为：

真实 producer 交付
→ recipient 真实读取并使用、修改或拒绝
→ 绑定任务、交付、版本和动作的 situated judgment
→ responsibility-aware role evidence
→ 执行前的 future peer/responsibility assignment
→ 未见 task/root 上的质量、返工和完整成本。

主创新目标只有一个：把 recipient 的真实使用判断和责任归因，转成可被未来责任分派使用、并能被后续结果修正的 role evidence。责任面、传播面、时间面是验收维度，不是三个并列算法。文档明确不声称已经实现实时训练、形成 peer 专长、冻结 benchmark 或证明闭环收益。

## 评分方式

由于 v1.2 明确规定证据门不可由写作质量补偿，采用两个分数：

1. **设计/论证完成度**：只评价故事是否已经形成清晰、单一、可证伪的研究计划。
2. **严格证据就绪度**：评价它是否已经满足可写成完整方法论文的因果证据、estimand、baseline、独立任务和复现要求。

最终严格分取两者较低值。这样“故事写得清楚”不会掩盖实验尚未成立。

## 结果

| 维度 | 分数 | 解释 |
|---|---:|---|
| 设计/论证完成度 | **68/100** | 中心问题和唯一机制已经清楚，反驳意识较好；但最小反例、最近邻表和具体论文证据结构仍缺失 |
| 严格证据就绪度 | **34/100** | 当前没有完整箭头证据、预定义 estimand、独立 root/live histories、强同信息 baseline 或闭环结果 |
| **最终严格分** | **34/100** | 按 hard-gate 不可补偿原则取低值 |

## 逐项对照

### A. 问题切口：14/20（设计分）

已满足：

- 一句话问题明确；
- recipient、future assignment 和 multi-agent dependency 是问题必要部分；
- 已写出会否定主张的反驳条件。

未满足：

- 没有一个完整的最小反例：具体 producer、recipient、交付内容、错误的 raw acceptance 选择，以及 situated judgment 如何改变未来分派；
- 没有把“单次 acceptance/terminal reward 为什么无法归因”写成可复现案例。

### B. 创新：13/25（设计分）

已满足：

- 明确只有一个主创新；
- 主动排除了把 JEV、Laya、RLS、SGD、bandit、运行时和 prompt 拼装当作创新；
- 已提出责任、传播、时间三个验收面；
- 已列出 raw acceptance、contextual trust/bandit、terminal-only、pooled controller 等替代解释。

未满足：

- 没有至少五个最近邻的 novelty table；
- 没有具体最小消融；
- 没有预注册的替代解释检验；
- 三个验收面尚未用一张机制图证明它们确实是同一机制的必要条件。

### C. 因果链：10/20

已满足：

- 六段链条明确；
- 要求 producer contract、recipient integration、later outcome 和 UNKNOWN 分开；
- 要求第三方 future owner、assignment freeze、权限和 hash/ID 绑定。

未满足：

- 正文只有规范声明，没有完整 episode 实例；
- 没有展示具体判断如何转成 role evidence，再在执行前改变 assignment；
- 当前真实 v3 没有产生概率变化，不能给闭环分；
- producer 质量和 recipient 自有修改的责任边界还没有被真实数据证明。

### D. Claim–evidence：6/15

已满足：

- 明确区分协议级、信号级、闭环级和泛化级 claim；
- 明确写出当前不主张的内容；
- 没有把工程连通性写成方法效果。

未满足：

- 没有逐句 claim–evidence matrix；
- 没有把贡献绑定到具体代码、配置、原始日志、统计输出和图表；
- “可归因”“可合法传播”“低成本生效”仍是目标，不是证据结论。

### E. 强验证目标：3/15

已满足：

- 要求同信息 baseline、未见任务和完整成本；
- 明确不接受单次成功。

未满足：

- 没有在故事正文中落实多 root、independent live histories、失败/UNKNOWN 分母、效应量和不确定性；
- 没有主质量—成本终点；
- 没有精度或功效理由。

### F. Estimand 与可证伪预测：3/10

已满足：

- 已写出会否定主张的结果类型；
- 成功/失败方向有初步描述。

未满足：

- 没有在故事正文定义 H1 信息价值、H2 闭环 utility、H3 在线代价；
- 没有 primary endpoint、最小关心差异、时间窗、95% 区间和停止规则；
- “改善质量与完整成本”还不是可计算 estimand。

### H. 论文行文主链：2/10

当前故事文档本身是研究设计说明，不是完整论文骨架：

- 已有问题→故事链→创新→不主张→反驳条件→状态的顺序；
- 但没有 Introduction 段落职责、Related Work 分组、Method 输入输出、Experiment H1/H2/H3 顺序和 Discussion 边界；
- 没有逐段规定本段要证明什么、证据在哪里、下一段需要什么输入。

v1.2 已经把这些规则写入评价标准，但规则存在不等于本项目正文已经执行。

## Hard-gate 状态

未通过：

- A：最小反例；
- B：novelty table、具体机制消融、同信息替代解释；
- C：独立箭头证据、第三方 owner 使用、future assignment 改变未见 utility；
- D：claim–evidence matrix；
- E/F：预注册 estimand、主终点、统计和独立确认；
- H：论文行文主链尚未转成实际论文提纲。

当前尚未发现已经触发的一票否决；但若把现有 v3 写成已形成 peer 专长或闭环收益，会立即触发 I 类硬失败。

## 最小修复顺序

1. 在故事文档加入一个可复现最小反例和贯穿 case。
2. 建立五近邻 novelty table，锁定唯一机制、最小消融和等信息替代。
3. 建立逐箭头 claim–evidence 表，至少包含 event_id、artifact hash、权限、owner、时间和 UNKNOWN 规则。
4. 在唯一实验契约中落 H1/H2/H3 的单位、处理、主指标、最小差异/精度、95% 区间和停止规则。
5. 按“是否有效 → 为什么有效 → 何时失效 → 代价”形成实际论文提纲。
6. 只有 C/D/E/F 过门后，才进入新的真实 API 或 A800 主实验。

## 与 Goal 的对照

- 已完成：中心问题、主创新边界、反驳条件和不主张范围已形成。
- 部分满足：故事骨架清晰，但最小反例、最近邻表、段落级论证和实验 estimand 仍缺失。
- 未满足：完整 judgment → role evidence → future assignment → unseen utility 闭环、强 baseline、独立验证和 A800 证据。
- 具体原因：责任归因、producer 质量计分、持久 peer state 与 independent histories 尚未完成；不是 Goal 可以降级。
- 下一步：按上述六步修复，再重新评分。
