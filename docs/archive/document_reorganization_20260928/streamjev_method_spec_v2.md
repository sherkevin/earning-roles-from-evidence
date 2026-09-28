# Stream-JEV v2：可上线的 selected-only 在线参数学习范式

**日期：** 2026-09-24  
**状态：** 当前工程 baseline 规范，不是已冻结的论文方法。Laya 仍是候选 encoder，
RLS 仍是强基线；创新边界见 [`streamjev_novelty_boundary_20260925.md`](streamjev_novelty_boundary_20260925.md)。
严格记号版问题定义见 [`streamjev_math_spec_v2_20260925.md`](streamjev_math_spec_v2_20260925.md)，
解释性问题定义见 [`streamjev_problem_formulation_20260925.md`](streamjev_problem_formulation_20260925.md)，
backbone 与更新方法的筛选规则见 [`backbone_method_math_selection_20260925.md`](backbone_method_math_selection_20260925.md)。

## 先给结论

我们的研究问题不是“把一个 JEV 模型接进 agent”，而是：在只观察被选候选结果、反馈有延迟且任务分布会变化的条件下，能否用极小的可训练参数头，在每条反馈到达后完成稳定、低延迟的在线更新，并且不破坏已有能力。

当前主线采用“冻结表示 + 在线 RLS 参数头 + 异步慢速巩固”的范式。RLS 不是最终创新本身，而是一个必须打赢的稳定主线和清晰的工程下界。门控循环快状态、短 unroll 元训练和 LoRA 慢更新都只能作为受控 challenger；如果它们在严格 selected-only、同等探索和相同预算下不能稳定超过 RLS，就删掉，不把复杂度写进论文。

## 为什么这一版比原方案干净

原来的“双快状态”容易把状态变化误称为模型训练，而且很容易在合成实验中使用未选候选真值。v2 把两件事分开：

1. **参数学习**：每条已到达反馈直接改变小型 `theta`，可检查 checkpoint 前后参数差异。当前参考实现使用稠密线性代数，评分和更新通常为 `O(d³)`；只有在实际维度和延迟预算要求时，才实现并验证递推分解后再声称 `O(d²)`；
2. **运行时记忆**：可选的 gated state 只作为 challenger，不承担“已经完成在线训练”的论断。

训练目标只使用已执行候选的标签和该次决策时记录的 propensity。未执行候选的结果、未来结果、全量真值和事后 oracle 排名一律不能进入 actor 或 learner 的输入。

## 模型边界

### 冻结表示和共享特征

第一版使用 Laya multilingual 约 322M 参数作为离线编码器，或者使用已经缓存的等价小模型表示。对任务上下文 `q`、候选 `c` 和 typed decision 计算固定维度特征：

```text
phi(q, c, type) = [q, c, q*c, type_embedding, bias]
```

候选由共享 scorer 逐个计算，菜单只通过 masked softmax 归一化。候选顺序置换不能改变任一候选的单项分数。缓存键必须包含 `task_id, candidate_id, candidate_version, encoder_version, feature_schema`；任一版本变化都不能复用旧特征。

### 在线参数头（主线）

每个 selector 维护一个低维 residual head：

```text
A_t = ridge I + lambda (A_{t-1} - ridge I) + w_t phi_t phi_t^T
b_t = ridge theta_0 + lambda (b_{t-1} - ridge theta_0) + w_t y_t phi_t
theta_t = solve(A_t, b_t)
```

其中 `w_t = min(w_max, 1 / propensity_t)`，`y_t` 是被选候选最终得到的二值或软标签。`theta_0` 是静态 head 的锚点。`theta` 设范数上限，`A` 采用对称化和必要的数值抖动；所有反馈由单一 learner 串行化或按 selector 分片串行化，避免并发写同一统计量。遗忘因子按 learner 接收的反馈序列定义；如果业务需要按真实时间遗忘，必须把事件时间纳入 decay，而不能把乱序到达时间默认为决策时间。

`base_i` 是和 `theta^T phi_i` 同尺度的质量 utility，不是未经校准的语言模型 logit。公式中的 `A^{-1}` 表示通过稳定线性求解得到的不确定度，不要求服务端显式存储逆矩阵。行为策略使用固定温度的 softmax：

```text
policy_i = softmax((base_i + alpha * theta^T phi_i
                    + beta * sqrt(phi_i^T A^{-1} phi_i)) / temperature)
```

