# Stream-JEV：从第一性原理抽象问题

**日期：** 2026-09-25  
**状态：** 数学问题定义与设计边界；不锁定 backbone，也不锁定最终训练算法。

为便于后续检索和对比，暂将问题称为 **Constrained Delayed Selective-Feedback
Contextual Bandit（CDS-CB，受约束延迟选择性反馈上下文 bandit）**。这个名字是
问题类别，不是论文方法名。

## 1. 研究目标不是“把候选打分”

系统在每个决策时刻只能从当前可见的一组 peer/tool 中选一个。被选对象执行
后才会产生结果，且结果可能延迟到达；未被选对象没有标签。候选对象会加入、
删除、替换版本，任务分布也会变化。我们要学习的是一个能够在这种信息约束下
持续更新的小型决策状态，使未来选择质量提高，同时满足实时延迟和旧能力保留
约束。

因此最小目标是一个**受约束的部分反馈在线控制问题**：

> 在只使用截至当前已经到达的反馈的前提下，最大化长期 prequential utility，
> 同时把更新延迟、状态大小和旧分布性能退化控制在预算内。

这一定义同时覆盖 peer selection 和 tool selection。peer 图只影响当前候选集合
的生成方式；tool 选择可以看成没有显式图的候选池。

## 2. 过程定义

### 2.1 决策、候选和潜在结果

设 `i` 是发起选择的 agent（tool 项目可把 `i` 固定为一个 selector）。在决策步 `t`：

- `x_t`：任务上下文（问题、工作流状态、调用约束等）；
- `G_t=(V_t,E_t)`：当任务是 peer selection 时的局部 agent 图；发起者 `i` 的
  候选集合通常是 `C_{i,t}=N_{G_t}(i)`，tool selection 则是普通候选池；
- `C_{i,t}=C_{i,t}(v_t)`：当前允许选择的候选集合。每个候选写成
  `c=(id, version, metadata)`，因此同一个 `id` 的换版是不同对象；
- `u_{i,t}(c)∈[0,1]`：候选在该任务上的潜在 utility，例如交付正确性、返工成本
  的反向分数或验证后的质量；它只在候选被执行后才可能被测量；
- `y_t`：被选择候选的观测标签。二值正确性是 `y_t∈{0,1}` 的特例，软标签
  和多值质量分数也可以使用。

选择策略从 `C_t` 中采样：

```text
a_t ~ π_{i,t}(· | x_t, C_{i,t}, S_{i,t}),
       p_t = π_{i,t}(a_t | x_t, C_{i,t}, S_{i,t}).
```

`p_t` 是真实行为 propensity，必须随事件记录。若只用 greedy 选择而从不探索，
未选候选的质量在统计上不可识别。

### 2.2 在线状态和信息边界

共享的离线参数可以跨 agent/任务共享，但每个发起 agent 保留自己的在线状态：

```text
S_{i,t} = (θ_{i,t}, m_{i,t}, R_{i,t}, v^model_t, v^schema_t),
```

其中：

- `θ_t`：相对慢的 scorer 或可写参数；
- `m_t`：每条反馈可更新的 fast state；
- `R_t`：有限 replay/reservoir 或可合并的统计量；
- `v^model_t`、`v^schema_t`：模型和特征协议版本。

决策时可见的信息是过滤：

```text
F^dec_{i,t} = σ(x_≤t, C_{i,≤t}, a_<t,
                 {e_s : selector(s)=i, τ_s < t}),
```

其中 `e_s` 只包含已经到达的反馈事件。策略必须对 `F^dec_t` 可测，不能读取
未来标签、未执行候选的事后真值或 oracle 排名。

候选打分可抽象成：

```text
φ_{i,t}(c) = φ(x_t, i, c, C_{i,t}, G_t; v^model_t, v^schema_t)
s_{i,t}(c) = f_{θ_{i,t},m_{i,t}}(φ_{i,t}(c), C_{i,t}),
π_{i,t}(c) = masked_policy(s_{i,t}(·), C_{i,t}).
```

这里的 `φ` 不预设为 Laya hidden state。它只需要产生可缓存、带版本、对候选
菜单变长可用的表示；是否需要 set/graph encoder 是后续模型选择问题。

### 2.3 延迟反馈事件

选中候选的结果在决策步之后 `D_t≥0` 到达，
`τ_t=t+D_t`。到达的事件保存决策时快照，而不是重新用新模型编码：

