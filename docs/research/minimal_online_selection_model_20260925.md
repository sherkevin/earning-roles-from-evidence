# 最小在线选择模型：符号、依赖与贯穿案例

日期：2026-09-25  
状态：earning-roles 的数学建模候选；用于替换过度展开的控制过程版本。

## 建模原则

先只保留在线选择真正需要的原始概念：任务上下文、候选集合、被选候选、即时输出、延迟质量反馈和在线状态。模型参数、表示函数和更新器是函数，不是新的环境输入；日志字段、propensity、图、版本号和 belief 暂不作为原始符号。

只有实验确认“动作会改变未来任务分布”以后，才增加状态转移；只有需要离线逆倾向评估时，才从策略中派生 propensity。这样不会把工程实现字段误当成问题定义。

## 0. 一组贯穿案例

下面固定一个 peer-selection 案例，所有公式都用它实例化。

在第 (t=1) 次决策：

- 任务上下文 (x_1) 是 JSON：
  `{"task":"summarize ticket T17","stage":"draft"}`；
- 候选集合 (C_1={	exttt{agentA@v3},	exttt{agentB@v2}})；候选对象自身包含身份和版本，不另定义 (V_t)；
- 候选 agent 返回交付物后，外部 evaluator 给出二值质量标签；
- 反馈延迟两轮，即 (delta_1=2)。

tool-selection 只需把 (x_1) 换成工具任务 JSON，把候选换成工具对象；数学符号不变。

## 1. 原始输入和动作

第 (t) 次决策的任务上下文是 (x_t)，当前可执行候选集合是 (C_t)：

$$
x_tinmathcal X,
\qquad
C_tsubseteqmathcal A.
$$

**Case：** (x_1) 就是上面的 JSON；(C_1) 的两个元素分别是 `agentA@v3` 和 `agentB@v2`。如果候选版本变化，就形成新的候选元素，例如 `agentB@v3`，不再额外引入版本符号。

策略从当前集合中选择一个动作 (a_t)：

$$
a_tsim pi_{	heta_t}(,cdotmid x_t,C_t),
\qquad
a_tin C_t.
$$

**Case：** 对 (C_1) 计算两个候选分数，若 (epsilon)-greedy 策略以 (0.9) 概率选择最高分候选、以 (0.1) 概率均匀探索，某次运行采样得到 (a_1=	exttt{agentB@v2})。

候选表示由一个待选择的 backbone (phi_omega) 生成：

$$
z_{t,a}=phi_omega(x_t,a)inmathbb R^d,
\qquad ain C_t.
$$

**Case：** 将 (x_1) 的 `task`、`stage` 和候选 agent 的描述文本拼接后输入候选 encoder；为便于说明，假设一次实验得到 (d=4) 的 toy 表示 (z_{1,	exttt{agentB@v2}}=(0.8,0.1,0.4,0.2))。这个四维向量只是符号实例，不代表最终 backbone 已经选定。

## 2. 即时输出和潜在质量

执行 (a_t) 后可能立即得到原始输出 (o_t)：

$$
o_tsim P_O(,cdotmid x_t,a_t).
$$

**Case：** (a_1=	exttt{agentB@v2}) 返回
`{"text":"The ticket is about login timeout","citations":["log-17"]}`；若某个 benchmark 只有最终标签而没有中间输出，则令 (o_t=ot)。

如果需要在同一 episode 内继续决策，下一次上下文直接包含已经观察到的输出：

$$
x_{t+1}=\operatorname{append}(x_t,a_t,o_t).
$$

**Case：** 动态 JEV 在第一次 provider call 后把 provider 名称和返回 JSON 追加到问题上下文，得到第二次 call 的 (x_2)。earning-roles 的独立任务流则由外部产生新的 (x_{t+1})，不强行假设动作改变下一题。

每个候选在该次任务上都有一个潜在质量 (y_t(a))，但在线只会执行并评价被选候选：

$$
y_t(a)in[0,1]quad(ain C_t),
\qquad
y_t=y_t(a_t).
$$

**Case：** evaluator 检查 agent B 的 JSON 是否解决 T17，得到 (y_1=1)；没有执行 agent A，所以 (y_1(	exttt{agentA@v3})) 不可见，不得写入训练日志。

## 3. 延迟反馈和在线更新

反馈从决策到可用的延迟为 (delta_tge0)，到达时刻为：

$$
	au_t=t+delta_t.
$$

**Case：** 第 (1) 轮选择 B，evaluator 需要两轮才返回结果，因此 (delta_1=2)，标签在第 (3) 轮结束时可用。

时刻 (k) 新到达的反馈集合只由上述原始字段组成：

$$
B_k=
\left\{
(x_t,C_t,a_t,o_t,y_t):\tau_t=k
\right\}.
$$

