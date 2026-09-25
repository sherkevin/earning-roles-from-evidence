# earning-roles 的最终数学建模候选

日期：2026-09-25

## 结论

当前的 CDS-CB（受约束延迟选择性反馈上下文 bandit）是单步选择器的正确模型，
但不是 earning-roles 故事的完整模型。

原因是：选择某个 peer 会改变后续交付、信任、角色和工作流状态。若动作会改变
未来环境，纯 bandit 的假设就不成立。

对当前研究目标，最小而足够的模型是：

    带隐藏协作状态、动态候选集合、即时观测、延迟选择性反馈和在线学习状态的
    受约束控制过程

它比完整自由形式 POMDP 窄，因为我们只建模与 peer/tool 选择有关的状态；它比
contextual bandit 强，因为允许选择动作改变未来协作状态。

数学上这是一个隐藏状态控制过程；若需要严格求解，信念状态
`b_t = P(Z_t | F_t)` 是充分统计量。工程中的 `S_t` 是对这个信念和历史的有限
近似，不能把学习器状态直接等同于真实协作状态。

## 1. 变量

在决策时刻 t：

    Z_t       隐藏的真实协作状态
              例如 agent 能力、角色适配度、工作流阶段、信任和图结构

    X_t       从 Z_t 可见的任务上下文

    G_t       当前 peer 图
    C_t       当前可选候选集合，通常是 N_Gt(i_t)

    S_t       选择器自己的在线学习状态
              例如参数、后验、replay 统计量和版本

    b_t       对隐藏状态 Z_t 的信念或压缩表示

    A_t       实际选择的 peer/tool

    O_t       执行 A_t 后立即可见的原始输出或交付结果

    Y_t(C_t)  所有候选的联合潜在结果向量
    Y_t       对 A_t 的正确性/质量标签，可能延迟到达

    D_t       从决策到反馈可用的延迟
    τ_t=t+D_t

联合潜在结果应写成：

    Y_t(C_t) ~ P_Y(· | Z_t, C_t)
    Y_t = Y_t(A_t)

不能假设同一任务中不同候选的结果相互独立。动态 JEV 中多个 provider 共享同一
个实验真值，正是这种相关性的例子。

这里必须区分：

    O_t = 现在可以看到的执行输出
    Y_t = 以后才能看到的真实性能标签

没有看到 O_t 的任务可以把 O_t 设为空；有 O_t 的任务可以用它决定后续动作。

## 2. 一个决策如何产生

策略根据当前信念、学习状态和候选集合选择动作：

    A_t ~ π(· | b_t, S_t, X_t, C_t)

真实行为概率必须记录：

    p_t = π(A_t | b_t, S_t, X_t, C_t)

选中的候选产生即时输出：

    O_t ~ P_O(· | Z_t, A_t)

环境状态可能被这次协作改变：

    Z_(t+1) ~ P_Z(· | Z_t, A_t, O_t)

候选图、可用 peer 和候选版本也可能随状态变化：

    C_(t+1) ~ P_C(· | Z_t, A_t, O_t)

这一步是 earning-roles 与普通 contextual bandit 的根本区别。若在实际任务中
选择 peer 不会改变未来状态，则 P_Z 可以退化为与 A_t 无关的分布，模型自然退化
为 CDS-CB。

延迟反馈由潜在结果产生：

    Y_t ~ P_Y(· | Z_t, A_t, O_t)
    τ_t = t + D_t

在 τ_t 之前，更新器不能使用 Y_t。

严格的 Markov 增广状态还应包含待到达反馈队列 Q_t：

    Q_(t+1) = shift(Q_t) ∪ pending_event_t
    B_t = pop(Q_t, arrival_time = t)

这样乱序和延迟不是日志层面的附加字段，而是状态转移的一部分。

## 3. 观察历史和状态更新

即时输出进入当前任务的观察历史：

    H_(t+1) = T(H_t, A_t, O_t)

延迟标签到达时形成事件：

    e_t = (
      task/episode id,
      decision id,
      X_t, C_t, A_t, p_t,
      H_t 或 feature snapshot_t,
      O_t,
      candidate version,
      decision time t,
      arrival time τ_t,
      Y_t
    )

第 k 个 tick 到达的反馈集合：

    B_k = { e_t : τ_t = k }

在线学习状态的更新是：

    S_(k+1) = U_ψ(S_k, B_k)

U_ψ 只能使用已经到达的 B_k。它不能读取未来标签、未执行候选的结果或事后
oracle 排名。

如果事件乱序，U_ψ 必须满足以下之一：

    事件增量可交换、可结合，任何到达顺序得到同一 canonical state

或：

    保存事件并按 decision time 重放，checkpoint 记录 replay watermark

## 4. earning-roles 的目标

