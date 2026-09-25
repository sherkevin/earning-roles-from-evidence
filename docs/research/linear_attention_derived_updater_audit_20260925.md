# 用 linear attention 标准审查在线 JEV 更新器

日期：2026-09-25

## 结论先行

当前文档中的

$$
s_{k+1}=U(s_k,B_k)
$$

只是接口定义，不是一个可审查创新。它没有说明状态如何计算、每条反馈的计算量、
状态大小、顺序语义或稳定性条件，因此不能凭它开始方法实验。

linear attention 提供了一个更严格的标准：必须从相似度分解得到结合律，再得到可
执行的递推和复杂度。把这个标准应用到我们的任务，可以得到一个**确实可计算的
候选更新器**；但它的核心公式本身等价于核回归/linear attention 的 associative
memory，暂时不能称为新算法。潜在创新只能来自 selected-only 延迟反馈、真实
consumer/judge 条件、角色迁移和抗遗忘约束的组合，并必须与已有核回归、RLS、
fast-weight 和 linear-attention memory 做逐项比较。

## 1. linear attention 为什么能落地

Katharopoulos 等人的原始推导从一般注意力开始。对 query、key 和 value，定义：

$$
V'_i=
\frac{\sum_{j=1}^{N}
\operatorname{sim}(Q_i,K_j)V_j}
{\sum_{j=1}^{N}\operatorname{sim}(Q_i,K_j)}.
$$

如果相似度可以写成非负特征映射的内积：

$$
\operatorname{sim}(q,k)=\phi(q)^\top\phi(k),
\qquad \phi(q),\phi(k)\ge0,
$$

则分子可以利用矩阵结合律重排：

$$
\left(\Phi(Q)\Phi(K)^\top\right)V
=
\Phi(Q)\left(\Phi(K)^\top V\right).
$$

对因果序列，定义两个累积状态：

$$
S_i=S_{i-1}+\phi(K_i)V_i^\top,
\qquad
Z_i=Z_{i-1}+\phi(K_i).
$$

输出变为：

$$
V'_i=
\frac{\phi(Q_i)^\top S_i}
{\phi(Q_i)^\top Z_i}.
$$

这四步给出了可执行算法，而不是只给出目标函数：每个新 token 只需更新
(S_i,Z_i)，历史不需要重新展开。若特征维度为 (C)、value 维度为 (M)，复杂度
为 (O(NCM))，状态大小与序列长度无关。非负特征和非零归一化分母是定义成立的
条件；复杂度结论不等于精度保证。原论文明确指出，精确 softmax 的指数核通常是
无限维，实际使用有限维近似或其他正核。