不确定度项只负责受控探索。部署时必须记录实际采样概率，不能把 greedy 分数当作 propensity。特征必须包含显式 bias 或等价的全局校准维度，否则 head 只能修正方向性偏差。

### Challenger：门控快状态和慢更新

门控循环状态可以读取 `(phi, y, delay, propensity)` 并在反馈到达时更新，用来测试非线性 regime 适应；它不改变主线的 selected-only 合约。短 unroll 元训练只在离线 stream 上训练状态转移，不能宣称“逐条反向传播整个大模型”。

异步慢 learner 可以周期性更新静态 scorer 或小 adapter，但只能从“最近窗口 + reservoir”采样，并通过旧 regime holdout、校准和延迟门槛后原子发布。第一版不在线更新 Laya encoder，也不把 LoRA 放进关键路径。

## 统一事件和延迟反馈

peer 和 tool 两个项目共用 `DecisionEvent`：

- `decision_type`：`select`、`verify` 或 `final`；
- `candidates`：带版本的候选描述；
- `chosen_id`、实际 `propensity`、`state_version`；
- 当时可见的 context、候选特征快照或可重建的 feature key；
- 反馈只引用 `source_event_id`，并携带 `label`、到达时间、延迟和 `truth_status`。

反馈到达时必须使用决策时捕获的 `phi_t`、encoder/schema 版本和行为策略快照。禁止用反馈到达时重新编码的特征替代历史特征，否则版本漂移会被误认为在线适应。learner 需要用 `feedback_id` 做幂等去重；有限大小的本地去重窗口不能替代上游的 exactly-once 或可审计重放。

## 训练和上线流程

### Stage 0：静态基线

训练或加载静态 scorer，先只验证表示、菜单置换不变性和基础准确率。固定记录 checkpoint、特征 schema、模型版本和菜单构成。

### Stage 1：selected-only 小批量在线验证

按真实事件顺序回放，反馈按真实或随机化延迟到达。每次到达只更新选中候选的 head。对比 static、static+Beta、static+RLS、周期性 full-refit、label-shuffle 和 no-feedback 控制；所有方法共用相同候选、探索、延迟和随机种子。

### Stage 2：受控 challenger

只有当 RLS 在真实回放上稳定工作后，才加入 gated state 或短 unroll 元训练。每次只增加一个自由度，并保留 RLS 作为回退。每个 challenger 都要证明它带来更快的漂移恢复或更少的遗忘，而不是只提高训练集分数。

### Stage 3：异步巩固和服务

RLinf 只复用 Ray worker、Channel、replay 和 checkpoint 机制；第一版算法本体使用 PyTorch 小模块，避免把 RL 框架的 trajectory 假设强行套到 selector 事件上。ROLL 暂不作为依赖。服务拆成 Actor、FeedbackArbiter、Learner、SnapshotStore：Actor 只做缓存表示、打分和写事件；Arbiter 检查 selected-only、版本和延迟；Learner 更新参数并生成原子 snapshot；SnapshotStore 支持回滚。

## 必须报告的证据

每个实验都要保存配置、代码 commit、环境、每条 decision/feedback 原始记录、失败和聚合结果。至少报告：

- prequential regret、NLL、Brier、ECE 和选中正确率；
- 随机 regime switch 后的恢复步数；
- 旧 regime holdout 的遗忘量；
- 更新和决策的 p50/p95 延迟、内存、checkpoint lag；
- 多 seed 配对置信区间；
- 标签打乱、无反馈、静态和 Beta/RLS 基线。

合成实验必须随机化 regime、switch 时间、候选排列、反馈延迟和标签噪声；不得使用 `argmax(hidden_truth)` 作为训练目标。正式结论至少需要 10 个配对 seed，并在独立探索切片上复核 IPS/DR。

## 否决规则

出现以下任一情况，停止增加模型复杂度：

- 去除全量真值后，challenger 不超过 RLS 或优势不稳定；
- 提升只出现在固定 switch、固定候选顺序或可预测延迟；
- 旧 regime 明显退化且 reservoir/anchor 无法恢复；
- 更新 p95 超过决策间隔，或 checkpoint/version lag 使反馈无法对齐；
- peer 与 tool 无法共用同一事件和反馈合约；
- 真实回放只能提供事后全量 truth，无法形成 selected-only 训练证据。

若 RLS 已经是最优且 challenger 没有稳定增益，论文应收缩为可复现的实时在线选择工程，而不是继续堆叠“智能”模块。
