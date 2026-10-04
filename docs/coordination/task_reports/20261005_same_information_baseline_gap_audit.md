# N03-next-r5.66：same-information baseline gap audit

日期：2026-10-05  
状态：`BLOCKED_BY_EVIDENCE`（代码审计完成；live parity 不放行）  
`goal_change_requested=false`

## 目的

在 r5.65 的 runtime stream builder 通过后，重新检查真正进入 live comparison 的
strongest same-information baseline。目标不是再增加一个协议字段，而是确认 RARE 与
contextual/pooled control 的差异是否只来自预注册的更新规则，而没有混入表示或输入
差异。

## 可核对事实

当前 runner 在 `PolicyMatrixRunner.run()` 中把 `captured_features`、`base_scores`、
candidate menu、arrival 和 public feedback 传给所有 policy，但实际消费不同：

1. `RarePolicy._scores()` 明确丢弃 `base_scores`，并用每个候选的 64 维
   `captured_features` 计算线性 sigmoid 分数；RARE 还验证 `hash64-v1`、维度和范数。
2. `ContextualTrustPolicy._scores()` 只按
   `context_key × candidate_key` 的 Beta posterior 计算分数；它保存了
   `captured_features`，但不读取它。
3. `PooledControllerPolicy._scores()` 只按 candidate key 聚合 Beta posterior，也不读取
   `captured_features`。
4. `contextual_trust` 与 RARE 的反馈 source 都是 `recipient_judgment`，但 contextual
   将 correction 作为不可用事件，RARE 支持 event-time correction。这一差异可以是预注册
   updater 对照，但当前 feature 输入差异不能被同样解释。

对应代码为 `scripts/peerrolebench_baseline_policies.py` 的
`ContextualTrustPolicy`、`PooledControllerPolicy` 和 `RarePolicy`；共同输入路径在
`scripts/peerrolebench_policy_matrix_runner_v1.py`。这不是基于结果的推断，而是静态实现
事实，未调用 API/GPU。

## 与生效标准的冲突

`method_v1.1` 第 6 节要求同一 `φ`、信息、propensity、预算和历史可见性下比较；
`benchmark_baseline_v1.1` B2 要求逐项信息 parity；评价标准 B1 将 strongest
same-information contextual trust 作为排除替代解释的必要 arm。当前代码不能满足这一
要求，因此七臂离线 matrix 只能叫 engineering matrix，不能叫 scientific baseline parity。

这也解释了为什么不能马上开 PIPE3 live parity：如果 RARE 改善，无法判断改善来自
responsibility-aware/delayed bounded update，还是仅来自 64 维特征表示；如果没有改善，
也无法判断 Beta comparator 的表示劣势是否掩盖了方法差异。

## 推荐的修复方案（尚未写入 active method）

建议将 strongest control 定义为一个版本化的
`contextual_trust_linear_v1`：

- 使用同一 `hash64-v1`、同一 64 维 `φ`、同一 candidate menu、read cut、arrival、
  selected-only recipient judgment、propensity、exploration、state cap 和成本口径；
- 采用普通 feature-aware diagonal RLS/线性 contextual updater，不使用 RARE 的 protected
  anchor、bounded fast window、correction queue 或责任专用逻辑；
- 与 RARE 接收同一 public/UNKNOWN projection，UNKNOWN 不更新；correction 行为作为
  独立预注册 ablation，不混入表示差异；
- 当前 Beta `contextual_trust` 保留为较弱的 context-only diagnostic，不能继续充当唯一
  strongest control；`pooled_controller` 仍作为共享历史上界。

在真实 runner 之前必须完成 zero-call parity qualification：feature mutation、menu
permutation、base-score policy、late/correction、snapshot/restore、same feedback
sequence 和 policy namespace；随后才重新生成 canonical manifest 与 matched live card。
现有 `base_scores` 在 fixture 中为零，但 live 合同必须明确“固定为全零”或让 RARE 与
新 control 使用同一 base-score 项，不能默认为隐含常数。

## 当前决定与下一步

本报告只记录冲突和候选修复，没有擅自修改 active method、baseline arm 名单或 Goal，也
没有启动 API/A800。需要确认的唯一方法选择是：是否把
`contextual_trust_linear_v1` 作为 strongest same-information control，并保留现有 Beta
版本为辅助诊断。得到确认后，下一小任务是实现该 comparator 和零调用资格矩阵；在此之前
不运行任何 live efficacy episode。
