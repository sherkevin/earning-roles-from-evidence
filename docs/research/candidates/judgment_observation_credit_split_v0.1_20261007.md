# 候选修正：保留评价差异，单独验证后续分派收益

状态：`ACCEPTED_DIRECTION — IMPLEMENTATION_NOT_QUALIFIED`。用户于 2026-10-07 明确确认
方案 B，决议见 [ADR0049](../../user/decisions/0049-separate-judgment-observation-from-credit.md)。
本文件保留推导、备选与争议过程，不是另一份 ACTIVE；生效定义由 canonical registry
登记的方法版本承载。不降低 Goal、评分标准，不修改历史结果。

## 1. 目的与已证实的问题

我们的第一性目标是：接收方实际面对交付物时形成的评价，能否为后续任务的责任分派
提供额外信息，并改善真实质量与完整成本。保护归因是必要约束；若保护规则先删除
所有不同评价，再增加训练轮数，就无法检验这条主张。

当前 `evaluate_source_gate` 的 strict 分支只发布“预注册 producer defect、Qp FAIL、
accept、use、无接收方修改、完整绑定与结果”的源事件；
`score_role_evidence` 只消费 accept/rework/reject 的固定数值，不读理由或置信度。
[源码枚举审计](../../../experiments/logs/n03_judgment_support_audit_20261007_v1/summary.json)
调用了现有函数，2592 个**符号输入组合**仅两行可发布，分别对应 Y PASS/FAIL；
两行 J 都是 1，Qp 都是 FAIL。九组计数对照与下式逐项相等。
它不是 2592 次真实任务、成功率估计或 LLM 实验；全部为 0 API、0 GPU。

## 2. 最小数学说明与实例

只使用两个被测量的量及两个派生量：J 是接收方的类别评价经当前映射得到的分数；
G 是现有源事件发布门的布尔输出；n 是某个候选通过该门的历史记录数；a 是固定
Beta 平滑常数（当前 a=1）。这些不是新模型输入。

$$
J\in\{0,\tfrac12,1\},\qquad G=1\ \Longrightarrow\ J=1.
$$

**Case：** B 交付 `producer.py`，A 评价 `accept_with_rework`，J=0.5。
即使交付摘要正确，当前 strict 门仍不发布；把同一评价换为 `accept`、A 实际原样使用，
且满足其他全部条件，才可能发布。这个例子说明门如何删掉评价差异，不代表评价正确。

$$
\widehat q_B=\frac{a+\sum_{i=1}^{n_B}J_i}{2a+n_B}
             =\frac{a+n_B}{2a+n_B}.
$$

**Case：** B 有两条可发布记录，C 有一条；a=1 时分别为 3/4 与 2/3。
当前同等 base score 下 B 更受偏好，差别完全可由记录数解释，无须读取判断内容。
无历史候选的值为 1/2。记录数本身可能有用，不能据此说选择器必然无效。

$$
\operatorname{Var}(J\mid G=1)=0.
$$

**Case：** 只看进入这条源发布通道的任意非空记录集合，J 永远是 1。
这是该门逻辑的结论，不是从两条符号可发布行估计出总体方差。
它不涉及未被消费的评价文本，也不约束后续任务的 J。

**结论范围必须保持精确：** 当前 C1 在目标任务完成后仍可能把不同的 target J 输入
RARE/linear 更新器；但该 target J 的责任/收益规则未充分验证，更新后的选择目前
只做了 preview，没有真实执行。
因此不能说“整个系统没有学习信号”，也不能把这条 target 更新当成 source J
具有额外信息的证明。仅增加 Qp PASS 的准入分支也无法改变 accept-only 的上述恒等式。

## 3. 三个可行方向与选择依据

| 方向 | 修改和可复用部分 | 能解决什么 | 不能解决什么／停止条件 |
|---|---|---|---|
| A：补全正向质量事件，保留 accept-only | 复用 ADR0047 的 defect/quality 注册 | 修正 Qp PASS 全被排除的问题 | J 仍为常数；不能单独作为本轮答案 |
| **B：评价观测与收益归因分开（已确认方向）** | 复用 ledger、artifact binding、read cut、later assignment 和独立 Qp/Y；新增有类型的观察通道 | 正负评价都可被研究，评价不自动变成正确性标签 | 新通道有噪声，必须证明超过 Qp/计数等强对照；实现与效果尚未验证 |
| C：额外执行反事实替换来估计产出方增量贡献 | 复用既有 C3/counterfactual 资格与匹配产物审计 | 更强地区分 producer 与 recipient 对结果的作用 | 额外执行昂贵；反事实配对不足时仍不识别因果贡献；暂不作为每事件默认机制 |

B 不是已验证创新，也不确定 backbone/updater。它让核心假设重新具有可检验性；
新训练框架、实时性、稳定性和任务泛化仍须按原标准证明。

## 4. B 的具体边界

**第一层：记录“谁评价了谁的哪次交付”。** producer 的任务前材料→交付材料的 diff
与 recipient 的交付后→最终材料的 diff 分开。前者证明交付来源，后者描述后续动作；
不得把 producer 自己写出的代码填进 recipient `changed_paths`。
预注册 actor/version、contract、事件规则；Qp PASS/FAIL 仅实例化这个既定规则，
不能在看到结果后选择哪些 actor 或事件算数。

