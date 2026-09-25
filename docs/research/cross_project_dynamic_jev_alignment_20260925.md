# earning-roles 与动态 JEV 项目的数学对齐

**日期：** 2026-09-25  
**状态：** 跨项目复用建议；不把两个科学问题强行合并。

对照的另一项目文档是：

    /Users/jingwu/work/benchmark/docs/候选方法_动态JEV数学抽象.md

## 结论

两个项目可以共享一层延迟选择性反馈的事件和更新基础设施，但不能直接共享
同一个核心优化问题、策略头和评价指标。

动态 JEV 是预算约束的顺序 provider acquisition：

    call(provider) -> 立即看到 provider output -> 继续 call 或 STOP
    -> 最后作答或拒答 -> 真值延迟到达

earning-roles 当前是每个决策 tick 的 peer/tool contextual selection：

    当前任务和候选集合 -> 选择一个候选 -> 反馈延迟到达 -> 更新状态

效果导向的复用边界是：

    共用事件、状态、延迟反馈、版本和更新基础设施；
    保留两个项目各自的策略、目标、标签语义和评估方法。

## 1. 可以统一的对象

候选都统一表示为：

    c = (candidate_id, candidate_version, metadata)

事件都应保存：

    episode_id
    decision_id
    selector_id
    context_snapshot
    candidate_set
    chosen_action
    action_propensity
    feature_snapshot
    candidate_version
    decision_time
    arrival_time
    feedback_group_id
    feedback_scope
    label

feedback_scope 必须区分：

    selected_only   一个被选候选得到反馈
    called_set      一个 episode 中所有已调用候选共同得到反馈
    terminal        只有最终作答或拒答得到反馈

两个项目可以共享同一个更新接口：

    B_k = { e : arrival_time(e) = k }
    S_(k+1) = U_psi(S_k, B_k)

更新器只能读取已经到达的事件，并必须使用事件中的决策时特征、propensity
和候选版本。

可共用的工程模块包括：

    event schema
    delayed queue
    exactly-once / 去重
    乱序重放
    feature cache
    state store
    checkpoint / rollback
    updater API
    latency 和证据日志

## 2. 不能直接统一的对象

### 2.1 动作流不同

动态 JEV 的动作空间是：

    call(p) 或 STOP

它有 episode budget、终端作答和拒答。

earning-roles 当前动作是：

    A_t ∈ C_t

它默认每个 tick 选择一次，没有 episode 内 STOP 或拒答头。

把 peer/tool 强行改成动态 JEV 的 call/STOP 语义，会改变任务，不是简单复用。

### 2.2 反馈的信息量不同

动态 JEV 中，一个真实值 y_i 可能同时给多个已调用 provider 产生标签：

    { c_(i,p) : p ∈ called_set_i }

这些标签共享同一个 shared_truth_id，彼此相关，不能摊平为独立样本。

earning-roles 当前一次选择通常只有一个 selected candidate 的结果：

    Y_t = Y_t(A_t)

所以统一事件时必须保留：

    episode_id
    feedback_group_id
    called_order
    terminal_action

否则会高估有效样本量和更新速度。

### 2.3 目标不同

动态 JEV 的 episode 目标是：

    L_episode =
      prediction_loss(final_answer, truth)
      + lambda_abort * abstain
      + lambda_call * number_of_calls

earning-roles 的 stream 目标是：

    J_stream =
      average future utility of selected peers/tools

同时约束：

    old-task forgetting
    update p95
    decision p95
    state memory
    drift recovery

可以共享 U_psi，但不能把 terminal loss 和长期 stream utility 合成一个没有
任务语义的总分。

### 2.4 预测对象不同

动态 JEV 估计：

    q(p | current_sample, called_history)
      = provider p 正确的概率

然后用 VOI 决定是否继续调用。

earning-roles 直接优化：

    pi_t(c | task_context, candidate_set, online_state)

动态 JEV 需要：

    provider correctness scorer -> VOI / STOP / abstention policy

earning-roles 需要：

    candidate utility scorer -> contextual selection policy

