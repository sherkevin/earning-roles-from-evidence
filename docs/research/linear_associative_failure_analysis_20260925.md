# 线性 associative 更新器为什么没有带来选择收益

日期：2026-09-25

这份分析解释 linear_associative_smoke_20260925 的失败原因。实验用五个相同
的 synthetic selected-only delayed-feedback world 比较 static、OnlineRLSHead、
no-feedback 和 associative。完整配置、逐事件日志和结果见
references/aamas/streamjev_20260924/experiments/logs/linear_associative_smoke_20260925_*。

## 先给结论

这次结果不是“更新太慢”或“实现有 bug”。结果说明：

1. S/Z 的递推确实可执行，和显式指数衰减求和一致；
2. 当前方法不是一个会学习表示或参数的训练框架，而是一个固定特征核的在线核回归器；
3. 这个固定核在本次非平稳短流中没有充分表达和利用 signed linear reward，且菜单内约 65% 的核质量来自所有候选共享的 bias/context；
4. 在温度为 1 的 softmax 下，四个候选的分数几乎相同，策略接近 uniform，反馈没有转化为有效的选择差异；
5. regime 切换、延迟、只有约 100 条 selected-only 标签和较短 horizon 进一步降低了可识别性；
6. 线性注意力的结合律只解决固定状态的计算复杂度，不能自动提供表达能力、抗遗忘或准确率。

## 1. 代数层：正确，但只证明了“能算”

associative 更新为

$$
S_k=\lambda^{k-k^-}S_{k^-}+\sum_{r:\tau_r=k}w_r y_r\phi(x_r),
\qquad
Z_k=\lambda^{k-k^-}Z_{k^-}+\sum_{r:\tau_r=k}w_r\phi(x_r).
$$

查询为

$$
\hat y_k(q)=
\frac{\phi(q)^\top S_k}
     {\phi(q)^\top Z_k+\varepsilon}.
$$

例如，x_r 是一次被选候选的 7 维缓存特征，y_r 是其到达的 0/1 标签，
q 是当前菜单中另一个候选的同类特征，S 和 Z 是内存中的两个 14 维向量。

这等价于

$$
\hat y_k(q)=
\frac{\sum_r \lambda^{k-\tau_r}w_r K(q,x_r)y_r}
     {\sum_r \lambda^{k-\tau_r}w_rK(q,x_r)},
\qquad
K(q,x)=\phi(q)^\top\phi(x).
$$

也就是固定核的 Nadaraya–Watson 平滑器。S/Z 只是它的充分统计量，并没有
学习新的参数、特征权重或交互项。实验中 5/5 个 seed 与显式衰减和一致，
同一 arrival batch 逆序后的状态差异小于 \(10^{-13}\)。所以递推正确性已经
通过；失败发生在统计模型层。

## 2. 表示层：固定核与环境的真实关系不匹配

环境的标签由

$$
y\sim\operatorname{Bernoulli}\left(\sigma(\theta^\top x)\right)
$$

产生。这里 x=[1, context, candidate_vector]，theta 是每个 regime 的带符号
线性参数。RLS 保存

$$
A=\lambda A_{\mathrm{old}}+wxx^\top,\qquad
b=\lambda b_{\mathrm{old}}+wyx,\qquad
\hat\theta=A^{-1}b,
$$

所以它能从 selected-only 样本恢复一个全局的带符号线性方向，并通过 xx^T
保留坐标之间的关系。

当前 associative 使用

$$
\phi(x)=[\max(x,0),\max(-x,0)].
$$

因此

$$
K(q,x)=\sum_i\max(q_i x_i,0).
$$

这个核只奖励同坐标、同符号的重叠；它没有 RLS 的协方差，也没有二阶或跨坐标
交互。对一个真实关系为 sigmoid(theta @ x) 的环境，它不能稳定地外推一个
全局 signed direction，只能从历史样本中找相似向量做局部平均。

这不是把特征维度加倍就能自动解决的问题。加倍只是把正负坐标分别存储；
S/Z 仍然只做一个标量 kernel average。

还有一个更具体的统计量错配。若目标是拟合环境里的线性 reward，平方损失的
加权岭回归应维护

$$
A_k=\lambda A_{k^-}+\sum_r w_r\phi(x_r)\phi(x_r)^\top,
\qquad
b_k=\lambda b_{k^-}+\sum_r w_r y_r\phi(x_r),
\qquad
\hat w_k=A_k^{-1}b_k.
$$

