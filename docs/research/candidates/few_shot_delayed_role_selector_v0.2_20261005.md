# Candidate method v0.2 — Snapshot-separated profile, evidence delta, delayed residual

- **状态**：`CANDIDATE / NOT_ACTIVE / GATE_REQUIRED`
- **前一候选**：[`v0.1`](few_shot_delayed_role_selector_v0.1_20261005.md)
- **修订原因**：v0.1 的三层融合可能重复使用同一批 evidence，且未定义未来标签和快照边界。

## 1. 核心思想

把 Agent 选择拆成三个不同时间尺度，但不让同一条证据重复进入多个学习器：

```text
旧 evidence → profile snapshot P_k
snapshot 之后的新 peer judgment y^J → evidence delta D_(k,t)
future assignment/use 完成后的 later outcome y^L → residual head θ
```

文字画像是冷启动先验，evidence delta 是 few-shot 快速修正，residual head 是跨任务的
长期校准。三者都保留来源 ID、read cut、版本和 digest。

## 2. 选择时可见的最小实例

| 对象 | 输入来源 | 例子 |
|---|---|---|
| `x_t` | 当前任务的公开文本/结构 | `修复 queue.py 的优先级顺序` |
| `c` | 当前局部候选菜单 | `agent-b@v1` |
| `P_k(c)` | 截止到 `profile_cut=k` 的 B 能力画像 | `B 擅长队列并发，证据数 5` |
| `D_(k,t)(c)` | `k` 之后已发布的 edge-local judgment 卡 | `B 在两个相似队列任务上得分 .9/.2` |
| `y^L` | 已完成 future assignment/use 的结果 | `后续测试通过率 .8` |

当前选择不能读取 `t` 之后的 judgment、later outcome 或 private scorer。

## 3. 打分

设 `E_ν` 是冻结且版本化的任务/画像 encoder：

$$
s_P(c)=\operatorname{cos}(E_\nu(x_t),E_\nu(P_k(c))).
$$

对 delta 中的正/负原型分别计算：

$$
s_D(c)=\max_j\operatorname{cos}(z_t,\mu^+_{c,j})
-\lambda_-\max_j\operatorname{cos}(z_t,\mu^-_{c,j}),
$$

其中原型只由 `profile_cut` 之后的新 `y^J` 产生，且每条记录的权重为：

$$
w_e=\min(w_{\max},1/p_e)\cdot r_{judge(e)}\cdot d(\Delta t_e).
$$

`p_e` 是当时选择该 Agent 的 propensity，`r_judge` 是预注册的评价者可靠性，`d` 是
时间衰减。未被选择的候选不构造负例。

残差 head 只在 later outcome 已到达后学习：

$$
r_\theta(c)=\theta^\top h(x_t,c,s_P(c),s_D(c)).
$$

最终 utility 为：

$$
u_t(c)=b_t(c)+a_Ps_P(c)+a_Dg_t(c)s_D(c)+r_\theta(c)
-\lambda\operatorname{cost}_t(c)+\xi_t(c),
$$

$$
g_t(c)=\frac{n_{\mathrm{eff}}(c)}{n_{\mathrm{eff}}(c)+\kappa}.
$$

权重 `a_P,a_D,κ,λ` 只在 development split 选择，并在 confirmation 前封存。

## 4. 标签和更新

### 4.1 `y^J`：源交接判断

接收者对发送者交付的评分，只能在 producer/recipient/action/outcome lineage 通过责任门后
进入 `D_(k,t)`。它不更新 `θ`，也不能把 recipient 自有修改变成 producer 负例。

### 4.2 `y^L`：延迟未来结果

只有 target assignment 在 selection/start 前封存，且后续实际使用完成后，才生成 `y^L`。
它读取当时封存的 `P_k + D_(k,t)`，对 residual head 做一次 selected-only 更新：

$$
\delta_t=\operatorname{clip}\left(y^L_t-
\sigma(s_P+g_ts_D+r_\theta),-\delta_{\max},\delta_{\max}\right),
$$

$$
\theta_{t+1}=(1-\eta\lambda_\theta)\theta_t
+\eta\,\min(w_{\max},1/p_t)\,\delta_t h_t.
$$

参数有 ridge anchor、范数上限和旧任务 reservoir replay；若 `y^L` 为 UNKNOWN，则
`θ` 不变。这个更新本身仍需和普通 RLS/online SGD 比较，不能预先称为新算法。

## 5. 为什么比 v0.1 可识别

- profile 和 delta 使用不同的时间区间，避免一条 evidence 被算两次；
- `y^J` 与 `y^L` 分开，分别回答“交付是否被接收”和“未来使用是否成功”；
- profile refresh 有版本和 digest，画像生成不在实时选择关键路径；
- residual head 的输入快照固定，不能用更新后的 profile 解释旧结果；
- propensity、judge reliability 和 UNKNOWN 写入训练记录，便于审计选择偏差。

## 6. 仍未通过的创新门

该结构的“profile + prototypes + small head”仍可能被审稿人视为组合。只有当预注册的
delayed responsibility transfer 在未见 task family 上超过 profile-only、prototype-only、
RLS/SGD、weighted-kNN 和 no-memory，并且 permutation/泄漏 controls 退化，才有资格把
它写成方法贡献。当前不锁定 backbone、encoder、更新器或最终论文 claim。

## 7. 最小验证顺序

1. CPU 零 API：验证 snapshot separation、propensity、UNKNOWN/no-op、profile refresh 和
   replay digest；
2. synthetic temporal replay：4 个 task family、多个 Agent、0/1/K-shot、delayed labels、
   5 个 seed；
3. 用真实历史做 offline matched replay，禁止随机行切分；
4. 只有跨 family 和成本/延迟门通过，才进入 bounded real API；A800 仅在 encoder/head
   训练瓶颈被真实数据证明后考虑。
