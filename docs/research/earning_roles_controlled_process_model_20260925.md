# earning-roles 的最终数学建模候选

日期：2026-09-25

## 结论

当前的 CDS-CB（受约束延迟选择性反馈上下文 bandit）是单步选择器的正确模型，
但不是 earning-roles 故事的完整模型。

原因是：选择某个 peer 可能改变后续交付、信任、角色和工作流状态。若动作会改变
未来环境，纯 bandit 的假设就不成立。

对当前研究目标，最小而足够的总模型是：

> 带隐藏协作状态、动态候选集合、即时观测、延迟选择性反馈和在线学习状态的受约束控制过程。

数学上，这是一个隐藏状态控制过程；严格求解时，它属于部分可观测的控制过程。
工程中的在线状态是对真实 belief 的有限近似，而不是环境状态本身。

## 1. 状态和变量

在决策时刻 \(t\)，定义：

- \(Z_t\)：隐藏的真实协作状态，包括 agent 潜在能力、角色适配度、工作流阶段、信任、负载和 peer 图；
- \(X_t\)：从 \(Z_t\) 中可观测的任务上下文；
- \(G_t\)：当前 peer 图；
- \(C_t\)：当前可选候选集合，peer 选择中通常为 \(N_{G_t}(i_t)\)；
- \(M_t\)：选择器的在线学习状态，包括参数、后验、replay 统计量和版本；
- \(b_t\)：对隐藏状态的 belief；
- \(A_t\)：实际选择的 peer 或 tool；
- \(O_t\)：执行 \(A_t\) 后立即可见的原始输出或交付结果；
- \(Y_t\)：对 \(A_t\) 的正确性或质量标签；
- \(\Lambda_t\subseteq C_t\)：本次反馈组覆盖的候选集合；earning-roles 中
  \(\Lambda_t=\{A_t\}\)，动态 JEV 中可以是同一 episode 的 called set；
- \(D_t\)：从决策到反馈可用的延迟。

信念状态写成：

$$
b_t
=
P\!\left(Z_t \mid \mathcal{F}_t\right),
$$

其中 \(\mathcal{F}_t\) 是当前已经可见的任务、历史动作、即时输出和已到达反馈。

必须区分：

$$
O_t = \text{立即可见的执行输出},
\qquad
Y_t = \text{延迟到达的真实性能标签}.
$$

没有即时输出的任务可以令 \(O_t=\varnothing\)。

## 2. 一次决策如何产生

策略根据 belief、在线状态、任务上下文和候选集合选择动作：

$$
A_t
\sim
\pi\!\left(
\cdot \mid b_t,M_t,X_t,C_t
\right).
$$

实际行为概率必须记录：

$$
p_t
=
\pi\!\left(
A_t \mid b_t,M_t,X_t,C_t
\right).
$$

选择动作后，系统立即得到原始输出：

$$
O_t
\sim
\Omega\!\left(
\cdot \mid Z_t,A_t
\right).
$$

如果 peer 选择会改变之后的协作环境，则环境状态转移为：

$$
Z_{t+1}
\sim
P_Z\!\left(
\cdot \mid Z_t,A_t,O_t
\right).
$$

候选集合也可能随状态变化：

$$
C_{t+1}
\sim
P_C\!\left(
\cdot \mid Z_t,A_t,O_t
\right).
$$

如果实验发现动作不改变未来状态，则可退化为：

$$
P_Z\!\left(
Z_{t+1}\mid Z_t,A_t,O_t
\right)
=
P_Z\!\left(
Z_{t+1}\mid Z_t
\right),
$$

此时才可以使用 contextual bandit 作为主模型。

## 3. 潜在结果和延迟反馈

对于当前候选集合，所有候选的潜在结果是一个联合随机变量：

$$
Y_t(C_t)
\sim
P_Y\!\left(
\cdot \mid Z_t,C_t
\right).
$$

