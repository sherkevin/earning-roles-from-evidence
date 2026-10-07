# 评价支持度审计与观察／收益分离 — 2026-10-07

状态：`PARTIAL`；`goal_change_requested=false`。对应 ER-G1/ER-G2/ER-G3/ER-G4。
目的：在付出下一轮实验成本前，确认数据能否识别“评价改善未来分派”。衡量标准为
源 J 支持度、计数对照、责任/reward 边界和实际协议可达性，不用测试条数替代科学进度。

## 结果与证据

当前 strict source gate 要求 accept、原样 use、Qp FAIL；scorer 只消费 J 的类别映射。
因此已发布源 J 恒为 1，Beta 均值退化为 `(a+n)/(2a+n)`。这条 source overlay 的变化
可由事件数完全解释，尚不能证明评价内容增量。补 Qp PASS 分支仍不能修复 accept-only。

[审计脚本](../../../scripts/peerrolebench_judgment_support_audit.py)直接调用当前实现，
[配置、原始逐行输入/输出与汇总](../../../experiments/logs/n03_judgment_support_audit_20261007_v1/)
先配置后执行：2592 个符号组合仅两行可发布，J 支持集为 `{1}`；9 组 scorer 与计数
公式精确相等。枚举包含拒绝测试的非法组合，**不是 2592 个真实或合法任务样本**，
不估计成功率。无 gate 时三类 J 可以改变原 scorer，说明问题在过滤后的支持度。

结论只限源通道。C1 的 target J 可不同，并已输入 delayed updater；但其责任/收益
语义不足，更新后的选择也只预览未执行。不能扩写成“所有评价无用”或“模型不能学习”。
本轮新增真实 API 调用和 GPU 作业均为 0。

随后对既有 real-smoke v2–v6 全部五轮做了
[事后真实记录清点](../../../experiments/logs/n03_real_actor_judgment_census_20261007_v1/summary.json)，
不重跑模型或评分器：Qp 五次 PASS，J 五次 accept_with_rework，**没有 J 类别差异**。
三轮可比的实际 repair 仅修改 recipient-owned `processor.py`；两轮 consumer 解析失败，
动作及终局 UNKNOWN；仅 v3/v6 有 native terminal outcome。原始字段和文件摘要逐行保存。

这不能推断“五次 judge 都判断错误”：需要集成可以是正确的行动计划。它证明不能
直接把 rework 当作 producer 错误标签。新观察通道解除门控删样本，不会自动让这批
饱和任务获得区分度。五轮同 root/seed 且协议改变，既不能估计独立准确率，也不能
事后声称满足新合同的准入。下一轮优先核验 public producer contract、recipient
integration 与判断问题的语义是否真正分开，而不是增加同一任务的调用或训练轮数。

## 多轮独立审查及纠正

真实提示词的[逐轮作用域审查](../../../experiments/logs/n03_real_actor_judgment_census_20261007_v1/prompt_scope_review.json)
进一步确定原因：请求虽然写着 review delivered producer，却附带整体集成任务，
并直接把同一评价类别映射成 consumer 的 use/repair/redo。五轮 rework 理由均指向
recipient-owned `processor.py`；四轮还明确表示 producer 正确。问题是评价类别
混入自身集成计划，不能将其解释成 judge 把 producer 判错。下一卡应分别封存
producer-contract assessment 和 recipient integration plan，保留原始类别与实际路径，
用独立 Qp/未来结果检验它们的信息价值；这仍是卡片候选，历史标签与 ACTIVE 定义
没有因此被回写或私自改义。

主代理与 Codex `gpt-6-sol` 审查者逐条核对源码，没有以多数同意替代证明。

| 问题 | 审查结论与处理 |
|---|---|
| 正向事件支持 | 增加 Qp PASS 只补覆盖；J 仍恒定，不能单独解决问题 |
| 旧 delayed credit | 仅校验 lineage，不能证明 target J 是 producer reward；新合同显式拒绝该推断 |
| 固定 A 任意改变 J | native 强制 J–action 配对；改用合法配对及配对内路径变动，错误配对必须拒绝 |
| auxiliary observation ID | 不能冒用 native evidence ID；需实际注册回执与类型明确的桥 |
| 观察后再写归因回执 | native 每 J/A 只准一条 update；同一完成锚点支持分别验证的投影 |
| replay PASS | 只说明 native lineage 完整，不证明归因、标签有效或质量收益 |
| 只读支持文件被修改 | 早版 observation 只加 warning 不够；须 UNKNOWN，新版资格保留旧日志 |

## 用户确认与唯一生效版本

