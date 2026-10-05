# Candidate method — Few-shot delayed role selector v0.1

- **状态**：`CANDIDATE / NOT_ACTIVE`
- **日期**：2026-10-05
- **用途**：把“相似任务经验 + 链式责任反馈 + 快速在线更新”收敛成一个可实现、可消融的候选方法。
- **不代表**：最终 backbone、最终 updater、benchmark freeze 或科学效果。

## 1. 方法目标

给定当前任务、角色和局部候选集，选择预期下游效用最高的 Agent。历史任务通常与当前
任务不完全相同，因此选择器必须同时具备：

1. **episodic few-shot path**：从已经发生的相似交接中快速取证；
2. **parametric generalization path**：用一个很小的在线状态跨相似任务共享规律；
3. **delayed responsibility update**：只有链路责任和后续使用结果完整时才更新持久状态；
4. **stability fallback**：历史经验不可覆盖，低支持度时回退到稳定先验并探索。

## 2. 可见输入和经验卡

一次候选选择只允许读取 sealed read cut `M_{<t}`。每条公开经验卡包含：

```text
task_signature        当前任务/角色的公开表示版本
role_signature        发送者、接收者和责任位置的版本化摘要
candidate_key         agent_id@version
judgment_label        接收者对发送者交付的 [0,1] 评价
later_outcome_label   未来 assignment/use 的 [0,1] 结果，可为空
arrival_index         该证据进入公共视图的顺序
lineage_digest        delivery → judgment → action → outcome 的摘要
cost                  token/tool/wall-clock/rework 等完整成本
status                PASS / FAIL / UNKNOWN
```

`UNKNOWN` 卡可以保留用于审计，但不能参与正负训练。原始 artifact、private gold、未来
terminal outcome 和其他 policy 的状态不进入公开经验卡。

## 3. 选择公式

### 3.1 任务表示和相似任务

对当前任务 `x_t` 和角色 `r_t` 形成表示：

$$
z_t=f_{\nu}(x_t,r_t),
$$

其中 `ν` 是表示版本。v0.1 的 CPU 原型先使用可复现的公开字段编码；冻结小型 encoder
和可训练 encoder 是后续正交条件，不能在同一实验中混用。

在 read cut 之前的经验库中检索：

$$
\mathcal N_t=\operatorname{TopK}_{e\in M_{<t}}
\left[\operatorname{sim}(z_t,z_e)\cdot
\operatorname{role\_match}(r_t,r_e)\right].
$$

相似度、`K`、角色匹配和时间衰减必须在实验卡中预注册。

### 3.2 两条经验路径

对候选 Agent `c`，从检索结果得到 episode estimate：

$$
q_{\mathrm{epi}}(c)=
\frac{\alpha_0+\sum_{e\in\mathcal N_t:c_e=c}w_e y_e}
{\alpha_0+\beta_0+\sum_{e\in\mathcal N_t:c_e=c}w_e},
$$

其中 `y_e` 优先使用 edge-local judgment；later outcome 作为独立结果头，不直接覆盖
原始 judgment。`w_e` 由相似度和预注册的 recency decay 得到。

同时，固定公共特征 `φ_t(c)` 进入一个小型参数状态：

$$
q_{\mathrm{param}}(c)=\sigma\!\left(\phi_t(c)^\top\theta\right).
$$

根据当前候选的有效支持量 `n_eff(c)` 做收缩：

$$
\rho_c=\frac{n_{\mathrm{eff}}(c)}{n_{\mathrm{eff}}(c)+\kappa},
\qquad
\widehat q_t(c)=\rho_c q_{\mathrm{epi}}(c)+(1-\rho_c)q_{\mathrm{param}}(c).
$$

支持量少时主要依赖稳定参数和先验；相似经验足够时才让 few-shot 证据主导。

### 3.3 选择和探索

$$
u_t(c)=b_t(c)+\gamma\widehat q_t(c)
-\lambda\operatorname{cost}_t(c)+\eta\operatorname{uncertainty}_t(c),
$$