不能默认同一任务中不同候选的结果相互独立。动态 JEV 中多个 provider 共享同一实验真值，就是一个相关标签的例子。

实际只执行一个候选，因此在线只观察：

$$
Y_t
=
Y_t(A_t).
$$

这是 earning-roles 单步选择的形式。动态 JEV 的一次实验真值可能给多个已调用
provider 产生标签，应记录为同一反馈组：

$$
\left\{Y_t(c):c\in\Lambda_t\right\}.
$$

同一反馈组中的标签共享真值，不能当作相互独立的样本。

标签延迟到达：

$$
\tau_t
=
t+D_t,
\qquad
D_t\ge 0.
$$

在到达时间 \(k\) 收到的事件集合是：

$$
B_k
=
\left\{
e_t:\tau_t=k
\right\}.
$$

在线更新器只能读取已经到达的 \(B_k\)：

$$
M_{k+1}
=
U_\psi\!\left(
M_k,B_k
\right).
$$

如果事件乱序，\(U_\psi\) 必须满足以下一种语义：

1. 将事件转换为可交换、可结合的充分统计量，使不同合法到达顺序得到同一状态；
2. 保存事件并按决策时间重放，同时记录 replay watermark。

只把事件放进 FIFO 队列，不等于解决了延迟和乱序反馈。

## 4. 事件和版本绑定

每条反馈事件必须绑定决策时信息：

$$
e_t
=
\left(
t,
X_t,
C_t,
A_t,
p_t,
H_t,
O_t,
V_t,
\tau_t,
Y_t
\right),
$$

其中：

- \(H_t\) 是决策时的历史或 feature snapshot；
- \(V_t\) 是候选、模型和特征协议版本；
- \(p_t\) 是实际 behavior propensity；\(\Lambda_t\) 和 feedback group id
  记录本次反馈覆盖的候选。

反馈到达后，不能使用新模型重新编码旧候选，也不能把旧版本的标签写入新版本。

## 5. earning-roles 的目标

长期目标是未来协作效用，而不是当前标签拟合：

$$
J_T(\pi,U_\psi)
=
\mathbb{E}
\left[
\frac{1}{T}
\sum_{t=1}^{T}
\left(
R_t
-
\kappa_{\mathrm{call}}\,C_t^{\mathrm{call}}
-
\kappa_{\mathrm{explore}}\,C_t^{\mathrm{explore}}
\right)
\right].
$$

其中 \(R_t\) 可以是：

- 交付是否被接受；
- 交付是否被后续 agent 使用；
- 返工成本的反向分数；
- 最终任务质量；
- 对未来角色分配的贡献。

若离线 benchmark 能提供每个候选的完整结果，才计算动态 regret：

$$
\operatorname{Reg}_T
=
\mathbb{E}
\left[
\sum_{t=1}^{T}
\left(
\max_{a\in C_t} R_t(a)
-
R_t(A_t)
\right)
\right].
$$

完整候选结果只能用于离线评估，不能进入在线更新。

## 6. 稳定性、实时性和可识别性约束

锁定旧任务分布 \(D_{\mathrm{old}}\)，定义当前在线状态在旧任务上的风险：

$$
L_{\mathrm{old}}(M)
=
\mathbb{E}_{(X,C)\sim D_{\mathrm{old}}}
\left[
\ell\!\left(
\pi_M,X,C
\right)
\right].
$$

以发布前状态 \(M_{\mathrm{ref}}\) 为参照，最大遗忘为：

$$
F_{\mathrm{peak}}
=
\max_t
\left[
L_{\mathrm{old}}(M_t)
-
L_{\mathrm{old}}(M_{\mathrm{ref}})
\right]_+.
$$

必须满足：

$$
F_{\mathrm{peak}}
\le
\varepsilon_{\mathrm{old}}.
$$

实时和内存约束写成：

$$
Q_{0.95}\!\left(L^{\mathrm{update}}\right)
\le
B_{\mathrm{update}},
$$