当前的 S 相当于 b，但 Z 是 \(\sum_r w_r\phi(x_r)\)，不是
\(\sum_r w_r\phi(x_r)\phi(x_r)^\top\)。因此它不是 RLS 的低成本近似，而是
attention 的归一化核回归。即使只保留对角近似，也应使用

$$
D_k=\lambda D_{k^-}+\sum_r w_r(\phi(x_r)\odot\phi(x_r)),
\qquad
\hat w_{k,i}=\frac{b_{k,i}}{D_{k,i}+\rho},
\qquad
\hat y(q)=\phi(q)^\top\hat w_k.
$$

这个对角形式仍然不是最终方案，但它是一个可证伪的最小对照：如果它在固定
theta、长 horizon 的 world 上恢复了排序能力，说明当前失败的一个直接原因是
分母统计量选错；如果它仍接近 uniform，再继续查 feature map 和共享 context。

## 3. 菜单结构：候选区分信号被公共项淹没

同一个菜单中的候选共享当前任务上下文，因此

$$
x_i=(1,c,v_i),
$$

其中 1 是所有候选相同的 bias，c 是所有候选相同的 context，v_i 才是
候选差异。于是同一菜单内两个候选的核包含

$$
K(x_i,x_j)=1+K(c,c)+K(v_i,v_j).
$$

在这次运行中，共享 bias/context 贡献了约 65% 的对角核质量；非对角核与对角核
的比值约为 0.75–0.86。候选之间的核很接近，查询分数自然被拉向全局标签均值。

诊断回放显示：

- oracle 最优候选的平均期望奖励：0.537092；
- uniform 菜单平均期望奖励：0.412845；
- associative 策略平均期望奖励：0.413246；
- oracle 相对 uniform 仍有约 0.124247 的可学习空间；
- associative 分数平均跨度只有 0.029898；
- 四选一 uniform 熵为 log(4)=1.386294，associative 熵为 1.386185。

因此当前方法的具体失败形态是“无法把候选拉开”，不是“把候选拉开后排序错了”。

## 4. 决策层：分数有一点信号，但策略没有利用它

associative 的不确定度项是

$$
u(q)=\frac{1}{\sqrt{1+\phi(q)^\top Z}}.
$$

它只反映核质量，不反映哪个候选最值得探索。菜单内候选的核质量也很相近，
所以不确定度 bonus 几乎相同。再经过温度为 1 的 softmax，微小分数差异被进一步
压平，行为策略基本保持均匀。

这形成了一个反馈闭环：

$$
\text{候选分数接近}
\rightarrow
\text{选择近似均匀}
\rightarrow
\text{每个候选只得到稀疏标签}
\rightarrow
\text{固定核继续估计全局均值}.
$$

状态范数达到 86–166 也不代表模型学到了能力；S 和 Z 同时累加，查询时
取比值，公共规模会抵消。

## 5. 动态和数据层：短反馈流放大了表示缺陷

这次 horizon 只有 100，每步只有一个 selected-only 标签，反馈延迟为 1–8，
并且 regime 会重新采样完全不同的 theta。lambda=0.985 的有效记忆长度
约为 1/(1-0.985)=66.7 步，半衰期约 46 步；而切换后的评估窗口只有
13–25 步。

因此一个 regime 切换后，S/Z 仍混有大量旧 regime 标签，新 regime 能提供的
反馈又很少。这个问题同时影响 RLS：RLS 也只有约 +0.007444 的 paired reward
增益，说明这轮数据本身不是高功效设置。但 oracle headroom 仍然存在，说明任务
并非没有可学习信号；当前实验只是把“表示失配”和“数据不足”叠加在了一起。

延迟还有一个次要问题：标签在 arrival time 被加入并获得当前权重，而不是在其
decision/source time 进入状态。这个实现满足因果性，但旧标签到达时可能被当成
当前信息；需要在后续 watermark/source-time ablation 中单独测量。

## 6. 哪些解释已经排除

- 不是递推实现错误：闭式和、批内顺序、重复反馈检查均通过。
- 不是完全没有 oracle headroom：oracle 与 uniform 之间约有 0.124 的平均差距。
- 不是单纯“模型太小”：RLS 使用相同输入和反馈，在相同短流上已有小幅收益。
- 不是只要调一个温度就能解决：温度最多放大已有分数，不能补回被核抹掉的
  signed direction 和候选交互。

