# 从纯数学问题反推 backbone 与训练方法

**日期：** 2026-09-25  
**状态：** 选择框架和小实验规范；不表示已经锁定 Laya 或最终算法。

这份文档先把 peer/tool 选择写成同一个在线决策问题，再用约束筛选模型。模型名放在最后，不能反过来决定问题。

## 1. 任务的最小数学形式

在决策时刻 `t`，有任务上下文 `c_t` 和局部候选集合 `C_t`。`C_t` 可以是无向图中当前节点的邻居，也可以是工具集合。候选集合会增删，候选还可能有版本号 `v_{t,i}`。

对每个候选生成表示

```text
h_{t,i} = E_phi(c_t, x_{t,i}, v_{t,i})
```

其中 `x_{t,i}` 是候选描述、历史执行摘要和可见状态。`E_phi` 不应该看未来结果。选择器维护一个很小的动态状态 `s_t` 和参数 `theta_t`，给候选打分：

```text
q_{t,i} = f_theta_t(h_{t,i}, C_t, s_t)
pi_t(i | C_t) = softmax((q_{t,i} + exploration_{t,i}) / T)
a_t ~ pi_t
```

只执行 `a_t`，因此只得到一个标签或软奖励 `y_t`。反馈在 `tau_t = t + d_t` 到达，`d_t` 可以变化，反馈可能乱序。决策时必须保存 `h_{t,a_t}`、实际 propensity `p_t = pi_t(a_t|C_t)`、候选版本和快照版本；到达时不能用新版本特征替换历史特征。

环境可以非平稳地写成

```text
z_{t+1} ~ P(z_{t+1} | z_t),  y_t ~ P_z(. | c_t, a_t)
```

其中 `z_t` 是未观测的任务/agent regime。我们要学的不是“把当前标签拟合得更好”，而是在这条有延迟、部分反馈和 regime 漂移的流上长期选对候选。

selected-only 还要求探索有可识别性：对仍在候选集合中的候选，行为策略不能给出零概率，否则它的期望结果永远无法从日志中估计。最小约束是 `p_t(i) >= p_min`（或预先声明只估计被探索覆盖的子集）。IPS 更新可以写成

```text
ell_t(theta) = 1{a_t=i} / p_t(a_t) * loss(f_theta(h_{t,a_t}), y_t)
```

`p_min` 越小，估计方差越大；因此探索强度也是速度、效果和标签效率之间的约束，而不是一个可以事后调到最优的自由变量。

## 2. 三个必须同时满足的目标

### 2.1 决策效用

主目标是 prequential 选择效用（或 regret）：

```text
J_reward = liminf_T 1/T E[ sum_{t=1}^T y_t ]
```

如果不同任务的奖励尺度不同，先在任务内归一化，再报告任务宏平均。未执行候选的事后真值不能进入 actor 或 learner；它们最多用于独立评估。

### 2.2 实时更新

把反馈更新记为

```text
s_{tau_t+1}, theta_{tau_t+1} = U_psi(s_{tau_t}, theta_{tau_t}, e_t, y_t)
```

其中 `e_t` 是决策时冻结的事件。要求的是每条反馈到达后的端到端更新延迟，而不是离线 batch 的平均训练时间：

```text
P95(update_latency) <= B_update
memory(state) <= B_memory
```

`B_update` 应由真实服务的决策间隔确定；先测量，不能先写成某个漂亮的毫秒数。

### 2.3 旧能力保留

定义一份锁定的 old-regime holdout `D_old`。相对于发布前快照，遗忘量为

```text
F_t = Risk_D_old(theta_t) - Risk_D_old(theta_release)
```

要求平均和最坏遗忘都受控：

```text
E[F_t] <= epsilon_avg,   quantile_95(F_t) <= epsilon_peak
```

`D_old` 不参与当前事件标签的生成，只用于周期性评估和受限的保护更新。没有 old holdout，就无法声称“少遗忘”。

因此完整选择问题是一个约束优化，而不是单一准确率最大化：

```text
maximize       J_reward
subject to     P95(update_latency) <= B_update
               memory <= B_memory
               forgetting <= epsilon
               selected_only / version / propensity contract is valid
```

训练时可以使用对应的拉格朗日目标

```text
J = J_reward - lambda_F * F - lambda_L * latency - lambda_M * memory
```

但论文主结果必须报告原始约束指标，不能只报告一个调过权重的总分。

## 3. 选模型前需要分清三层

### 3.1 语义 backbone `E_phi`

它负责把任务和候选变成稳定的表示，不应承担实时更新。候选有序列表会导致伪信号，所以集合级交互必须满足置换等变性；最小形式是

```text
g_t = rho(sum_j psi(h_{t,j}))
q_{t,i} = f([h_{t,i}, g_t])
```

如果确实需要图结构，才换成局部 GNN；不能因为有“graph”叙事就默认使用 GNN。

可选 backbone 类别：

| 类型 | 适用条件 | 优点 | 主要风险 |
|---|---|---|---|
| 冻结小型双向文本 encoder | 输入主要是任务、候选描述和执行摘要 | 语义强；可缓存；线上不反向传播 | 维度和编码延迟；本身不是在线学习 |
| 蒸馏/量化 encoder | 需要更低 p95 或更高并发 | 成本最低；可压到较小维度 | 语义损失，需用静态 probe 验证 |
| 手工/结构化特征 | 候选输出已有可靠 schema | 更新最简单；可解释 | 跨任务泛化差，无法处理自由文本 |
| 可训练 cross-encoder/set encoder | 候选之间的相对关系决定结果 | 能建模 task×candidate×menu 交互 | 每次重算更贵；在线更新风险大 |

