# 从接口诊断回到可检验的角色学习 — 2026-10-07

状态：`PARTIAL`；`goal_change_requested=false`。对应 ER-G1、ER-G2、ER-G3、ER-G4。

## 目的与本轮结果

本轮只检查已有证据和实现，决定下一笔实验成本应花在哪里；没有新增 API、GPU 或评分器执行。两位 Codex 协作者分别审查测量对照与状态流，主代理结合当前 Goal 和唯一生效规范复核。成功标准是删掉重复实验，并明确下一个能产生科学信息的执行单元。

现有 matched control 已经足够回答“局部合同合规是否等同于下游可用”。
[terminal v2 的控制汇总](../../../experiments/logs/n03_terminal_scorer_v2_20261007/summary.json)
中，`recipient_only_fixed` 和 `correct_both` 在两个同根 seed 均为 PASS；二者共用修正后的 processor，只改变 producer 时间戳序列化。seed-0 的 `recipient_only_fixed` 完整产物摘要，恰与本次真实 C1 产物的 `819118801d4ccfab2801b36032d4f0808bdf938eedf9ee532d8ea798fd7ffa29` 一致。
TeamBench 原生 generator 的 serialization test 明确检查 `T` 分隔，任务 spec 要求 `isoformat()`。
因此本轮**取消重复运行这个 matched pair 的建议**；沿用已有终端控制、实际 Qp 结果与源码推导。没有把未执行的原生测试写成已通过或已失败。

证据入口：[控制代码](../../../tests/test_peerrolebench_terminal_scorer_v2.py)、
[真实产物复核](20261007_independent_y_integration_audit_v2.md)、
[本地原生来源与固定版本](../../research/n01_teambench_qualification_20260926.md)。

## 当前真实流距离 Goal 的具体缺口

| 必需环节 | C1 实际行为 | 可以支持的结论 |
|---|---|---|
| producer 产生真实交付 | `_candidate_materials` 构造两份固定代码；registry 为 `fixture-model` | 交付物选择与协议诊断；不是 producer 能力进化 |
| recipient 实际判断与处理 | 真实 API，但 prompt 只含当前材料，没有该 peer 的私有历史 | 本轮判断/处理行为 |
| evidence 改变未来分派 | 具备公开证据输入、封存 assignment 和 policy update | 接口顺序可审计；这批 target 仍选同一 peer |
| 更新后分派真的执行 | 后续 selection 仅 `preview_only`，不在 native ledger | 不能报告该分派的未来质量或完整成本 |
| 跨任务、跨根结论 | 单 PIPE3 root，同一材料与固定候选 | 不支持跨 root 泛化或角色形成效益 |

实现证据为 [C1 runner](../../../scripts/peerrolebench_c1_pipe3_bounded_live.py)
中的 `_candidate_materials`、`_registry`、`_run_episode`、`_run_arm` 和 `_select_post_update`。
需要区分 selector 的持久状态与 producer/recipient 的私有执行经验：前者已存在，后者未在当前 C1 接通。把公开 role profile 或 `PeerHistoryV1` 改名为 actor memory 不能填补缺口。

## 已有真实 producer 接口与难度信号

不需要重新造 producer 调用器。[PIPE3 real-smoke](../../../scripts/peerrolebench_pipe3_real_smoke_v1.py)
已经使用 `build_materials(load_pipe3(seed))` 生成公共输入，真实调用 producer、judgment 和 consumer，并评分实际交付。现有 v2–v6 的五次 seed-0 producer check 均为 PASS；v2 的后续 scorer 不完整、v4/v5 的 consumer 响应错误仍保留 UNKNOWN。这只能提示这个单根修复任务可能过易，不能估计正式泛化准确率，也不能删掉执行失败。
[只读证据清点](../../../experiments/logs/n03_real_actor_evidence_census_20261007_v1/summary.json)保留全部五行及失败原因；[原始请求时间复核](../../../experiments/logs/n03_real_actor_evidence_census_20261007_v1/trace_check_result.json)确认各轮分别记录了真实 producer/judgment/consumer 请求，但五轮只有两份不同的 producer 产物，不能视作五种独立能力样本。

第二根的现有证据仍不足：DIST1 的两条早期真实链没有有效 producer objective，后续优先级审计发现真实缺陷；PIPE2 尚无真实 API，且部分 generator seed 产生无效 CSV。故下一步应复用实际 producer seam 和评分资产，而不是继续同 seed、同 prompt 的饱和 smoke。必须先在卡片中定义任务区分度和失败处理，不能把固定代码差异当成自然形成的能力差异。

## 下一执行单元：以真实后续执行替代预览

这是实现任务约束，不是新的 ACTIVE 方法，不预先锁定 backbone 或训练器：

1. 复用已有真实 producer 调用、source/action validator、评分器与成本账本；不再把两份人为设定优劣的代码当作完整智能体群体。先核查近期真实 producer 记录，避免重做已有接口。
2. 将执行前的 peer 状态读入真正的生成请求，并封存状态摘要和合法历史截止点；执行后仅写入该 peer 实际获得的经验。所有 peer 从相同初始状态与能力配置开始，按 arm/stream/peer 隔离。经验内容、容量和更新规则必须在卡片中固定；它们本身不被宣称为新算法。
3. 将现有 post-update preview 延伸为真的后续任务：先封存 assignment，再执行并测量 Qp、recipient 行为、独立终端结果及完整成本。产出方合同、终端效用与 assignment credit 分开记录；no-update 同样进入结果分母。
4. 无更新、原始验收、仅终局和同表示 contextual 控制使用同一初始机会与执行规则，随后各自积累独立经历。不能将 RARE 的已实现历史复制给 live baseline，也不能把当前仅三个可运行臂写成全部基线已冻结。
5. 第一张小卡仍只检查真实信息价值和闭环后果。没有自然区分度、未知责任、评分缺口或 label 通道不合法时停止并记录原因；不通过换分数或反复试 seed 制造收益。独立 root 和确认流仍是主结果前提。

验收量必须是：真实 producer/recipient 请求数；每次生成消费的 peer state/历史；实际完成的后续任务数；合法分派与结果绑定；逐臂质量及完整成本；UNKNOWN 和失败分母。工程测试条数不作为科学进度指标。

## 对 Goal 的回看

本轮消除了一个无效重复实验，并定位了“有更新调用，但没有更新后执行”的具体缺口。
没有完成 ER-G2 的新训练机制、实时性/遗忘比较，也没有完成 ER-G3 的两个合格 root、全基线独立流或 ER-G4 的效果证据。三份审核标准、Goal、主指标与创新主张均不降级；科学投稿 gate 继续关闭。