$$
\pi_t(c)=\operatorname{softmax}(u_t(c)/T).
$$

`b_t` 是所有 arm 共享的基础分，`cost` 使用已冻结的成本合同，`uncertainty` 只用于
预注册探索。选择必须先 `preview`，记录完整概率和 propensity，再写入 assignment，
最后以固定 chosen key `commit`，不能在 assignment 后重新抽样。

## 4. 延迟反馈中心

延迟中心不把“发布经验”和“训练持久状态”混为一件事：

```text
source episode
  → responsibility gate
  → append immutable public evidence card
  → future assignment/read cut
  → target selection and actual use
  → later outcome
  → selected-only parameter update
```

伪代码：

```python
def choose(task, role, candidates, read_cut):
    z = encoder.encode(task, role)
    neighbors = memory.topk(z, role=role, read_cut=read_cut, k=K)
    for c in candidates:
        q_epi, n_eff = memory.estimate(neighbors, candidate=c)
        q_param = predictor.score(public_features(task, role, c))
        rho = n_eff / (n_eff + kappa)
        utility[c] = base[c] + gamma * (rho*q_epi + (1-rho)*q_param)
    return preview_softmax(utility)

def publish(source_episode):
    if not responsibility_gate(source_episode):
        return UNKNOWN
    memory.append(immutable_public_card(source_episode))
    return PUBLISHED_WITHOUT_POLICY_UPDATE

def apply_later_credit(assignment, later_episode):
    if not replay_and_lineage_gate(assignment, later_episode):
        return UNKNOWN
    memory.append(resolved_later_card(assignment, later_episode))
    predictor.update_selected_only(assignment.chosen, later_episode.label)
    return UPDATED_ONCE
```

## 5. 稳定性、时效性和速度来源

- **稳定性**：经验卡 append-only；参数状态以 ridge prior 初始化，更新采用 selected-only
  和 bounded residual；低相似度时回退到先验；旧卡不因新反馈被覆盖。
- **时效性**：新证据先进入公共经验视图，下一次 read cut 即可检索；持久参数更新等待
  后续 assignment/use 的完整结果，避免错误责任标签污染模型。
- **速度**：选择阶段只做固定维度编码、Top-K 检索和小向量打分；更新阶段只更新一个
  小型状态，不做大模型全参数反向传播。大规模经验库再替换为 ANN 索引，保持同一接口。

## 6. 与当前实现的关系

现有 `DelayedPolicyAdapter`、`RoleEvidenceOffer`、`preview→assignment→commit`、
`PeerHistoryV2` 和 `FeatureContextualTrustPolicy` 可分别复用为延迟中心、证据卡、时序
边界、持久历史和参数路径。当前代码尚未实现 `TopK` 相似任务检索、双头结果估计或
跨 root few-shot 泛化，因此本文件只是候选设计。

`contextual_trust_linear` 是普通 same-information RLS comparator；它必须保留为 baseline，
不能把“把 RLS 接到经验库”直接称为方法收益。候选方法的增量必须通过以下正交实验识别：

```text
no memory
episodic retrieval only
parametric online update only
episodic + parametric + delayed responsibility update
```

## 7. 实现顺序和停止条件

1. 先实现纯 CPU、零 API 的 experience-card schema、read-cut、Top-K 和 no-leakage replay；
2. 用同一 root 做 0/1/K-shot 与 leave-one-root-out 离线回放；
3. 与 uniform、no-memory、contextual_trust_linear、普通 weighted kNN 和 RARE 做同信息比较；
4. 只有检索延迟、记忆容量、跨 root 效用和遗忘指标通过预注册门槛，才进入 bounded live history；
5. 真实 API/A800 只在 live history 暴露出明确的表示或更新瓶颈后启动。

如果随机行切分、未来结果泄漏、UNKNOWN 被当负例、或 retrieval 不能超过 no-memory 同信息
baseline，则停止方法扩展，保留失败证据，不修改 Goal。