Laya、ModernBERT、MiniLM、E5 等只能作为这些类别的实例。此处没有默认 Laya；应先通过同一 frozen-probe 资格测试再决定。

### 3.2 选择器/score model `f_theta`

候选选择器只需要可靠的相对排序和可校准概率，未必需要大语言模型。按在线更新复杂度可分为：

| scorer | 每条事件更新 | 适合作为 |
|---|---:|---|
| 线性/低秩线性头 | `O(d^2)`（递推 RLS）或 `O(rd)` | 稳定下界、速度基线 |
| 小型 MLP/双线性头 | `O(r d)` 到 `O(h^2)` | 建模非线性 challenger |
| set/graph scorer | 依菜单规模增加 | 仅在 pairwise/menu 交互确实必要时使用 |
| 全 encoder 微调 | 与 backbone 参数量相关 | 不进入实时关键路径，只能离线巩固 |

当前实现的稠密 `solve(A,b)` 通常是 `O(d^3)`；只有实际采用 Sherman–Morrison/Woodbury 等稳定递推并测过，才能宣称 RLS 的 `O(d^2)`。

### 3.3 更新算子 `U_psi`

这是实时训练的核心。候选包括：

1. **递推 RLS/online logistic**：用选中事件和 propensity 做 rank-one 更新。它是必须打赢的强基线，不是创新本身。
2. **低秩受保护写入**：冻结语义基座，只更新 `r << d` 的可写子空间；写入前用 old holdout 的 KL/ECE 或 trust-region 投影，超限就拒绝。
3. **元学习事件更新器**：离线用多条 selected-only stream 学习 `U_psi`，线上只执行一次前向和低秩写入，不对大 encoder 反向传播。元目标应包含未来窗口 reward 和 old-regime retention，而不是当前标签 loss。
4. **事件溯源更新器**：记录决策时的特征、版本、propensity 和 snapshot；延迟/乱序反馈先生成独立增量，再合并 sufficient statistics。必须证明不同到达顺序得到同一 canonical state，只有消息队列不算算法创新。

线上实时性来自“小状态更新”，而不是把大模型每条反馈重新训练一次。慢速巩固可以异步进行：只从最近窗口与 reservoir 采样，经过 locked holdout 和版本检查后原子发布。

## 4. 从数学约束得到的筛选规则

### Backbone 资格门

候选 backbone 只有同时满足以下条件，才进入在线方法比较：

1. frozen static probe 在真实任务上明显优于随机/手工特征，且校准不会完全失效；
2. 候选顺序随机置换后，单候选分数和选择结果保持等变；
3. 表示可缓存，特征维度 `d` 和推理 p95 能放入实际预算；
4. 候选版本或 encoder 版本改变时缓存不会静默复用；
5. 许可证、权重、tokenizer 和运行环境可复现；
6. 不依赖在线反向传播才能工作。

静态资格测试还必须覆盖候选数量和菜单长度。Laya 上游报告本身显示，高基数选项
和 score 任务可能出现明显性能下降或位置偏差；因此“参数量小、推理快”不能替代
我们在真实 peer/tool 菜单上的 task×candidate 交互、候选置换和校准测试。

只有在上述指标接近时，才用语义分数、吞吐和大小做次级排序。一个 4B backbone 即使静态准确率高，也可能因更新和缓存成本不满足问题约束。

### 训练方法资格门

每个方法必须在同一个 frozen representation、同一个候选菜单、同一个探索策略、同一反馈延迟和同一事件预算下比较，并且：

1. 只读取选中候选的反馈；
2. 记录实际 propensity，并处理重复、乱序和候选版本；
3. p50/p95 更新延迟和状态大小均过门；
4. old holdout 的平均/峰值遗忘过门；
5. 相对于 RLS 和周期性 refit，在至少 10 个配对 stream seed 上有稳定的 reward 或恢复速度增益；
6. label-shuffle/no-feedback 控制不能得到同等增益。

如果一个方法只提高离线 accuracy，或只在知道所有候选真值时提高，直接淘汰。

## 5. 最小判别实验

先不要训练大模型或扫描大量超参。使用真实 peer/tool 小批量事件，建立一份可重放的 selected-only stream：

1. 对两个或三个小型候选 encoder 只做 frozen static probe，统一投影到同一维度 `d'`；
2. 冻结最佳和最弱但合格表示，各自运行 `no-update`、真正 rank-one RLS、一个受保护低秩更新候选；
3. 反馈按真实延迟或预注册的随机延迟到达，并打乱到达顺序；
4. 每个方法使用相同菜单、propensity、事件数和 A800 服务预算；
5. 报告 prequential reward、regret、漂移恢复步数、old-regime 遗忘、ECE、update p50/p95、状态大小和版本错配率。

选择的判据不是“谁的单次均值最高”，而是约束集合中的 Pareto 优势：

```text
reward gain > 0 with paired CI
forgetting <= epsilon
p95 latency <= B_update
state size <= B_memory
```

若所有非线性候选都不能在同预算下稳定超过 RLS，则论文应把 RLS 作为方法结论或收缩为系统论文；不能用更多模块掩盖没有增益。

## 6. 当前应锁定与尚不能锁定的内容

现在可以锁定的是：上述数学对象、selected-only/延迟/版本合约、old holdout 和四类硬指标。不能锁定的是 Laya、某个参数量，或 A/B/C 中哪一种更新算子。backbone 和训练方法要由第 5 节的小实验共同决定；先确定模型再改问题，会把工程偏好误写成科学结论。
