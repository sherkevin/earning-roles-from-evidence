# 最小在线选择模型：符号、依赖与贯穿案例

日期：2026-09-25

## 建模原则

只把在线数据生成链中不可再删的概念作为原始符号。模型参数、表示函数和更新器是函数，不是新的环境输入。历史并入当前上下文；候选身份和版本并入候选对象；propensity 是策略的派生量，不进入基础定义。只有实验证明动作会改变未来任务分布时，才增加显式隐藏状态。

下面所有公式都用同一个 peer-selection case 解释：

- 任务上下文是 JSON：\(\{\texttt{task}:\texttt{summarize ticket T17},\texttt{stage}:\texttt{draft}\}\)；
- 两个候选是 \(\texttt{agentA@v3}\) 与 \(\texttt{agentB@v2}\)；
- 执行后的交付物由 evaluator 判定是否正确；
- evaluator 在两轮后返回标签。

## 1. 原始符号

第 \(t\) 次决策的可见上下文和候选集合为：

$$
x_t\in\mathcal X,
\qquad
C_t\subseteq\mathcal A.
$$

**Case：** \(x_1\) 是上面的任务 JSON；\(C_1=\{\texttt{agentA@v3},\texttt{agentB@v2}\}\)。如果版本变化，直接把 \(\texttt{agentB@v3}\) 当作新的候选元素，不额外定义版本变量。

候选对象可以写成：

$$
c=(\mathrm{id},\mathrm{description},\mathrm{version}).
$$

**Case：** \(\texttt{agentB@v2}\) 的三个字段分别是 agent 身份、角色描述和实现版本。

在线状态 \(s_t\) 是算法内部可写状态，例如选择头的参数及其统计量；它不是新的任务输入。

## 2. 从输入到反馈的最小链

### 2.1 表示

给定待评估的 backbone \(\phi_\omega\)，候选表示为：

$$
z_{t,a}=\phi_\omega(x_t,a)\in\mathbb R^d,
\qquad
a\in C_t.
$$

**Case：** 把任务 JSON 的 text 与候选描述拼接后输入候选 encoder。为说明符号，假设一次 toy encoder 输出 \(d=4\)：

$$
z_{1,\texttt{agentA@v3}}=(0.20,0.70,0.10,0.40),
\qquad
z_{1,\texttt{agentB@v2}}=(0.80,0.10,0.40,0.20).
$$

这两个四维向量只是实例化，不代表最终 backbone 已经确定。

### 2.2 选择

策略从当前候选集合中选择一个动作：

$$
a_t\sim\pi(\,\cdot\mid x_t,C_t,s_t),
\qquad
a_t\in C_t.
$$

**Case：** 当前选择头给 agent A 的分数为 \(0.50\)，给 agent B 的分数为 \(0.60\)，并使用带探索的 softmax；一次运行可能采样 \(a_1=\texttt{agentB@v2}\)。

### 2.3 即时输出

执行动作后立即获得原始输出：

$$
o_t\sim P_O(\,\cdot\mid x_t,a_t).
$$

**Case：** \(a_1=\texttt{agentB@v2}\) 返回 JSON：\(\{\texttt{text}:\texttt{The ticket is about login timeout},\texttt{citations}:[\texttt{log-17}]\}\)。没有中间输出的 benchmark 令 \(o_t=\bot\)。

若同一 episode 还要继续决策，已观察到的输出并入下一次上下文：

$$
x_{t+1}=\operatorname{append}(x_t,a_t,o_t).
$$

**Case：** 动态 JEV 的第二次 provider call 的输入包含第一次 call 的 provider 名称和返回 JSON；独立的 peer 任务流可由外部直接提供新的 \(x_{t+1}\)。

### 2.4 质量

每个候选对当前任务都有一个潜在质量 \(y_t(a)\)，但在线只执行一个候选：

$$
y_t(a)\in[0,1]\quad(a\in C_t),
\qquad
y_t=y_t(a_t).
$$

**Case：** evaluator 检查 agent B 的 JSON 是否解决 T17，得到 \(y_1=1\)。agent A 没有被执行，因此 \(y_1(\texttt{agentA@v3})\) 不可见。

实际标签来自执行输出，而不是和输出脱钩的第二个输入：

$$
y_t=\rho(x_t,a_t,o_t,\xi_t),
$$

其中 \(\xi_t\) 是 evaluator 或任务环境的随机性。

**Case：** \(\rho\) 读取上述 JSON；文本和引用都满足检查规则时输出 \(1\)，否则输出 \(0\)。

