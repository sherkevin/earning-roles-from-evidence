# 从 vault 的 Loop Attention 与 KV Cache 笔记得到的启发

阅读来源：

- /Users/jingwu/work/vault/loop attention.md
- /Users/jingwu/work/vault/kv cache.md
- /Users/jingwu/work/vault/Linear Attention.md
- /Users/jingwu/work/vault/01-Methods/inference-kv-cache-management.md

这条支线不是主线方法，而是用来解释当前 associative 失败后，哪些结构原则值得迁移。

## 1. Loop 解决计算深度，不自动解决在线记忆

vault 笔记把 loop 定义为共享参数的重复计算：

$$
h^{(r+1)}=F_\theta(h^{(r)}).
$$

它首先是 compute allocation / parameter sharing architecture，不是 memory architecture。
对我们的任务，不能把“固定大小的递推状态”直接称作“实时训练”。如果没有可学习的
key/query 表示和监督目标，loop 或 linear recurrence 只是在更快地重排已有计算。

可迁移原则是：

$$
\text{representation learning}
\quad\perp\quad
\text{online state update}
\quad\perp\quad
\text{decision policy}.
$$

三者必须分别验证，不能用更新速度替代预测效果。

## 2. 当前实现把 Q、K、V 压成了一个对象

vault 笔记对 attention 的功能分工很清楚：

- Q 决定当前要找什么；
- K 是稳定的地址；
- V 是被读出的内容。

当前 associative 实现中，当前候选和历史样本都使用同一个 \(\phi(x)\)，标签 y 是
一个标量 value，状态还是全局共享的 S/Z。它没有显式的：

$$
\text{stable peer/version key}
\quad\longrightarrow\quad
\text{mutable quality/value state}.
$$

因此它无法表达“这个 peer 长期可靠，但这次任务不适合”或“这个版本近期退化，
但历史能力仍然保留”。所有 peer 的证据都被放进同一个全局核平均。

更合理的候选接口应拆成：

$$
K_i=\operatorname{KeyEncode}(\text{peer}_i,\text{version}_i),
$$

$$
q_t=\operatorname{QueryEncode}(\text{task}_t,\text{stage}_t),
$$

$$
V_i^{(t)}=\text{peer i 的可变质量、角色和近期残差状态}.
$$

当前任务只生成一次性的 \(q_t\)；稳定的 \(K_i\) 和带版本的 \(V_i\) 才进入长期状态。

## 3. 冻结或慢更新 KV 对应“稳定身份 + 快速质量更新”

vault 里最有用的结构假设是：

$$
K^0,V^0=\operatorname{Encode}(H^0),
$$

之后重复更新 query：

$$
q^{(r)}\rightarrow \operatorname{Attn}(q^{(r)},K^0,V^0)
 \rightarrow q^{(r+1)}.
$$

对我们的 selector，这启发出两个时间尺度：

1. 慢时间尺度：离线训练或低频更新 peer/version 的 key 表示；
2. 快时间尺度：每条 selected-only 反馈只更新小的 value/residual 状态。

这比每条反馈都重新改变完整 encoder 更符合实时性，也能避免旧任务的表示被新标签
覆盖。它仍然需要通过实验验证，不能直接当作最终架构。

## 4. Gated DeltaNet 暗示：实时更新需要 erase，而不只是 decay + write

vault 的 Gated DeltaNet 推导把更新拆成：

$$
\text{Decay}-\text{Erase}+\text{Write}.
$$

其核心是用当前 key 上的新目标减去旧预测：

$$
\text{residual}=v_t-S_{t-1}k_t,
$$

再沿 \(k_t\) 的方向擦除旧关联并写入残差。当前实现只有整体衰减和累加，没有
针对错误关联的 residual erase。延迟反馈到来时，如果旧 regime 的证据已经写入，
简单累加只能慢慢稀释，不能沿对应地址主动修正。

可借鉴的候选方向是 gated fast-weight memory：

