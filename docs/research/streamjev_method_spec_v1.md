# Stream-JEV v1: 可训练的实时评判模型方案

**日期：** 2026-09-24  
**状态：** Superseded by [`streamjev_method_spec_v2.md`](streamjev_method_spec_v2.md) for the current mainline. 保留本文件记录早期双快状态假设；它不是已经接受的论文方法。

## 要解决的问题

JEV 不是负责生成答案的大语言模型，而是一个在候选集合中作决定的小模型。每次决定时它只能看到任务、候选描述、已有合法历史和当前预算；真正执行的候选才会产生结果，反馈可能晚到，也可能只给出二值或软标签。模型必须在反馈到达后快速改变当前选择，同时保留旧任务上的能力。

两个项目共用同一个事件协议和更新器：

- peer 项目从 `select` 开始，候选是邻居 agent；
- tool 项目使用 `select`、`verify`、`final` 三种 typed decision，候选是工具或版本；
- 反馈只绑定已经执行的候选；未执行候选的结果和真值不能进入状态；
- 每个 selector 有独立的快状态，慢模型可以共享，除非实验显示两类标签可以安全合并。

## 争论后的取舍

### 全模型逐条反向传播

它的适应容量最大，但把大部分延迟、显存和不稳定性放在了线上关键路径；延迟标签和选择偏差还会把一次错误反馈传播到整个表示层。因此只作为压力测试，不作为上线方案。

### 冻结表示加 Beta/RLS

这是必须保留的第一强基线。它能逐条更新、可解释、易回滚，但它本身是已知的在线学习构造，不能单独作为论文创新。

### 仅仅把 Laya 的 `observe` 接进来

Laya/AnyJev 的周期性重拟合可作为基线，但它不是实时更新：反馈先积累，随后重新拟合历史数据。直接包装它不会回答“如何实时训练”。

### 采用的方案：学习型快状态 + 保守后验 + 慢速巩固

主模型不是把 Laya 改成一个更大的生成模型，而是把“反馈如何改变未来决定”建模成一个可训练的状态转移问题。它保留一个小的、可解释的后验通道，再增加一个经过流式元训练的低维快状态；慢模型只在异步 learner 中更新。

## 模型结构

### 1. 冻结或慢速更新的候选表示

用 Laya multilingual（约 322M）作为第一版语义编码器。对任务上下文和每个候选得到表示 `q_t`、`c_i`。菜单通过候选共享参数的 scorer 逐项打分，再做 masked softmax；候选顺序不能影响任一候选的分数。这个改动是必要的，因为原始菜单头不能作为动态候选集合的干净接口。

第一轮只缓存表示，不让编码器进入逐条更新。若小模型容量不足，再做参数高效的慢更新；不从头训练四亿参数模型。

### 2. 保守后验通道

每个候选维护带遗忘因子的 Beta 后验 `(alpha_i, beta_i)`。只有选中的候选在反馈到达时更新，更新权重是截断的 inverse propensity。后验提供三个作用：冷启动先验、可校准的不确定度、快状态失效时的安全退路。

### 3. 学习型快状态

维护一个全局 regime state `u_t` 和候选局部 state `v_i,t`，维度先固定为 32 或 64。反馈 `(q_t, c_i, y_t, delay_t, propensity_t)` 到达时，使用共享的 gated cell 更新：

```text
r_t = clip(IPS(y_t, propensity_t), -w_max, w_max)
z_t = sigmoid(W_z [q_t,c_i,u_t,v_i,t] + b_z)
u_{t+1} = (1-z_t) ⊙ u_t + z_t ⊙ tanh(A_u u_t + B_u φ_t)
v_{i,t+1} = (1-z_t) ⊙ v_i,t + z_t ⊙ tanh(A_v v_i,t + B_v φ_t)
```

`z_t` 有上限，`u/v` 有范数上限，所有矩阵维度很小。没有反馈时状态不自行“猜测”变化；延迟只在反馈到达时作用。候选离开菜单时保留有界的版本化状态，过期后按 TTL 清理。

### 4. 选择分数和门控

```text
base_i = scorer(q_t, c_i)
residual_i = head(q_t, c_i, u_t, v_i,t)
gamma_t = sigmoid(a · evidence_t + b · drift_t - k · uncertainty_t)
logit_i = base_i + gamma_t * residual_i + λ * logit(Beta_i)
```