不能把 JEV 的 choice distribution 直接当成 provider correctness，也不能让
peer/tool 选择器默认承担 VOI 和拒答。

### 2.5 立即输出和延迟标签不同

动态 JEV 调用 provider 后立即看到原始返回：

    O_(i,j) = provider output
    H_(i,j+1) = T(H_(i,j), action, O_(i,j))

它用 O 继续决定下一次 call 或 STOP。

延迟到达的真值标签是另一条信息：

    Y_(i,j) arrives at tau_(i,j)

earning-roles 当前数学定义主要写了延迟结果，未把 episode 内立即输出作为
下一动作观测。两边可以共用上位事件接口，但不能把 O 和 Y 混成一个字段。

## 3. 共同的上位形式

两边都可以看成：

    hidden/task state
      -> choose action
      -> observe selected action output
      -> delayed correctness/quality feedback
      -> update online state

动态 JEV 是：

    horizon <= B_i
    action = call(provider) or STOP
    terminal output = answer or abstain

earning-roles 是：

    horizon = 1 per decision tick
    action = choose one local candidate
    no default STOP/abstention head
    objective = long-run stream utility

这适合作为代码层共享抽象，不建议在论文中再引入第三个新问题缩写。

## 4. Backbone 能不能共用

可以共用 encoder contract 和资格测试，但不能现在直接共用同一个 backbone。

共同资格门：

    frozen static probe
    task x candidate interaction
    candidate permutation
    variable-size candidate set
    version-aware cache
    calibration
    decision p95 latency

动态 JEV 的输入是分子/性质、provider output 和结构化数值；earning-roles 的
输入通常是任务文本、agent role、局部图和交付结果。它们可能需要：

    modality-specific E_phi^JEV
    modality-specific E_phi^peer
    shared low-dimensional updater API

只有跨模态表示和校准测试都通过，才考虑共享 backbone；否则共享 updater 和
缓存基础设施更稳妥。

## 5. 另一项目候选稿中需要保留的边界

这份候选稿是最小问题，不是最终 benchmark 的全部数学对象。后续若纳入 typed
decisions、复核、工具选择、作答和拒答，必须保留 episode wrapper。

还需要补齐四点：

1. 连续值任务不能同时使用 exact equality 和容差判定，应统一为显式 prediction
   loss；
2. 独立 Bernoulli 的 q(p) 不足以计算 VOI，VOI 还需要 provider output 分布及
   观察后的联合影响；
3. 在线更新事件必须包含 history/feature snapshot、propensity、version 和
   decision/arrival time；
4. 安全约束不能只用 wrong-and-answer 概率，否则全拒答会平凡满足；必须同时
   报告 coverage 和 conditional selective risk。

这些是另一项目的标签、策略和评估修正，不需要改写成 earning-roles 的 bandit
目标。

## 6. 效果导向的实现顺序

第一阶段只共享底层：

    两边各自产生原始 event log
    -> 共用 delayed queue / snapshot / replay / updater harness
    -> 各自运行自己的 policy 和 evaluator

动态 JEV 单独测：

    terminal loss、call cost、coverage、selective risk、abstention safety

earning-roles 单独测：

    prequential utility、dynamic regret、drift recovery、old-task forgetting

只有当同一个 U_psi 在两边同时通过下列条件，才共享训练方法：

    动态 JEV：terminal loss 下降、call cost 不恶化、abstention safety 通过
    earning-roles：future utility 提升、恢复更快、旧任务退化受控
    共同：update p95 通过、乱序重放一致、版本错配率为零

若只能改善其中一个项目，就保留共同工程接口，分别设计训练方法。为了节省
代码而强行共享算法，不符合效果优先原则。

## 最终建议

当前最合理的共享范围：

    共享：
      event schema、feedback group、feature cache、delayed queue、
      replay/order handling、state store、checkpoint、updater API、
      latency/evidence harness

    分开：
      VOI、STOP、abstention、contextual peer/tool policy、
      terminal episode loss、stream regret/forgetting、
      task-specific label calibration

这可以显著节省开发时间，同时不改变两个项目各自的科学问题。
