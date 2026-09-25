# 有界残差快权更新器：实验前的数学候选

日期：2026-09-25  
状态：候选方案，尚未宣称创新或通过真实数据验证。本文的作用是把一个
可以被证伪、可以计算复杂度和稳定性边界的更新器交给小规模实验，而不是
把 DeltaNet、RLS 或线性注意力的已有结果改名。

## 1. 只增加一个可实现的表示分解

沿用最小在线选择模型中的任务上下文 (x_t)、候选 (a_t)、质量标签
(y_tin[0,1]) 和到达批次 (B_k)。候选在决策时得到一个**稳定地址**
(k_tinmathbb R^m)，任务得到一个**当前查询** (q_tinmathbb R^m)：

$$
k_t=P_k\,\phi_k(a_t),\qquad
q_t=P_q\,\phi_q(x_t),qquad
\lVert k_t\rVert_2=\lVert q_t\rVert_2=1.
$$

这里 (P_k,P_q) 是冻结的低维投影，(m) 是小常数（第一版建议
(m\in\{16,32\})）。稳定地址只含候选身份、版本和不随当前任务改变的描述；
当前任务文本不能拼进 (k_t)。例如：

- (a_t=\texttt{agentB@v2})，(phi_k(a_t)) 是候选注册表文本的冻结编码，
  (P_kphi_k(a_t)) 归一化后得到 (k_tin\mathbb R^{16})；
- (x_t=\{\texttt{task}:\texttt{summarize T17},\texttt{stage}:\texttt{draft}\})，
  (P_qphi_q(x_t)) 归一化后得到 (q_tin\mathbb R^{16})。

这不是新增环境输入，而是同一 (x_t,a_t) 的固定表示函数。候选版本变化必须
改变 (k_t)，否则旧版本标签会写入新版本。

## 2. 基线加一个有界的快速残差

冻结模型给出先验分数 (s_0(q,k))。在线状态只有一个小矩阵
(R_k\in\mathbb R^{m\times m})，初值为 (0)：

$$
s_k(q,k)=s_0(q,k)+q^\top R_k k,
\qquad
\hat y_k(q,k)=\operatorname{clip}_{[0,1]}(s_k(q,k)).
$$

收到一条事件 (e=(q,k,y)) 后，先对旧残差衰减，再用标签残差写入：

$$
\begin{aligned}
\tilde R&=\alpha R_k,\\
e_y&=y-\operatorname{clip}_{[0,1]}\bigl(s_0(q,k)+q^\top\tilde R k\bigr),\\
R_{k+1}&=\Pi_\rho\left(\tilde R+
   \frac{\eta e_y}{1+\varepsilon}\,qk^\top\right).
\end{aligned}
$$

参数为 (0\le\alpha<1)、(0<\eta\le1)、(arepsilon>0)，
(Pi_\rho) 是 Frobenius 球 ({R:\lVert R\rVert_F\le\rho}) 上的投影。
因为 (q,k) 已归一化且 (|e_y|\le1)，每条反馈只做一个外积和一次投影；
第一版 (m=16) 时状态为 256 个浮点数。投影可在小矩阵上精确做，或采用等价
的范数裁剪并记录其实现。

同一到达索引 (k) 的多条反馈采用批量定义，消除 FIFO 顺序歧义。令
(B_k=\{(q_j,k_j,y_j)\}_{j=1}^{n_k})，先用同一个衰减状态
(\tilde R=\alpha^{n_k}R_k) 计算所有 (e_{y,j})，再一次写入：

$$
R_{k+1}=\Pi_\rho\left(
 \alpha^{n_k}R_k+
 \sum_{j=1}^{n_k}\frac{\eta e_{y,j}}{1+\varepsilon}q_jk_j^\top
\right).
$$

因此同一批反馈的结果对输入列表置换不敏感；跨到达索引仍按真实到达顺序更新。

## 3. 可证明的性质

### 3.1 因果性

更新器在时刻 (k) 只读取 (B_k) 和 (R_k)，而 (R_k) 只由
(B_1,\ldots,B_{k-1}) 递推得到。因此第 (t) 次动作使用的状态不依赖
(\tau_j\ge t) 的未来标签。反馈的原始 (q_j,k_j) 必须在决策时快照，不能在
标签到达时重新编码，否则会把新模型信息泄漏到旧事件。