`gamma` 在冷启动时接近零，证据和当前漂移都不足时退回 base + posterior。这样“实时”来自状态转移，而不是线上反向传播整个 encoder。

## 训练流程

### Stage 0：静态初始化

用合法的离线标签训练候选 scorer，保留原始 Laya head 作为静态基线。训练输入只包括动作前可见信息；把菜单随机打乱，测试 permutation invariance。这个阶段只回答“表示和候选打分是否可用”。

### Stage 1：流式元训练

把真实 replay 事件切成短 stream episode。每条 episode 明确候选到达/移除、反馈延迟、漂移、探索率和标签噪声。训练 gated cell、后验先验和门控，使模型在收到前几条反馈后对**下一条**决定更好，而不是只拟合当前标签。

训练目标由四部分组成：

```text
L = prequential loss/regret
  + ρ_old * old-regime loss
  + ρ_anchor * KL(p_adapt || p_base)
  + ρ_cost * update_compute
```

logged policy 的选择偏差用 IPS 或 doubly robust 估计；没有 propensity 支持的样本不用于强结论。反向传播只在长度为 K 的短 unroll 上进行，K 从 8/16 开始，避免把整个历史展开。

### Stage 2：异步慢速巩固

线上 actor 只执行编码缓存、候选打分、快状态更新和事件写入。learner 从“最近窗口 + reservoir”采样，周期性更新 scorer、cell 初始化或轻量 adapter。新 checkpoint 必须同时通过新 regime 和旧 regime holdout、校准和延迟检查，随后原子发布；失败就回滚到上一版。

### Stage 3：真实服务

部署四个边界：`Actor`、`FeedbackArbiter`、`Learner`、`SnapshotStore`。arbiter 校验事件版本、反馈延迟和 selected-only 约束；learner 不能访问真值文件或未执行候选的输出。actor 只在安全点切换 checkpoint，每个 selector 的快状态单独持久化。

RLinf 只复用 Channel、replay、worker placement 和 checkpoint 机制；先用 PyTorch + 小型 Ray 边界把算法跑通，再接 RLinf。ROLL 的生成式多角色训练路径不作为第一版强依赖。

## 评估与否决规则

必须同信息、同探索率、同预算比较：

1. random/epsilon 与固定静态 scorer；
2. 静态 scorer + Beta；
3. 静态 scorer + RLS/LinUCB；
4. AnyJev/Laya 周期性重拟合；
5. 只有 gated fast state；
6. 完整方案（后验 + fast state + 慢巩固）。

每条 stream 报告 prequential regret/NLL、选中正确率、Brier/ECE、漂移后的恢复步数、旧 regime 性能变化、反馈到达后的更新 p50/p95、决策 p50/p95、内存和 checkpoint 回滚次数。工具项目还要报告 verify/final 的成本；peer 项目还要报告后续责任变化和返工成本。

出现以下任一情况就砍掉对应复杂度：

- 完整方案不稳定超过 RLS/Beta，或优势只在有泄漏的 full-information 标签上出现；
- fast state 的提升伴随旧 regime 显著退化，reservoir/anchor 无法恢复；
- 更新 p95 超过业务决策间隔；
- IPS/DR 在独立探索切片上失效；
- 同一事件协议不能同时容纳 peer 和 tool 的 typed decision；
- 后续 assignment 或 team utility 没有改变，只有内部分数改变。

## 当前可执行实验顺序

1. 本地协议与快状态测试（已通过 4/4）；
2. 用合成 stream 验证漂移、延迟、噪声和稳定性曲线；
3. 接入已通过回放测试的真实 selected-only 事件，先做 replay-only 对比，不宣称独立测试集；
4. 在 A800 上测 Laya 表示缓存、短 unroll learner 和 actor/learner p95；
5. 只有数据资格和 propensity 支持明确后，才做正式小批量科学实验。

这套方案的科学风险不是“代码能否跑”，而是它是否相对同信息的 Beta/RLS 基线带来可重复的**更快适应且更少遗忘**。如果不能，论文方法就应收缩为一个工程化在线选择器，而不是继续堆模块。
