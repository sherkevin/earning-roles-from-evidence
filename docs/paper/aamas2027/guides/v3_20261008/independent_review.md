# Guide v3 多角度独立审查

日期：2026-10-08。三位只读 Codex `gpt-6-sol` 审查员；无新实验、搜索或改写研究规范。
这份记录保存首轮反对意见与修复后的判定，不能只保留最后的 GO。

**最终结论：条件研究指南 `GO`；真实方法均值、排名、误差预测 `NOT_IDENTIFIED / NO-GO`。**
二者不是同一个 gate。当前 Guide 可以指导验证合理的赢、平、输，尚不能为科学家提供
高置信度的真实结果分布，更不能填正文实测结果。

## 第一轮：v2 没有通过的地方

| 审查员 | 角度 | 原判定与关键理由 |
|---|---|---|
| `/root/guide_v2_benchmark_review` | benchmark/baseline、权威性、公平性 | v2 是条件模型，不是方法效果 forecast；root、later-use、强对照和 closest adapter 未科学资格化；S0–S4 不对应命名方法。 |
| `/root/guide_v2_effect_review` | 效果、误差、联合分布、一致性 | 条件算术基本通过；潜在 q/κ、成本、方差未拟合；oracle p=q+e、不同选择人群、强制返工费用及 UNKNOWN 都可能改变效果解释。 |
| `/root/guide_v2_advantage_review` | 优势、不足、机制与反证 | 缺“机制→条件→匹配对照→指标方向→代价→反证”；冷启动、错误/旧判断、漂移和高服务成本的失效方向不足。 |

一致意见：不能用数学计算正确证明真实方法优越，也不能为让表格显得真实而人为安排
RARE 在某些格输。优劣方向必须来自机制和明确条件。

审查额外核对 10 月 8 日的真实职责诊断与任务条件 ridge 报告：前者两次真实判断后
因 datetime 空格/T 的事实误判停止，未执行未来任务；后者仅通过人工交叉偏好的离线
代数控制。它们强化噪声观察与强对照要求，没有识别方法效果。C1 的八次调用是单独的
冻结快照，不能说成项目全部调用总量。

## 第二轮：v3 初稿仍被指出的问题

| 问题 | 修复 | 证据位置 |
|---|---|---|
| Qp-only 混入合法 live 对照 | private/target Qp 仅用于评价或 oracle 诊断；过去检查只有 read cut 前已合法公开才可作输入 | v3 第2页预测比较段 |
| 强任务条件对照仅列为可选诊断 | task-conditioned ridge 与 matched composition 的独立 live parity 是匹配机制归因前置条件；现有八行不足的集成缺口明确列出 | v3 第1页表与脚注 |
| 正文 ΔA↑ 被误当成功方向 | 明确须在 confirmation 前去箭头或重定义；本次只登记集成待办，不改正文 | v3 第2页开头 |
| prediction 标签/时点混淆 | Qp 与 later-use Y 分别定义预测和损失，不混合；选中 propensity 不等于正确率 | v3 第2页预测比较段 |
| gate 公平性可能抹掉其代价 | 匹配原始机会集/标签可用规则，分别报告门控后 eligibility、coverage、UNKNOWN | v3 第2页公平段 |
| constant-J 反证列方向含混 | 改为“Against a claimed benefit”；mask 后仍有效反对 J 增量主张 | v3 第2页条件表 |
| L2-public 似乎已有公开同口径结果 | 明确是 published Meta-Team L2 启发的受限候选适配器，无同口径公报且未资格 | v3 第1页对照表 |
| owner gate 被误认为能纠正 J 事实错误 | 直接写清归属安全与事实准确性不同 | v3 第3页机制表 |
| 重加权/预测评价可能补造未选结果 | 同一真实已选 holdout；跨策略需 overlap/positivity 与权重不确定性，无覆盖则限制结论 | v3 第2页预测比较段 |
| exact break-even 显示 -0.000 | 生成器对绝对值 <1e-12 规范为0，PDF显示 +0.000 | B2 与计算JSON |

首稿源、生成器、参数、计算、PDF、日志与 hash 全部保存在版本包 `pre_review/`；修复
不覆盖历史首稿。v1/v2 的固定 PDF、原计算和失败记录不变。

## 第三轮：实际修复稿复核

- benchmark/baseline 审查员：**“P0 is closed. v3 is GO as a conditional research guide.”**
  同时判定 empirical forecast `NO-GO`；正文矩阵和 ΔA 箭头的集成仍 pending。
- 效果一致性审查员：**“guide 逻辑 GO；真实效果预测 NOT_IDENTIFIED。”**
  七例 ΔU、.3125 阈值、.8 反转点、UNKNOWN 界一致，无剩余计算阻断项。
- 优势/不足审查员：**“Guide v3: GO as a conditional research guide. Empirical forecast gate: not passed.”**
  有利和不利条件来自机制，未给 RARE 安排排名，也未降级 Goal 或否定已确认创新。

以上是审查员的最终短判定摘录；详细意见和修复映射保存在本记录与
[`review_rounds.json`](review_rounds.json)。没有把审查一致意见解释成效能证明。

## 可复算边界与剩余工作

七例均由 ΔU=ΔQ−0.1ΔC 推出。B0/B3/B4/B5 负，B1/B6 正，B2 零；输入是手设的
代数应激点，不是方法预期均值。v2 费用模型中 Δκ>.3125Δh，Δκ=.25 对应额外
h=.8 的 break-even，显示该简化费用模型对路由收益惩罚偏弱。UNKNOWN 示例为
候选 [.5525,.7025]、对照 [.588,.608]，不能建立无缺失机制假设的稳健排序。

仍需：合格独立 roots、同信息强基线的真实 parity、各臂未来任务与独立历史、完整费用、
自然 judgment 支持度、合法 credit、独立 owner 真值、联合误差拟合与留出覆盖/宽度。
这些缺口不是撤销故事线或创新点的授权，而是下一步验收工作的对象。

正文集成：ΔA 方向、Qp/Y 的预测标签与时点、强任务条件/组合对照及完整服务指标，均须
在确认卡与论文表格同步；本次没有宣称这些已完成。
