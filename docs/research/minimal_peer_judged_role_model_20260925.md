# 最小 peer-judged role 模型

日期：2026-09-25

这份定义保留研究问题本身需要的最小符号：任务、候选 producer、交付物、实际
consumer/judge、判断结果、延迟和公共角色证据。把 judge 隐藏在一个抽象
evaluator 函数里，会把“从他人的判断学习角色”删掉，因此这里显式保留
\(j_t\)。

下面使用同一个贯穿案例：

- \(x_1\) 是任务 JSON：\(\{\texttt{task}:\texttt{summarize ticket T17},
  \texttt{stage}:\texttt{draft}\}\)；
- \(C_1=\{\texttt{agentA@v3},\texttt{agentB@v2}\}\) 是当前可选 producer；
- 选中的 producer 交付 JSON；
- agent A 是实际 owner/consumer，读取交付并作判断；
- 判断两轮后到达。

## 1. 原始概念

任务上下文和当前可承担任务的候选 producer 为：

$$
x_t\in\mathcal X,
\qquad
C_t\subseteq\mathcal A.
$$

**Case：** \(x_1\) 是上面的任务 JSON；\(C_1\) 的两个元素分别是
\(\texttt{agentA@v3}\) 和 \(\texttt{agentB@v2}\)。候选自身携带身份和版本，
不再单独定义版本符号。

根据上下文、候选集合和公共角色证据 \(s_t\)，系统选择 producer：

$$
a_t\sim\pi(\,\cdot\mid x_t,C_t,s_t),
\qquad
a_t\in C_t.
$$

**Case：** 当前证据认为 B 更适合处理引用整理，因此一次运行选择
\(a_1=\texttt{agentB@v2}\)。

执行 producer 后得到可被 consumer 读取的交付物：

$$
o_t\sim P_O(\,\cdot\mid x_t,a_t).
$$

**Case：** B 返回
\(\{\texttt{text}:\texttt{The ticket is about login timeout},
\texttt{citations}:[\texttt{log-17}]\}\)。

实际 consumer/judge 的身份为 \(j_t\)：

$$
j_t=\operatorname{owner}(x_t),
\qquad j_t\ne a_t.
$$

**Case：** \(x_1\) 的 owner 是 \(\texttt{agentA@v3}\)，所以
\(j_1=\texttt{agentA@v3}\)，且它不同于 producer
\(a_1=\texttt{agentB@v2}\)。如果 owner 不在上下文中，必须由冻结的任务分配器
单独产生；不能事后按标签反推 judge。

判断先按预先冻结的规则映射为标量质量；判断语义仍来自 consumer 对交付物的接受、
使用或返工行为：

$$
y_t=\rho_{j_t}(x_t,a_t,o_t)\in[0,1].
$$

**Case：** A 读取 B 的 JSON 并据此继续工作，故
\(y_1=1\)（\(\texttt{use}=1\)）；如果 A 要求修改则
\(y_1=0.5\)（\(\texttt{rework}=0.5\)），如果拒绝则
\(y_1=0\)（\(\texttt{reject}=0\)）。若 benchmark 只有客观成功/失败，
\(y_t\) 直接取 \(0\) 或 \(1\)。

标签从交付到可用于更新的延迟为 \(\delta_t\ge0\)：

$$
\tau_t=t+\delta_t.
$$

**Case：** A 在两轮后返回判断，因此 \(\delta_1=2\)，
\(\tau_1=3\)。

公共角色证据 \(s_t\) 只保存可依法传播的 producer 证据；它不是
consumer 的私有信念，也不是研究者事后写入的 gold：

$$
s_{k+1}=U(s_k,B_k),
$$

其中已到达判断集合为：

$$
B_k=
\left(
(x_t,C_t,a_t,j_t,o_t,y_t)
\right)_{t:\tau_t=k}.
$$

**Case：** \(B_3\) 包含
\((x_1,C_1,\texttt{agentB@v2},\texttt{agentA@v3},o_1,1)\)；
\(U\) 用这个事件更新 B 的公开角色证据，例如增加
\(B\) 在“引用整理”情境下承担后续职责的权重。

下一次职责分配再次读取公共证据：

$$
a_{t+1}\sim
\pi(\,\cdot\mid x_{t+1},C_{t+1},s_{t+1}).
$$

**Case：** 新任务要求整理引用时，更新后的 \(s_4\) 使 B 的选择概率上升；
这一步才证明“判断进入了未来职责”，仅有 \(s_4\) 数值变化还不够。

## 2. 目标和约束

长期目标是预先冻结的协作评分，不自动等同于客观任务成功：

$$
J_T(\pi,U)
=
\mathbb E\!\left[
\frac1T\sum_{t=1}^{T}y_t
\right].
$$

**Case：** 三轮判断为 \(\texttt{use},\texttt{rework},\texttt{use}\)，对应协作评分
\(1,0.5,1\)，该轨迹的经验效用为 \(5/6\)。

更新后的旧任务风险不能显著变坏。给定锁定的旧任务集合
\(\mathcal D_{\mathrm{old}}\)，定义：

$$
F_T=
\left[
\max_{0\le k\le T}
\bigl(L_{\mathrm{old}}(s_k)-L_{\mathrm{old}}(s_0)\bigr)
\right]_+.
$$

**Case：** 100 个旧任务上的职责选择准确率由 \(0.82\) 降到
\(0.79\)，则该运行的最大遗忘为 \(F_T=0.03\)。

每次判断进入公共证据的时间预算为：

$$
Q_{0.95}\!\left(
\operatorname{latency}(U)
\right)
\le B_{\mathrm{update}}.
$$

**Case：** 若预算为 \(10\mathrm{ms}\)，测得 p95 为 \(4.1\mathrm{ms}\)，
则满足实时更新约束。

最终求解的是：

$$
\begin{aligned}
\underset{\pi,U}{\operatorname{maximize}}\quad
&J_T(\pi,U)\\
\text{subject to}\quad
&F_T\le\varepsilon_{\mathrm{old}},\\
&Q_{0.95}\!\left(\operatorname{latency}(U)\right)
\le B_{\mathrm{update}}.
\end{aligned}
$$

**Case：** 若 \(\varepsilon_{\mathrm{old}}=0.02\)，则
\(F_T=0.03\) 的更新器不能作为最终方法，即使它提高了新任务效用。

## 3. 与另一个项目的对应

tool selection 中，\(a_t\) 是被调用的 tool，\(o_t\) 是 tool 返回值，
\(j_t\) 是环境 evaluator，\(y_t\) 是二值正确性；同一个
\(U\) 可以更新 tool 的公共选择证据。

动态 JEV 中，\(x_t\) 还包含当前 episode 已观察到的 provider 输出，
\(a_t\) 是下一次 call 或 STOP，\(o_t\) 是即时 provider 输出，
\(j_t\) 是 terminal evaluator。若一个 terminal label 同时覆盖多个
provider call，必须把这些 call 放在同一反馈组；这属于 JEV 的上层反馈范围，
不能把它伪装成 earning-roles 的单步 selected-only 标签。

## 结论

对 earning-roles，最小且不丢失故事对象的原始符号是：

$$
\boxed{(x_t,C_t,a_t,o_t,j_t,y_t,\delta_t,s_t)}.
$$

其中 \(j_t\) 不能在 peer-judged role 问题中删除；若任务使用客观 evaluator，
才可把 \(j_t\) 特化为固定环境评估者。backbone 只负责从
\((x_t,a_t)\) 生成表示，训练方法只负责实现 \(U\)，二者仍需在相同
判断事件和未来职责指标下由实验确定。
