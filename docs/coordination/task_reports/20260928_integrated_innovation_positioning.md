# 2026-09-28 有机整体创新定位与量化验证

- 状态：PARTIAL
- 对应 Goal：ER-G1（创新性与 sharp 故事线）、ER-G2（方法可验证）、ER-G4（AAMAS 可审计论文）
- goal_change_requested：false
- 真实 API/GPU：未运行；本任务是研究定位、决议和实验指标设计。

## 本任务解决的问题

前一轮评分指出，故事线虽然有单一主机制，但对外如果写成“不是组件组合创新”，会主动削弱贡献；同时只用措辞把组合包装成创新也不可靠。需要把二者分开：

- 论文对外呈现一个完整的、有机的机制和它产生的新系统性质；
- 内部用严格的 matched composition、留一消融、非加性交互和跨 root 结果验证这个主张。

## 已完成

1. 新建并登记 [故事线与创新点 v1.1](../../research/versions/storyline/storyline_v1.1_20260928.md)：
   - 将 situated judgment、责任过滤、延迟更新和 future assignment 写成一个有机闭环；
   - 删除“创新不在组合”的对外否定式表述；
   - 增加整体增量、留一必要性、交互效应和闭环完整性定义；
   - 保留当前尚未证实的状态和反驳条件。
2. 新建 [ADR 0040](../../user/decisions/0040-integrated-mechanism-public-positioning.md)，记录内部审计与论文正文的职责分离。
3. 新建 [有机整体创新量化验证方案](../../research/20260928_integrated_innovation_validation_plan.md)：
   - 用质量—完整成本主指标 M；
   - 定义整体增量 Delta_F；
   - 定义留一必要性 N_i；
   - 定义模块交互 I_ij；
   - 规定 strongest matched composition 和四箭头闭环门。
4. 更新 canonical registry 到 v1.3，并修正方法、benchmark 文档对当前故事线版本的链接。

## 与评分的关系

本任务直接修复此前最低的 B 项（创新识别）和 H 项（论文定位）：

- 原先的问题：内部“不是拼装创新”的审计语言混入了主线定位；
- 现在的处理：正文讲完整机制；内部实验仍要证明它不只是命名或组件堆叠；
- 新增的量化方案会把“有机整体”变成可反驳的实验命题，而不是修辞判断。

这不会自动提高科学证据分。当前 34/100 的严格分仍然有效，因为 matched composition、消融、交互效应和未见 root 结果尚未取得。

## 未完成与原因

- 完整机制尚未在独立 root 上超过 strongest matched composition；
- 尚未完成 J/A/U/F 的真实 factorial 运行；
- 尚未证明四个闭环箭头都成立；
- 未决定最终 updater/backbone；
- 这些是实验和方法资格缺口，不是 Goal 可以降级的理由。

## 下一步

1. 把 J/A/U/F 映射到现有 policy sidecar 和 scorer 合约，先做零 LLM factorial schema/replay 检查。
2. 在不启动新 API 的前提下，检查现有 fixture 是否能产生所有 partial conditions 的可审计 ledger。
3. 仅当责任、producer quality、recipient action 和 feedback semantics 通过资格门后，才设计有界真实 factorial 卡。
4. 重新按 v1.2 故事线标准评分，更新 claim–evidence matrix。