```text
e_t = (event_id, x_t, C_t, a_t, p_t,
       φ_t(a_t), y_t, t, τ_t,
       candidate_version, model_version, schema_version).
```

在墙钟时刻 `h` 到达的事件集合是
`A_h={t:τ_t=h}`。更新算子只接收已经到达的事件：

```text
S_{h+} = U_ψ(S_{h-}, A_h).
```

若事件乱序，`U_ψ` 必须明确采用以下两种语义之一：

1. **可合并语义**：事件映射到可交换/可结合的 sufficient statistics，任何合法
   到达顺序得到同一个 canonical state；或
2. **事件溯源语义**：保存事件并按决策时间重放受影响窗口，发布版本携带重放
   水位线。

只在队列中顺序更新、却没有定义乱序语义，不能声称解决 delayed feedback。

候选版本发生变化时，旧事件仍绑定旧的 `(id, version, φ)`。不能把旧版本的
标签直接写到新版本的参数上。

## 3. 纯数学优化目标

### 3.1 主目标：未来 prequential utility

给定算法 `A=(φ,f,U,π)`，在真实流上定义：

```text
J_pre(A) = liminf_{T→∞} (1/T) E[ Σ_{t=1}^T
              ( u_t(a_t) - λ_c cost_t(a_t) ) ].
```

有限窗口中报告 prequential regret：

```text
Reg_T = Σ_{t=1}^T [ max_{c∈C_t} u_t(c) - u_t(a_t) ].
```

如果真实 oracle utility 只能在评测集获得，训练过程仍只能看到 selected-only
事件；oracle 只用于离线评估。

### 3.2 适应和遗忘必须同时定义

设 `D_old` 是锁定的旧任务/旧 regime 分布，`J_old(S)` 是用当前策略状态在
`D_old` 上的 utility。定义遗忘量：

```text
F_T = max_{0≤h≤T} [ J_old(S_0) - J_old(S_h) ]_+.
```

新 regime 的适应增益可定义为漂移后窗口的相对提升：

```text
A_{[t0,t1]} = J_{[t0,t1]}(A) - J_{[t0,t1]}(A_no_update).
```

论文不能只报 `A` 或训练流准确率；核心是 `A` 与 `F` 的 Pareto 曲线，以及更新
延迟是否仍在服务预算内。

### 3.3 受约束问题

最终要解决的问题可写成：

```text
maximize_A       J_pre(A)
subject to       F_T ≤ ε_old,
                 L_update^p95 ≤ B_update,
                 L_decision^p95 ≤ B_decision,
                 memory(S_h) ≤ M,
                 compute_update(e_t) ≤ C,
                 p_t ≥ p_min for every eligible candidate,
                 causal(selected-only, delayed feedback).
```

工程上可以使用带乘子的训练目标：

```text
L(ψ, θ_0) = E_stream[
      Σ_t -u_t(a_t)
    + λ_f F_T
    + λ_u latency_update_t
    + λ_m memory_t
    + λ_s ||ΔS_t||²
].
```

这只是目标函数形式，不预设如何求解。`ψ` 可以表示离线学习到的更新规则，
`θ_0` 表示静态初始化；线上只允许使用到达事件更新 `S`。

### 3.4 选中反馈下的可识别性

对离线训练或评估，selected-only 数据只能通过 propensity 加权或 doubly robust
估计构造候选级风险。例如候选损失可写为：

```text
L_IPW = (1/T) Σ_t 1[a_t=c_t] · ℓ(c_t,y_t) / max(p_t,p_min).
```

`p_min` 既是探索约束，也是方差控制。若某候选永远不被选择，则任何算法都无法
从数据中辨认它的真实 utility；这不是模型容量问题。

## 4. 从数学形式得到的优化方向

### 4.1 把“实时训练”化为低维状态转移

全量 encoder 每条反馈反向传播的更新成本至少随参数量线性增长，并且会破坏
延迟预算。应将关键路径写成：

```text
ΔS_t = U_ψ(e_t, S_t),       dim(S_fast) = k ≪ dim(encoder).
```

可优化的是 `k`、更新算子结构和统计量存储方式，而不是先假定某个 backbone。
低秩/对角/块对角 sufficient statistics 可以把每条事件的更新从稠密求解降到
与 `k` 或秩 `r` 线性、平方相关的成本；任何复杂度声明必须用实际 A800 服务测量
的 p50/p95 支持。