**第二层：保留有噪声的评价，不宣称为质量真值。** 对绑定正确、责任对象明确且完整
的源交接，保留原始 accept/rework/reject；其语义是“接收方关于交付物的观察”。
必须同时保留责任范围与实际修改，以识别接收方把自己的集成工作误说成上游问题。
纯接收方工作或 mixed 结果不得被转成 producer 奖惩。若模型评错，留下错误并测量，
不能根据后来 Y 修改已经封存的 J。不是所有任意文本评价都因此获得训练资格。

**第三层：后续选择必须真的执行，再检验收益。** 新观察可以作为未来分派的输入，
但发布本身不调用持久更新器。完整未来 assignment/selection/delivery/outcome 绑定
后，才满足 delayed-credit 的绑定前提。现有 `derive_later_credit_from_ledger` 只
验证 lineage，不检查 target 修改归属、Qp 或完整成本，不能直接提供合法 reward；
当前 C1 的 target J→producer 更新仍只作诊断。新通道接训练前必须补足独立的责任、
质量和成本标签规则，且与同信息基线共同验证。source rework/reject 不能直接冒充
producer reward；later task 的质量及完整协作成本也不能自动解释成 producer 的
边际贡献。后续 credit 规则的任何额外放宽须另行论证，不在本候选中暗中包含。

当前 native `RoleEvidenceUpdate` 与 `RoleEvidenceOffer` 要求完整 terminal lineage。
本候选保持该时序：J 在行动前封存，源任务完成后才发布新版本的 observation 视图。
完成前只是 auxiliary observation；不得提前生成 native evidence、回填到旧 read cut，
或把记录时间伪装成可见时间。现有 source-publication/producer-credit schema
不能仅改名后复用；必须显式区分 noisy observation 与 attributable credit。独立审查
确认 native assignment 需要真实 evidence_id；可复用带专用 update_version 的完成
回执作为锚点，但每组 J/A 原生只允许一条 update，观察与归因须从同一锚点作不同
投影，不能追加第二条冒充新事件。该桥与旧 offer/credit 的版本隔离仍待实现验证。

**贯穿例子：** B 提交的序列化结果在 Qp 中 PASS；A 说“要返工”，实际仅补写自己
负责的 `processor.py`。我们可记录 A 对 B 的这次看法和后续行为以审查评价噪声，
但不能据此给 B 贴“错误产出”标签。未来若据这条看法选择或排除 B，这个选择是否
有益仍要由新的已执行任务检验，且与 Qp-only、计数-only 等对照比较。

## 5. 最小验证矩阵：先辨识，再扩大

| 阶段 | 对照／操作 | 通过意味着什么 | 停止或回看条件 |
|---|---|---|---|
| 语义资格，0 API | 固定 delivery、producer diff、Qp、Y、registry；比较三种合法 J–action 配对，在各配对内检验路径变化 | observation 可保留三种值；没有 source policy update；recipient/mixed 不生 producer credit；时序/重复/绑定仍 fail-closed | 错误 J–action 配对必须拒绝；桥接未通过不接 selector；任一失效则不调用 API |
| 真实信号小样本 | 复用 real-producer 接口与 actor 私有历史；预算、样本、提示词、失败规则事先冻结 | 观察自然出现的 J、Qp、动作与 Y，报告完整分母；确认后续选择实际执行 | 信号饱和、资格过低、错归因或完整结果缺失时停止诊断；不追 seed 凑效果 |
| 同信息对照 | count-only/J-masked，Qp-only，terminal-only，raw-J，contextual trust，以及候选方法；相同合法历史、初始预算和探索规则 | 把 J 内容价值与机会数、客观质量、表示和计算量分开 | 某信号部署不可见时只能做信息上界，不冒充公平 baseline |
| 核心效果 | 独立 live histories、真实执行的更新后任务、独立 roots、完整质量/成本/UNKNOWN 与区间 | 才有可能支撑“评价改善后续责任分派” | 同根饱和或仅 propensity 改变不能开科学 gate |

第一阶段是数学/协议资格，第二阶段是有预算的开发诊断，均不声称统计功效或主结果。
共享固定历史用于识别信息差异；在线比较各 arm 必须独立积累历史，不能长期复制
候选方法的已实现历史给 baseline。J shuffle 必须在任务/候选/时间可比层内进行，
否则破坏分布本身会成为新混杂；全 1 的当前源通道 shuffle 则应完全不改变结果。

所有具体实验卡须先冻结自然支持度检查、完整调用预算、分母、成本单位和停止条件；
不得因本审计临时把已有八调用 C1 的固定产物改写成真实 actor 学习流。

## 6. 共同确认与尚未验证的部分

用户已确认 B：将**可见评价观察**与**可归因收益/延迟更新**区分，升级 active method
与对应评价条款，保持 Goal、责任安全、独立实测收益和三份验收标准不降低。
确认不等于实现资格或效果通过；下一步先复用 native ledger 验证 typed observation，
再补足 reward 规则与真实小流卡。此阶段不把既有 C1 调用回写成新方法实验。