$$
Q_{0.95}\!\left(L^{\mathrm{decision}}\right)
\le
B_{\mathrm{decision}},
$$

$$
\max_t \operatorname{Memory}(M_t)
\le
B_{\mathrm{memory}}.
$$

selected-only 数据还需要满足可识别性条件：

$$
p_t(a)
\ge
p_{\min}
\quad
\text{for eligible candidates }a,
$$

或者在整个评估窗口内保证足够的累计曝光。没有探索，未选候选的质量无法从
selected-only 日志中识别。

## 7. 完整优化问题

在满足因果、selected-only、版本、探索和资源约束的算法集合
\(\mathcal{A}\) 中，优化问题是：

$$
\max_{(\pi,U_\psi)\in\mathcal{A}}
\quad
\liminf_{T\to\infty}
J_T(\pi,U_\psi)
$$

subject to：

$$
F_{\mathrm{peak}}
\le
\varepsilon_{\mathrm{old}},
$$

$$
Q_{0.95}(L^{\mathrm{update}})
\le
B_{\mathrm{update}},
\qquad
Q_{0.95}(L^{\mathrm{decision}})
\le
B_{\mathrm{decision}},
$$

$$
\max_t \operatorname{Memory}(M_t)
\le
B_{\mathrm{memory}},
$$

以及：

$$
U_\psi
\text{ 只能读取已经到达的 selected-only 事件。}
$$

这比把正确率、遗忘、延迟和内存随意加权更干净。若预算尚未确定，应先报告
效用—遗忘—延迟的 Pareto frontier。

## 8. 动态 JEV 是这个模型的另一个特例

动态 JEV 在一个 episode 内有内部步 \(j\)：

$$
a_{e,j}
\in
\mathcal{P}_e
\cup
\{\mathrm{STOP}\}.
$$

调用 provider 后立即得到：

$$
O_{e,j}
\sim
\Omega\!\left(
\cdot\mid Z_{e,j},a_{e,j}
\right),
$$

并更新题内历史：

$$
H_{e,j+1}
=
T\!\left(
H_{e,j},a_{e,j},O_{e,j}
\right).
$$

episode 最后输出答案或拒答，损失为：

$$
L_{\mathrm{episode}}
=
\ell_{\mathrm{prediction}}
+
\lambda_{\mathrm{call}}\,N_{\mathrm{call}}
+
\lambda_{\mathrm{abstain}}\,
\mathbf{1}\{\mathrm{abstain}\}.
$$

因此动态 JEV 是：

- 有限 horizon；
- call/STOP 动作；
- 即时信息获取；
- terminal answer/abstention；
- 延迟真值反馈。

earning-roles 当前第一阶段则是：

- 每个 tick 选择一个局部候选；
- 没有默认 STOP/abstention；
- 目标是长期 stream utility；
- 如果动作不改变未来状态，退化为 delayed contextual bandit；
- 如果动作改变未来状态，保留完整控制过程。

## 9. 这个模型为什么是当前最小充分模型

如果使用纯 contextual bandit，会遗漏 peer 选择对未来协作状态的因果影响。

如果使用完全自由的 POMDP，状态、转移和观测过于宽泛，当前数据无法识别，实验
也无法解释。

当前模型只保留我们确实需要的变量：

$$
\text{hidden collaboration state}
+
\text{dynamic candidates}
+
\text{immediate output}
+
\text{delayed selective feedback}
+
\text{online learner state}
+
\text{hard resource constraints}.
$$

它还能在不同假设下退化：

- 状态完全可观测、动作改变未来：MDP/CMDP；
- 状态隐藏、动作改变未来：POMDP；
- 动作不改变未来、每个 tick 一次选择：delayed contextual bandit；
- 动态 JEV：有限时域 call/STOP/answer/abstention POMDP。

因此，当前建议把它作为 earning-roles 的完整数学模型，把 CDS-CB 作为第一阶段
可执行子问题，把动态 JEV 作为顺序信息获取特例。