$$
M_{t+1}
=\alpha_t M_t(I-\beta_t k_tk_t^\top)
+\beta_t v_tk_t^\top,
$$

其中 \(\alpha_t\) 控制整体保留，\(\beta_t\) 控制本次写入/擦除强度，\(k_t\)
是 peer/task 地址，\(v_t\) 是反馈残差。创新空间在 selected-only 延迟反馈、
版本因果和低成本门控如何组合，而不是重新声称 linear attention 本身是创新。

## 5. KV cache 的可迁移原则：版本、生命周期和可组合性

vault 的 KV cache 笔记强调，缓存正确的前提是 causal history 不变、prefix 不被改写。
这对应我们需要的三条工程不变量：

1. 决策事件保存当时的 key/version/feature snapshot；
2. 迟到反馈只能生成新状态版本，不能改写已经做出的历史决策；
3. 一个 peer 的长期状态必须能在不同 task context 中复用，不能把当前 context
   的临时信息永久写进 peer identity。

当前 \(x=[1,\text{context},\text{candidate}]\) 同时承担身份和任务上下文，正是
不可组合的根源之一。要复用 peer memory，应至少把稳定 peer key 与任务 query 分开。

KV cache 的生命周期也可以迁移到 peer memory：

$$
\text{active local peers}
\rightarrow
\text{warm peer states}
\rightarrow
\text{compressed long-term evidence}
\rightarrow
\text{evicted but replayable history}.
$$

这与用户提出的无向局部 peer 图相容：决策时只加载邻域内的 peer block，必要时探索
新邻居，低频 peer 状态可以压缩或换出。它是内存系统设计，不应和 reward estimator
的表达能力混在同一个公式里。

## 6. 不同 memory source 不要直接共享一个竞争空间

vault 笔记指出，base context 和 retrieved memory 直接进入同一个 softmax，会因为
共享分母互相稀释。对我们的 selector，至少有三类来源：

- 全局 prior：所有 peer 的基础可靠性；
- local peer memory：当前 agent 邻域的历史交付证据；
- exploration memory：尚未充分验证的新 peer 或新版本。

更自然的结构是先在 source 内部读，再做 source-level gate：

$$
o_{\mathrm{prior}}=\operatorname{Read}(q,M_{\mathrm{prior}}),
$$

$$
o_{\mathrm{local}}=\operatorname{Read}(q,M_{\mathrm{local}}),
$$

$$
o_{\mathrm{explore}}=\operatorname{Read}(q,M_{\mathrm{explore}}),
$$

$$
\hat y=
g_{\mathrm{prior}}o_{\mathrm{prior}}
+g_{\mathrm{local}}o_{\mathrm{local}}
+g_{\mathrm{explore}}o_{\mathrm{explore}}.
$$

这样“是否相信邻居”和“邻居内部选哪个 peer”是两个决策，避免一个全局
S/Z 把不同生命周期的证据平均掉。

## 7. 对当前方案的直接改写建议

从这些笔记能直接推出的不是“把 KV cache 接进来”，而是四个可检验的结构假设：

1. 地址/内容分离：peer/version key 稳定，反馈只更新 value/residual；
2. 残差写入：用新反馈相对旧预测的 residual 做 erase + write；
3. 分层状态：global prior、local peer state、exploration state 分开维护；
4. 版本化生命周期：feedback watermark、source time、arrival time 和状态版本显式记录。

先不要同时实现四个假设。最小实验顺序应是：

$$
\text{固定 theta、长 horizon}
\rightarrow
\text{key/value 分离}
\rightarrow
\text{residual erase}
\rightarrow
\text{regime switch + delayed feedback}
\rightarrow
\text{真实 benchmark}.
$$

## 边界

这些笔记支持的是架构假设和工程不变量，不是我们方法在真实 peer/tool benchmark 上
已经有效的证据。尤其是 Gated DeltaNet、KV cache 和 loop attention 的原始目标分别是
序列建模、推理缓存和计算深度；迁移到 selected-only peer selection 仍必须经过独立
的可识别性和真实数据实验。