## 6.1 新的固定 theta 隔离实验改变了结论边界

随后运行了固定单一 theta、2000 步、一步 selected-only 延迟的隔离实验，并让
所有方法使用同一种 epsilon-greedy 策略。结果为：

| method | expected reward | regret | prediction MSE | rank hit |
|---|---:|---:|---:|---:|
| static | 0.368636 | 0.110405 | 0.074983 | 0.250000 |
| associative | 0.450058 | 0.028983 | 0.037748 | 0.647475 |
| diagonal LS | 0.402190 | 0.076851 | 0.126985 | 0.413075 |
| OnlineRLSHead | 0.457843 | 0.021197 | 0.081980 | 0.794025 |

这说明当前 associative kernel 不是完全不能学习：在 stationary、长 horizon 和
可利用的策略下，它明显超过 static；但它仍弱于 RLS，排序命中率也明显更低。
因此原来的失败不能简单归结为“kernel 没有表达能力”，更准确的说法是：

$$
\text{固定核的弱表达能力}
+\text{短流非平稳污染}
+\text{温度 1 的策略压平}
$$

共同导致了上一轮结果接近 uniform。固定 theta 实验还说明，估计器和策略必须分开
评估：associative 在可控策略下有排序信号，但上一轮 softmax 没有把信号转成动作。

随后在同一个 stationary world 上只替换行为策略，保持 associative estimator、反馈
延迟和随机种子不变：

| policy | expected reward | regret | rank hit | entropy |
|---|---:|---:|---:|---:|
| temperature-1 softmax | 0.369360 | 0.109680 | 0.743525 | 1.386260 |
| epsilon-greedy, epsilon=0.1 | 0.450058 | 0.028983 | 0.647475 | 0.349516 |

这说明上一轮的主要决策损失确实来自 calibration：softmax 的 rank hit 并不低，
但熵几乎等于 \(\log 4\)，没有把排序转成集中选择。epsilon-greedy 的 rank hit
反而略低，却因为真正利用了当前最高分而取得更高 reward。因此 estimator quality、
 policy calibration 和 exploration coverage 必须作为三个独立指标报告。

## 6.2 删除 context 不是直接修复

在同一个 stationary world 上把长期特征从 [1, context, candidate_vector] 改成
candidate_vector-only，并保持 epsilon-greedy、反馈和种子不变：

| feature mode | expected reward | regret | rank hit |
|---|---:|---:|---:|
| full | 0.450058 | 0.028983 | 0.647475 |
| candidate-only | 0.448583 | 0.030457 | 0.608125 |

因此“共享 context 稀释候选差异”是真实机制，但“删除 context 就能恢复效果”没有
得到支持。context 同时承担按任务检索历史证据的作用。正确的方向是让 context
进入当前 query，让 peer/version identity 进入稳定 key，而不是把 context 从所有
表示中粗暴删除。

## 7. 改进顺序

第一步的固定 theta 隔离已经完成。它保留当前 kernel 作为可用 baseline，但确认
需要同时报告 estimator 的 MSE、排序命中率和 policy 的 expected reward，不能只看
一个 aggregate reward。

第二步做表示和统计量消融：保留 context 作为当前 query，加入候选身份/版本作为
稳定 key，同时对比当前一次矩归一化、对角二阶统计量和 RLS 的协方差状态。继续
比较 signed kernel、二阶低秩特征和一个冻结的小型 learned key/query encoder。
必须保留 selected-only 约束，不能偷偷使用未选候选标签。

第三步才恢复 regime switch 和延迟，比较 source-time 与 arrival-time 衰减、不同
半衰期和 watermark replay。这样才能区分“表示能力不足”和“实时抗遗忘不足”。

最后再上真实 benchmark/A800，测端到端 p95；当前 66 微秒只是本地 Python
状态操作，不包含 encoder、队列、序列化和 LLM 调用。

## 最终判断

这次实验支持的是一个很窄的结论：固定核状态可以快速、因果、可重放地更新。
它没有支持“线性注意力式递推就是实时训练方法”。真正需要创新的地方仍然是：

$$
\text{如何在 selected-only 延迟反馈下，在线学习一个能表达任务/候选交互、又能保持固定更新成本和旧知识约束的 key/query/value 状态。}
$$
