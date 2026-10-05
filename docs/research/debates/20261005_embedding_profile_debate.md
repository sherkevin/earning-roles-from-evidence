# Debate — Can peer judgments become embedding-based Agent profiles?

- **日期**：2026-10-05
- **阶段**：M — method/story lock
- **状态**：`OPEN / candidate comparison`
- **goal_change_requested**：false

## 1. 问题

候选想法是：接收者 A 对发送者 B 的评价成为 B 的能力证据；聚合 B 的多条证据形成
文字画像；分别对当前任务和 B 的画像做 embedding，再按相似度选择 Agent。这个想法
可实现，但必须区分“语义相似”与“在当前责任条件下能交付并被采用”。

## 2. 公开先例与边界

- [FlyRoute](https://arxiv.org/abs/2605.22057) 已提出 success store、质量门、周期性
  capability distillation、BM25 检索和 profile-aware exploration；它的质量门由
  LLM-as-Judge 给出，gold route 只用于评估。因而“成功案例→Agent 画像→任务路由”不是
  足够的独立创新。
- [AgentNet](https://proceedings.neurips.cc/paper_files/paper/2025/file/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html)
  已使用任务 capability vector、Agent capability vector 和相似度进行动态分配，并用
  任务表现更新能力向量；它没有我们的 situated recipient judgment、assignment-before-
  selection 和 delayed responsibility lineage 合同。
- [DyTopo](https://arxiv.org/abs/2602.06039) 已用固定语义 encoder 对 Agent 的 need/key
  描述做余弦匹配，动态改变局部通信图；它回答的是消息依赖匹配，不是有归因标签的交付
  质量学习。

因此 embedding/profile 可以作为实现部件或强 baseline；我们的可识别差异必须来自
“谁评价谁、评价何时可见、责任如何绑定、未来使用结果如何延迟修正”，并由消融证明。

## 3. 三个候选方向

### A. 文本画像匹配（最接近用户原方案）

对每个 Agent 保留 seed profile、成功案例和周期性生成的 learned profile；用 frozen
encoder 计算 `sim(task, profile)`，按相似度选人。

- **标签**：通过责任门的 recipient judgment；后续 outcome 只作为独立校准/更新信号。
- **优点**：实现最快，可解释，容易做 cold-start 和人工检查。
- **风险**：LLM 画像会丢失 task condition、版本和反例；语义相似不保证交付可用；容易
  把接收者偏见或某个 Agent 的风格写成能力；周期性蒸馏也不是真正逐条实时训练。
- **定位**：必须作为 profile/BM25/embedding baseline 或 ablation，不能直接作为论文创新。

### B. 条件化证据原型（当前最适合先验证）

不把评价压成一段自由文本，而是把每条 edge-local evidence 保留为带任务/角色条件的
经验卡；对新任务检索相似卡，按相似度、recency、judge reliability 和 candidate version
加权聚合。文字画像只做可选解释输出。

对候选 `c`：

$$
q_J(c|x)=\frac{\alpha_0+\sum_{e:c_e=c}w_e y^J_e}
{\alpha_0+\beta_0+\sum_{e:c_e=c}w_e},
\qquad
q_L(c|x)=\operatorname{weighted\_mean}(y^L_e),
$$

其中 `y^J` 是接收者对源交付的 judgment，`y^L` 是未来 assignment/use 的 later
outcome；二者不能互相覆盖。选择器可用 `q_J` 作早期信号、用 `q_L` 作延迟校准，并
报告两者的独立贡献。

- **优点**：保留责任、时间和反例；不需要生成 hallucinated profile；天然支持 few-shot
  检索和 append-only 记忆。
- **风险**：需要严格的任务表示和跨 root split；相似度本身仍可能学到表面词汇。
- **定位**：优先实现的候选；先做 CPU no-leakage 和 matched retrieval 对比。

推荐把 B 实现成“每个 Agent 多个条件化原型”，而不是一个全局平均向量。对高质量
交付维护正原型 `\mu^+_{B,k}`，对低质量交付维护负原型 `\mu^-_{B,k}`；原型按任务/角色
条件聚类，数量上限 `K_B`，用加权在线均值更新。当前任务向量 `z_t` 的匹配分数可写成：

$$
s_B(x_t)=\max_k\cos(z_t,\mu^+_{B,k})-
\lambda_-\max_k\cos(z_t,\mu^-_{B,k}),
$$

再用有效支持量收缩到中性先验。这样同一个 Agent 可以同时保留“擅长队列调试”和
“不擅长 API 迁移”等不同能力，而不会被一段自由文本抹平。文字画像可以由这些原型
异步生成，作为解释视图；它不作为唯一训练状态。

### C. 学习任务—Agent compatibility head

将 `(task, candidate, public history)` 编成 `φ(x,c)`，用有效 edge/later labels 训练一个
小型 compatibility head，例如 logistic/low-rank scorer；保留 prototype memory 作为
few-shot support 和 OOD fallback。

- **标签**：selected-only、通过责任门的 `y^J`/`y^L`；没有被选中的候选不能默认当负例，
  需要 propensity-weighted loss 或固定探索样本。
- **优点**：可以学习“任务需求与 Agent 能力的互补关系”，不依赖文字画像的可读性。
- **风险**：样本效率、选择偏差、遗忘和 encoder 训练成本更高；没有足够独立 root 时
  容易把 Agent 身份记住而非学习泛化。
- **定位**：在 B 的检索 baseline 有清晰瓶颈后再训练；不提前锁定 backbone。

## 4. 标签到底是什么

一条合格标签不是“B 做过这个任务”，而是：

```text
(task/role context, selected B@version, B delivery, receiver A judgment,
 receiver action, adoption/terminal outcome, cost, lineage, arrival time)
```

`A → B` 的分数只能评价这一次交付在这个上下文中的质量；它不能直接变成 B 的全局
能力标签。聚合时至少保留 `judge_id`、role、版本、任务条件和时间，必要时按 judge
reliability 校准。未选择的候选没有反事实标签，必须保留 UNKNOWN/未观测状态。

若进入 C 的 compatibility head，最小可行的在线目标是对**被选中且通过责任门**的
记录做 propensity-clipped 加权损失：

$$
\mathcal L_t(\theta)=
\min\!\left(w_{\max},\frac{1}{p_t(a_t)}\right)
\operatorname{BCE}\!\left(\sigma(\theta^\top\phi_t(a_t)),y_t\right)
 +\lambda\|\theta-\theta_0\|_2^2.
$$

`y_t` 必须明确是 `y^J`（接收者对源交付的判断）还是 `y^L`（未来使用结果）；二者
先分开训练/评估，不能无说明地混成一个标签。探索概率和 propensity 是获得可识别
标签的必要条件，未被选择的候选不自动构造负例。

## 5. 最小判别实验

先不调用真实 API，构造严格的时间切分回放：

1. `uniform/no-memory`；
2. 文字 profile + embedding（A）；
3. weighted kNN evidence memory（B）；
4. `contextual_trust_linear`；
5. B + 小型 compatibility head（C）。

按 structural root 做 leave-one-root-out、0/1/K-shot 和 candidate-version shift。主指标是
assignment-level future utility/regret、later adoption/terminal quality、完整成本、
检索/更新 p50/p95、UNKNOWN 和旧 root forgetting。任何使用未来 evidence、把未选择候选
当负例或随机行切分的结果都不具备判别力。

## 6. 暂定结论

用户提出的 profile embedding 路线**能做**，但作为单独算法不足以支撑创新。当前最稳妥
的实现顺序是先做 B，保留 A 作为强 baseline；只有 B 在跨任务上暴露出表示/泛化瓶颈，
才进入 C。真正可争取的论文贡献是：在链式交接中，用可归因的 peer judgment 形成条件化
经验，经过严格 read-cut 和 delayed selected-only credit，实时改变未来角色选择，同时
比较它是否超过静态画像、普通 kNN、RLS 和现成 profile routing。

该结论还不是正式方法锁定。正式锁定前必须通过 profile permutation、task-only embedding、
历史先验和 direct-feature controls；并按 task family 与 agent 做 group split。若 profile
匹配只在同分布随机切分有效，或 profile permutation 仍然有效，则只能报告描述性关联，
不能声称学到了 Agent 的任务能力。