**Case：** (B_3) 包含
`(x_1, {agentA@v3,agentB@v2}, agentB@v2, {"text":...}, 1)`；没有到达的标签不在 (B_3) 中。

令 (s_t) 表示在线选择器的可写状态（例如线性头参数及其统计量），更新器为 (U_psi)：

$$
s_{k+1}=U_psi(s_k,B_k).
$$

**Case：** 初始 (s_0) 是零初始化的选择头；第 (3) 轮收到 (B_3) 后，RLS、online SGD 或候选的新型更新器各自把同一个 (B_3) 转成 (s_4)。因此三种训练方法可以在同一数据协议下公平比较。

注意：(phi_omega,pi_{	heta_t},U_psi) 是可替换的函数；(x_t,C_t,a_t,o_t,y_t,delta_t) 才是这个在线问题的原始数据概念。

## 4. 优化目标

在 (T) 次选择上的平均真实效用为：

$$
J_T(pi,U_psi)
=
\mathbb E\!\left[
\frac1T\sum_{t=1}^{T}y_t(a_t)
\right].
$$

**Case：** 若三次实际选择的标签为 (1,0,1)，则该条轨迹的经验效用为 (2/3)；未选择候选的潜在标签不能进入这条在线求和。

最终要寻找的是同时决定“如何选”和“如何更新”的一对函数：

$$
(\pi^\star,U^\star)
=
\underset{\pi,U}{\operatorname{argmax}}
\;J_T(\pi,U).
$$

**Case：** 在同一个真实数据流、相同候选集合和相同探索率下，比较 `RLS`、`online SGD` 和新更新器；哪个组合在未来窗口的平均 (y_t) 更高，才有资格继续作为候选方法。

## 5. 稳定性和实时性约束

在更新前固定一份旧任务集合 (mathcal D_{m old})，令 (L_{m old}(s)) 为状态 (s) 在该集合上的选择损失。最大遗忘定义为：

$$
F_T
=
\left[
\max_{0\le k\le T}
\bigl(L_{\rm old}(s_k)-L_{\rm old}(s_0)\bigr)
\right]_+.
$$

**Case：** (mathcal D_{m old}) 是 100 个已锁定的历史任务；更新前选择准确率为 (0.82)，更新过程中最低为 (0.79)，则这条运行的 (F_T=0.03)。

更新延迟约束为：

$$
Q_{0.95}\!\left(\operatorname{latency}(U_\psi)\right)
\le B_{\rm update}.
$$

**Case：** 若产品预算 (B_{m update}=10\mathrm{ms})，测得 1000 次更新的 p95 为 (4.1\mathrm{ms})，则满足实时约束。

因此最小约束优化问题是：

$$
\begin{aligned}
\underset{\pi,U_\psi}{\operatorname{maximize}}\quad
&J_T(\pi,U_\psi)\\
\text{subject to}\quad
&F_T\le\varepsilon_{\rm old},\\
&Q_{0.95}\!\left(\operatorname{latency}(U_\psi)\right)
\le B_{\rm update}.
\end{aligned}
$$

**Case：** 若允许最大遗忘 (\varepsilon_{\rm old}=0.02)，则上一个 (F_T=0.03) 的方法即使效用更高，也不能作为最终方案。

## 6. 何时才增加隐藏状态或更多符号

上述模型把动作影响未来的部分吸收到下一次上下文 (x_{t+1}) 中。只有实验显示“选择不同 peer 会改变未来任务分布”，才增加显式转移：

$$
x_{t+1}\sim P_X(\,cdot\mid x_t,a_t,o_t).
$$

**Case：** 如果选择 agent A 会使后续任务进入“需要返工”阶段，而选择 agent B 不会，且这一变化无法从 (x_{t+1}) 直接观察，就需要把隐藏环境状态单独建模；在此证据出现前，不引入 (Z_t) 或 belief (b_t)。

同理，propensity 只是由策略派生的量：

$$
p_t=\pi_{\theta_t}(a_t\mid x_t,C_t),
$$

**Case：** 只有做 IPS 离线评估时才记录 (p_t)；它不是在线选择问题的新增原始输入。候选图、候选版本和完整事件日志也遵循同一原则：能放进 (x_t) 或候选对象的，不另起符号。

## 结论

当前应冻结的数学对象只有：

$$
\boxed{(x_t,C_t,a_t,o_t,y_t,\delta_t,s_t)}.
$$

其中 (x_t,C_t) 是任务输入，(a_t) 是动作，(o_t) 是可选的即时观测，(y_t) 是被选动作的延迟质量，(delta_t) 是延迟，(s_t) 是在线可写状态。backbone 是 (phi_omega)，训练方法是 (U_psi)；二者仍应通过真实数据上的受控比较确定。