来源：[Fast Autoregressive Transformers with Linear Attention](https://proceedings.mlr.press/v119/katharopoulos20a.html)，
ICML 2020。

## 2. 将同一推导映射到 peer-judged role

当前研究对象的原始量是：

$$
(x_t,C_t,a_t,o_t,j_t,y_t,\delta_t,s_t).
$$

不新增环境原始概念，只定义两个派生表示：

$$
k_r=\phi_k(x_r,a_r,j_r),
\qquad
q_t(c)=\phi_q(x_t,c).
$$

这里 (r) 是产生反馈的 source decision index；(t) 是当前要做职责选择的
决策 index。将标量协作评分 (y_r\in[0,1]) 作为 value，定义延迟反馈到达后
的两个状态：

$$
S_k=\sum_{r:\tau_r<k}
\lambda^{k-\tau_r}k_r y_r,
\qquad
Z_k=\sum_{r:\tau_r<k}
\lambda^{k-\tau_r}k_r,
\qquad 0<\lambda\le1.
$$

对候选 producer (c\in C_t) 的预测为：

$$
\widehat y_t(c)=
\frac{q_t(c)^\top S_k}
{q_t(c)^\top Z_k+\varepsilon}.
$$

当反馈 (y_r) 在到达时刻 (k) 可用，若按 arrival/source watermark 顺序处理，
更新可以写成：

$$
S_{k+1}=\lambda^{\Delta_k}S_k+k_r y_r,
\qquad
Z_{k+1}=\lambda^{\Delta_k}Z_k+k_r,
$$

其中 \\(\Delta_k\\) 是两个已定义到达时刻之间的时间差，不是新的环境输入。若同一
到达批次包含多个反馈，应先按固定 source index 重放，或一次性累加；不能把它们
当作无序集合后又使用逐条 forgetting。

选择策略可以直接使用这个预测：

$$
\pi(c\mid x_t,C_t,s_k)
\propto
\exp\!\left(\widehat y_t(c)/T\right),
$$

并保留探索下界。此时 (s_k) 至少包含 (S_k,Z_k)，而不是一个未定义的黑箱。

## 3. 一个可以手算的 case

假设表示维度为 (2)，初始 (S_0=Z_0=(0,0))，先忽略衰减
(\lambda=1)。第 1 条到达反馈是：

$$
 k_1=(1,0),\qquad y_1=1.
$$

于是：

$$
S_1=(1,0),\qquad Z_1=(1,0).
$$

第 2 条到达反馈是：

$$
 k_2=(0,1),\qquad y_2=0.
$$

于是：

$$
S_2=(1,0),\qquad Z_2=(1,1).
$$

对两个新候选，若：

$$
q(c_A)=(1,0),\qquad q(c_B)=(0,1),
$$

则：

$$
\widehat y(c_A)=1,
\qquad
\widehat y(c_B)=0.
$$

这个 case 说明状态更新和候选打分都能直接实现；它不是效果实验，也不证明该
表示能识别真实角色。

## 4. 可以证明什么

若 (k_r,q_t(c)) 的每个分量非负、(y_r\in[0,1])、(\varepsilon>0)，则：

$$
0\le q_t(c)^\top S_k
\le q_t(c)^\top Z_k,
$$

从而：

$$
0\le\widehat y_t(c)\le1.
$$

若 \(\|k_r\|_1\le B_k\)，每条 feedback 只更新一次，且 (0<\lambda\le1)，则：

$$
\|S_k\|_1\le B_k,
\qquad
\|Z_k\|_1\le B_k\sum_{m=0}^{\infty}\lambda^m
=\frac{B_k}{1-\lambda}
$$

（当 \(\lambda<1\) 时）。因此状态不会随历史长度无限增长；这只是数值稳定性，
不是旧能力不遗忘的证明。

若表示维度为 (d)，标量 label 的每条反馈更新是 (O(d))，一个大小为
(|C_t|) 的候选菜单打分是 (O(|C_t|d))，状态大小是 (O(d))。如果 value 是
(m) 维角色证据，则对应为 (O(dm))。

## 5. 这是否已经构成创新

**不能直接称为创新。** 上面的 (S,Z) 递推是 linear attention 的累积 key-value
state，也等价于带指数遗忘的核加权回归/fast-weight memory。单独写出它，审稿人会
要求与 kernel regression、RLS、online SGD、linear attention memory 和 fast-weight
方法比较。

可能形成论文创新的部分不是“用了结合律”，而是需要同时满足：

1. 反馈只来自被执行 producer，未选 producer 没有标签；
2. label 延迟、乱序、重复和版本更换都能因果重放；
3. key 显式包含真实 consumer/judge 条件，但不把 judge 偏好误当客观任务真值；
4. 更新后的公共角色证据真的改变未来职责，而不是只改变内部参数；
5. 新任务适应、旧语义保持和 feedback-to-effective 延迟同时受约束；
6. 在相同表示、探索率、反馈量和状态预算下超过 RLS/核回归/静态模型。

这是一组待验证的创新假设，不是由公式自动推出的创新结论。

## 6. 开始实验前必须通过的数学门槛

- 明确 (\phi_k,\phi_q) 的维度、非负性、归一化和版本；
- 证明状态递推与历史核加权目标等价；
- 冻结 source-index/watermark 顺序和反馈尾部 flush 规则；
- 给出状态上界、预测范围和更新复杂度；
- 将 use/rework/reject 与 objective task success 分开记录；
- 与 RLS、kernel regression、静态 scorer 做同信息对照；
- 在旧语义 holdout 和概念变化流上分别测保持率与恢复时间。

没有通过这些门槛时，不能把一个能运行的递推称为“实时训练创新”；最多称为
可实现的 associative online baseline。