长期目标是未来协作效用，而不是当前标签拟合：

    J_T(π,U) =
      E [ (1/T) · ∑[t=1..T]
          utility(Z_t, A_t, O_t)
          − κ_call · call_cost_t
          − κ_explore · exploration_cost_t ]

utility 可以是：

    交付是否被接受
    后续是否被使用
    返工成本的反向分数
    最终任务质量
    对未来角色分配的贡献

离线若存在每个候选的完整结果，才计算动态 regret：

    Reg_T =
      E [ ∑[t=1..T]
          max[a∈C_t] utility(Z_t,a,O_t(a))
          − utility(Z_t,A_t,O_t) ]

完整结果只能用于评估，不能进入在线更新。

## 5. 稳定性、实时性和可识别性约束

旧任务集合 D_old 上的风险：

    L_old(S) =
      E[(X,C)∼D_old][ loss(π_S, X, C) ]

以发布前状态 S_ref 为参照：

    F_peak =
      max_t [ L_old(S_t) − L_old(S_ref) ]_+

要求：

    F_peak ≤ ε_old

实时约束：

    quantile_0.95(update latency) ≤ B_update
    quantile_0.95(decision latency) ≤ B_decision
    max_t memory(S_t) ≤ B_memory

selected-only 可识别性约束：

    记录真实 propensity p_t
    对需要比较的候选保证足够的累计曝光
    不使用未选候选的事后标签训练

## 6. 动态 JEV 是这个模型的另一个特例

动态 JEV 固定一个样本或 episode，内部步骤记为 j：

    状态 H_(e,j)
    动作 a_(e,j) ∈ provider set ∪ {STOP}
    即时输出 O_(e,j)
    历史 H_(e,j+1)=T(H_(e,j),a_(e,j),O_(e,j))
    最后作答或拒答
    真值标签延迟到达

它的 episode 损失是：

    L_episode =
      prediction_loss(final answer, truth)
      + λ_call · number of calls
      + λ_abort · abstain

因此动态 JEV 是：

    有限 episode horizon
    + call/STOP 动作
    + 即时信息获取
    + terminal answer/abstention
    + 延迟真值反馈

earning-roles 当前主问题是：

    长期 stream
    + 局部 peer/tool 候选
    + 一次选择一个候选
    + 选择可能改变未来协作状态
    + 长期效用、恢复和遗忘

二者可以由同一个上位控制过程描述，但不是同一个策略和损失。

## 7. 什么时候可以退化为 CDS-CB

如果满足以下条件：

    选择动作不改变未来 Z_t 的分布
    每个 tick 只选择一个候选
    没有题内多次调用
    没有 STOP/作答/拒答
    即时输出不影响下一动作

那么完整模型退化为：

    A_t ~ π_t(· | X_t,C_t,S_t)
    Y_t = selected-only delayed label
    S_(k+1)=U_ψ(S_k,B_k)

这就是当前的 CDS-CB。

因此 CDS-CB 应作为 earning-roles 的第一阶段可验证子问题，而不是最终故事
的完整数学定义。

## 8. 对 backbone 和训练方法的含义

backbone 负责表示：

    H_t(c) = E_φ(X_t, c, G_t, visible history)

它不能自动解决隐藏协作状态，也不应因为具有语言能力就被默认选中。

最终需要比较的是：

    policy π
    belief/state representation b_t
    event updater U_ψ
    slow consolidation mechanism

实时学习的创新必须落在 U_ψ 或 belief/state update 上：

    frozen semantic representation
    + small writable state
    + delayed-event update
    + old-task protection

RLS、online SGD、周期性 refit 是必须先打赢的基线，不是最终创新。

## 9. 为什么这是当前最小且足够的模型

如果用纯 contextual bandit：

    优点：简单、可估计、容易做小实验
    缺点：不能表达 peer 选择对未来协作状态的影响

如果用完全自由的 POMDP：

    优点：表达能力强
    缺点：状态不可观测、转移难以识别、实验成本过高，容易变成空泛定义

当前这个受限控制过程保留了真正需要的四件事：

    动作会改变未来
    反馈只对已执行动作可见
    标签可以延迟和乱序
    学习器必须实时且少遗忘

同时允许用 CDS-CB 做第一阶段实验，用动态 JEV 做另一个特例。

## 10. “最优”的判断标准

这里的最优不是公式越复杂越好，而是必须同时满足：

    1. 不遗漏 peer 选择对未来协作状态的因果影响；
    2. 不泄漏未执行候选或未来标签；
    3. 能容纳动态候选、版本和延迟；
    4. 能表达旧能力保持和实时资源约束；
    5. 能退化成可执行的 CDS-CB 小问题；
    6. 能覆盖另一个项目的 call/STOP/abstention episode；
    7. 允许共享 event/updater 代码，但不强迫共享错误的策略目标。

按这个标准，当前建议把它作为 earning-roles 的最终数学模型候选；CDS-CB 作为
第一阶段实验模型，动态 JEV 作为顺序信息获取特例。