用户明确确认方案 B，已保存
[ADR0049](../../user/decisions/0049-separate-judgment-observation-from-credit.md)。
方法 v1.3、方法评价 v1.4 取代旧版；六类注册仍各只有一个 ACTIVE，旧定义保留。
真实交付评价可以是有噪声的观察，producer 归因与未来任务 reward 另验；源发布不更新，
接收方工作不变成产出方奖惩。没有修改或降低 Goal。

[推导与三个备选方向](../../research/candidates/judgment_observation_credit_split_v0.1_20261007.md)
保留数学实例和争议过程，不是另一份 ACTIVE 方法。正文同步由写作协作者负责；
版式验收与科学验收分开，不加入效果数字。

## 可复用实现

[ActorExperience](../../../scripts/peerrolebench_actor_experience.py)按 stream/arm/actor
隔离公开任务输入及自身输出，等同空初态、每 task 一次完整 episode、容量限制、
原子写入、重复幂等、决策快照恢复。[v2 四项离线检查](../../../experiments/logs/n03_actor_experience_qualification_20261007_v2/)
通过。字段检查不证明字符串内无秘密，调用方须先用公共 allowlist 投影。它是历史
容器，不是新训练算法，也尚未进入真实生成请求。

[NoisyJudgmentObservation](../../../scripts/peerrolebench_judgment_observation.py)复用
native replay、candidate registry、artifact hash，区分 producer 生成 diff 与 recipient
行动 diff。三种合法 J–action 配对均可保留；不提供 reward，source update 和 producer
credit 标志始终为 false。日志在 `experiments/logs/n03_judgment_observation_qualification_20261007_v*/`。
v1 缺外部 contract pin，v2 补 pin 但只读 support 越界处理仍不足；这些旧版测试通过
不能当成遗漏已安全，版本与失败边界保留，新资格单独记录。

[v3 最终资格](../../../experiments/logs/n03_judgment_observation_qualification_20261007_v3/)
新增只读 support 越界与 terminal 结果摘要缺失拒绝，22 项检查通过；真实调用仍为 0。
首次包装命令的 zsh 错误保留，随后 pytest 正确执行。v3 保存匹配源码快照。
actor-state v2 后补归档了 hash 匹配的源码；旧 observation v1/v2 只留 hash、日志，
当时未保存可恢复源码，这个复现缺口明确保留，不重建冒充原始版本。
observation 的排他 `read_cut=len(events)` 是本适配器约定，桥接时不能直接等同于
旧 offer 的 inclusive cut。终局来源仍需上游 operator 提供独立有效的测量。

独立终审又发现仅拒绝 target selection 仍不足：合法 ledger 可已有 assignment、尚无
selection。若此时发布观察，它不可能影响先前分派。
[v4 最终修正](../../../experiments/logs/n03_judgment_observation_qualification_20261007_v4/)
拒绝已有同一 target assignment/task start 的前缀；反例先证明原生 replay 合法，再
验证观察返回 UNKNOWN。聚焦套件 23 项通过，旧 v3 保留。该模块目前仅处理单源
prefix；连续多任务历史、native assignment 桥和合法 reward 仍需集成，不能称 live-ready。

Qp/Y 的真实测量仍由上游独立评分器负责。结果存在及摘要不等于覆盖或准确性。
本轮没有重复已有 matched terminal control，也没有重复 API 健康探测。

## 与 Goal 比较及下一单元

| Goal | 本轮推进 | 未完成 |
|---|---|---|
| ER-G1 评价→责任→效益 | 找到源评价退化原因，修正观测/归因关系 | 合法桥接、真实后续执行、未见任务质量与成本 |
| ER-G2 方法与实时训练 | 增加可复用观察与 actor state 模块 | reward 合同、最终表示/updater、时效性/稳定性实测 |
| ER-G3 benchmark/baseline | 增加 count-only/J-masked 辨识检查，保留合法 Qp/terminal/contextual 控制 | 两个合格结构 root、全基线 live parity、独立确认流 |
| ER-G4 真实证据 | 明确区分数学/协议资格与模型实验，保留配置与逐例日志 | 不能据此填实证收益表 |

下一小任务先完成任务区分度与判断对象的无新增调用检查，并完成 observation→assignment
的合法桥及 reward 合同：复用唯一原生完成锚点，
在旧 offer、最终 assignment、credit 消费边界检查类型、责任、subject/read cut/propensity。
通过零调用完整链后冻结 label/成本规则，再接真实 producer、actor state 与实际后续任务。
小卡先检查自然支持度和完整结果，不能反复改 seed/mapping、删失败来制造效果。
新 backbone/GPU 仍需真实瓶颈依据；三份科学审核和科学投稿 gate 均未通过。