### 3.2 有界性与稳定性

投影的非扩张性给出

$$
\lVert R_{k+1}\rVert_F\le\rho.
$$

即使省去投影，由三角不等式也有

$$
\lVert R_{k+1}\rVert_F
\le\alpha\lVert R_k\rVert_F+\frac{\eta}{1+\varepsilon},
$$

所以当 (\alpha<1) 时稳态上界为

$$
\limsup_k\lVert R_k\rVert_F
\le\frac{\eta}{(1-\alpha)(1+\varepsilon)}.
$$

这只是状态稳定性，不是准确率定理；准确率仍需实验验证。

### 3.3 对重复同一事件的误差收缩

暂时令 (\alpha=1)、不触发投影，且连续收到相同的 ((q,k,y))。令
(r_n=q^\top R_n k)。单步更新满足

$$
r_{n+1}=r_n+\eta(y-s_0-r_n)\frac{\lVert q\rVert^2\lVert k\rVert^2}{1+\varepsilon}.
$$

归一化后，残差 (d_n=(y-s_0)-r_n) 满足

$$
d_{n+1}=\left(1-\frac{\eta}{1+\varepsilon}\right)d_n,
$$

因此 (0<\eta\le1) 时单调收缩。若 (\alpha<1)，旧残差还会以
近似 (\alpha(1-\eta/(1+\varepsilon))) 的因子衰减；这给出了适应速度和遗忘速度
之间的可调参数，而不是凭直觉选学习率。

### 3.4 旧能力的最坏扰动界

对任意旧任务的归一化 (q,k)，在线分数相对冻结先验的变化满足

$$
|s_k(q,k)-s_0(q,k)|=|q^\top R_k k|\le\lVert R_k\rVert_2\le\rho.
$$

若冻结先验在旧 holdout 上的分类 margin 至少为 (gamma)，且
(\rho<\gamma)，则线性阈值决策不会被残差翻转。若损失对分数是 (L)-Lipschitz，
旧 holdout 的损失增量至多为 (L\rho)。这不是“永不遗忘”的保证：若旧样本本身
没有 margin，必须直接测量 (F_{\mathrm{peak}})。

### 3.5 跨任务干扰界

一条新反馈 ((q',k',y')) 对旧输入 ((q,k)) 的单次分数改变至多为

$$
|\Delta s(q,k)|
\le \frac{\eta |e_y|}{1+\varepsilon}
 |q^\top q'|\,|k'^\top k|.
$$

这使“稳定地址”和“当前查询”可以被单独诊断：如果键或查询之间近似正交，
更新主要作用在相关任务；若两者都高度相似，任何快速更新器都会有干扰，必须
靠门控、版本隔离或更小的 (ho) 处理。

## 4. 复杂度与实时性可检验门槛

单条到达事件的更新复杂度为 (O(m^2))，状态占用为 (O(m^2))，与历史长度无关；
决策时每个候选的分数为 (O(m^2))（可缓存 (R_k k) 后降为 (O(m))）。这只给出
上界，不能替代硬件测量。进入 A800 实验前必须先在同一机器上检查：

1. 固定 (m,alpha,eta,ho) 和随机种子；
2. 对同一事件流比较当前 S/Z、对角 LS、RLS 和本更新器；
3. 同时报告未来窗口 reward、rank hit、校准误差、旧 holdout 遗忘、更新/决策
   p50/p95、状态字节数；
4. 只有在长稳态流上不劣于 S/Z、漂移后恢复时间明显改善且旧 holdout 遗忘低于
   预设阈值时，才值得提交一次真实数据队列任务。

## 5. 目前不能声称的内容

这个候选是一个有界的残差快权（fast-weight delta）更新器。外积残差写入、衰减
和投影分别在已有在线回归、快速权重或门控状态模型中出现；仅凭上述公式不能声称
“全新架构”。真正可成为贡献的部分，必须由同一 selected-only 延迟反馈协议下的
消融证明：稳定键/任务查询分离、到达批量更新、残差投影和低延迟更新的组合，是否
同时改善适应速度与旧能力保持。若基线已达到相同性能，方案应停止或改写问题，
不要为凑创新保留它。