### 2.5 延迟

标签从执行到可用的延迟为 \(\delta_t\ge0\)，到达时刻为：

$$
\tau_t=t+\delta_t.
$$

**Case：** 第 \(1\) 轮执行 B，evaluator 两轮后返回，因此 \(\delta_1=2\)，标签在第 \(3\) 轮可用。

第 \(k\) 轮新到达的反馈集合是：

$$
B_k=
\left\{
(x_t,C_t,a_t,o_t,y_t):\tau_t=k
\right\}.
$$

**Case：** \(B_3\) 包含第 \(1\) 轮的任务 JSON、候选集合、agent B、返回 JSON 和标签 \(1\)；还未返回的标签不在 \(B_3\) 中。

### 2.6 更新

在线更新器读取当前状态和已经到达的反馈：

$$
s_{k+1}=U_\psi(s_k,B_k).
$$

**Case：** \(s_0\) 是零初始化的线性选择头及其统计量。RLS、online SGD 或候选的新更新器都接收同一个 \(B_3\)，得到下一状态；因此它们在相同数据协议下比较。

## 3. 优化目标和硬约束

未来选择的平均质量是：

$$
J_T(\pi,U_\psi)
=
\mathbb E\!\left[
\frac1T\sum_{t=1}^{T}y_t(a_t)
\right].
$$

**Case：** 一条三轮轨迹的实际标签是 \(1,0,1\)，其经验效用是 \(2/3\)；未执行候选的潜在标签不能进入在线求和。

固定更新前的旧任务集合 \(\mathcal D_{\mathrm{old}}\)，令 \(L_{\mathrm{old}}(s)\) 表示状态 \(s\) 在该集合上的选择损失。最大遗忘定义为：

$$
F_T=
\left[
\max_{0\le k\le T}
\bigl(L_{\mathrm{old}}(s_k)-L_{\mathrm{old}}(s_0)\bigr)
\right]_+.
$$

**Case：** 旧任务集合包含 100 个已锁定任务，更新前准确率为 \(0.82\)，更新期间最低为 \(0.79\)，则 \(F_T=0.03\)。

更新延迟约束为：

$$
Q_{0.95}\!\left(
\operatorname{latency}(U_\psi)
\right)
\le B_{\mathrm{update}}.
$$

**Case：** 预算 \(B_{\mathrm{update}}=10\mathrm{ms}\)，1000 次更新的 p95 为 \(4.1\mathrm{ms}\)，则满足实时约束。

最小约束优化问题是：

$$
\begin{aligned}
\underset{\pi,U_\psi}{\operatorname{maximize}}\quad
&J_T(\pi,U_\psi)\\
\text{subject to}\quad
&F_T\le\varepsilon_{\mathrm{old}},\\
&Q_{0.95}\!\left(\operatorname{latency}(U_\psi)\right)
\le B_{\mathrm{update}}.
\end{aligned}
$$

**Case：** 若允许最大遗忘 \(\varepsilon_{\mathrm{old}}=0.02\)，前述 \(F_T=0.03\) 的方法即使平均效用较高，也不能作为最终方案。

## 4. 只在证据出现后增加的概念

如果实验显示选择不同 peer 会改变未来任务分布，才增加显式转移：

$$
x_{t+1}\sim P_X(\,\cdot\mid x_t,a_t,o_t).
$$

**Case：** 选择 agent A 会使下一阶段进入返工状态，而选择 agent B 不会，且该状态无法从当前 \(x_{t+1}\) 直接观察；这时再引入隐藏环境状态和 belief。没有该证据时，直接使用第 1--3 节的模型。

如果需要 IPS 离线评估，propensity 由策略派生：

$$
p_t=\pi(a_t\mid x_t,C_t,s_t).
$$

**Case：** 只有在评估日志策略与目标策略的差异时记录 \(p_t\)；它不是在线选择问题的新原始输入。

## 结论

基础问题只需要：

$$
\boxed{(x_t,C_t,a_t,o_t,y_t,\delta_t,s_t)}.
$$

\(x_t,C_t\) 是输入，\(a_t\) 是动作，\(o_t\) 是可选即时输出，\(y_t\) 是被选动作的延迟质量，\(\delta_t\) 是延迟，\(s_t\) 是在线可写状态。backbone 是 \(\phi_\omega\)，训练方法是 \(U_\psi\)；二者必须在同一数据协议和约束下由实验确定。