### 4.2 延迟与版本校正

事件中保存 `φ_t(a_t)`、`p_t` 和版本，使更新使用决策时信息。若目标是乱序不变，
需要设计可交换的事件增量；若做不到，就采用可审计重放而不是静默覆盖。这个
约束直接决定能否将反馈延迟误差与模型适应区分开。

### 4.3 稳定性与可塑性的显式约束

一次更新的可写方向 `ΔS` 可以被限制在旧任务允许的信赖域内：

```text
ΔS_t ∈ {δ : D_old(S_t+δ, S_t) ≤ ε_step},
```

其中 `D_old` 可以由旧样本的 KL、校准误差或 utility 下降近似。该形式允许比较
RLS、replay/EWC、低秩 adapter 和学习型 update operator，而不把某一种实现提前
写成答案。

### 4.4 探索和冷启动

`π_t` 需要在 exploitation 与 exploration 之间折中。新候选没有历史标签时，
只能由共享表示、候选元数据和先验产生初始分数；若它完全没有可迁移信息，则
不存在对其质量的即时保证。探索率、propensity 和新候选比例必须作为实验变量，
不能藏在实现细节里。

## 5. 最小假设与不可避免的边界

要得到可解释的适应/遗忘结论，至少需要：

1. `u_t(c)` 有界，标签噪声的条件均值与目标 utility 有固定关系；
2. 每个可评估候选有 `p_t≥p_min>0` 的机会被选中；
3. 延迟有限或至少有有限均值，并能审计 `t` 与 `τ_t`；
4. 候选 ID/version、特征 schema 和事件 ID 可追踪；
5. 旧分布有锁定的 replay/holdout，用于估计 `F_T`；
6. 环境漂移在评测窗口内受限（例如分段平稳或总变差有界）。

没有这些假设时，存在三个不可消除的 no-free-lunch：

- 无探索时，未选候选不可识别；
- 任意漂移和无界延迟下，不能同时保证快速适应和旧能力不变；
- 新候选完全没有可迁移特征时，冷启动性能没有统计保证。

因此论文应声称“在给定反馈、漂移、延迟和预算假设下的受约束适应”，而不是
“普遍实时学习”。

## 6. 由数学问题反推 backbone 和训练方法

### Backbone 必须回答的不是参数量，而是可行性条件

候选 backbone 至少要满足：

- 输出固定维度且数值稳定的 `φ(x,c)`；
- 支持变长候选菜单、mask，并在候选置换下保持语义不变；
- 支持候选 ID/version 和新候选 metadata 的增量编码；
- 表示可在决策时缓存，不能要求每条反馈重新运行全模型；
- 与 peer/tool 共用事件 schema；
- 允许把实时更新限制在小状态，而不必逐条更新语义基座。

Laya、其他小型 encoder 或 set/graph encoder 都必须按这些条件和真实数据验证，
不能因为参数量小就直接定为 backbone。

### 训练方法必须回答的是更新算子

训练流程应明确分成四层：

1. **静态初始化**：从历史任务学习 `φ` 和 `θ_0`；
2. **stream/meta training**：离线在带延迟、候选 churn、selected-only mask 的
   流上学习 `U_ψ` 或其参数；
3. **online fast update**：线上只接收真实到达事件，更新 `S_fast`；
4. **slow consolidation**：异步使用 replay/holdout 更新慢参数，验证通过后发布
   新 snapshot。

真正的算法贡献必须落在第 2/3 层的更新机制，并在同样的 `φ`、参数预算、探索率、
   延迟和反馈下超过 RLS、online SGD、周期性 refit 与 replay/EWC 等基线。仅仅把
   这些模块拼起来不构成新训练方法。

## 7. 进入模型选择前的最小判别实验

在锁定 backbone 之前，只做一个资格验证：

1. 选一批标签来源、候选版本、延迟记录都明确的真实 peer/tool replay；
2. 用两个候选 encoder 生成决策时缓存特征，检查菜单置换、版本切换和缓存重建；
3. 在同一特征上比较 no-update、RLS、online SGD 和一个候选学习型更新器；
4. 只看 post-update prequential utility、漂移恢复、旧任务遗忘、更新 p95、状态
   大小和乱序重放一致性；
5. 若没有稳定的适应–遗忘 Pareto 改善，就不扩大模型或训练搜索。

这个实验的作用是判断“数学问题是否存在可赢的算法空间”，而不是提前替某个
backbone 背书。
