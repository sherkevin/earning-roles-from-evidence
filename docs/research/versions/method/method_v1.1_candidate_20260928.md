# 方法论与训练合同 v1.1-candidate

- **状态**：`CANDIDATE`
- **日期**：2026-09-28
- **生效范围**：只用于离线审查和资格实现；尚未替换 active method v1.0
- **对应故事线**：[`storyline_v1.1_20260928.md`](../storyline/storyline_v1.1_20260928.md)
- **Goal 约束**：[`GOAL.md`](../../../coordination/GOAL.md) ER-G2

这是一份可以被独立读者重放的候选算法合同。它把“实时更新”具体化为有界事件窗口、稳定锚点和可撤销的延迟修正；它不是已验证的创新，也没有替代真实 API、独立 root 或强 baseline 证据。

## 1. 唯一原始输入：封存事件

不再为每个公式随意引入新的原始符号。每个 decision 和 feedback 都来自一个不可变、带版本的事件 `e`。例如 PIPE3 的一条事件是：

```json
{
  "decision_id": "d-17",
  "task_id": "PIPE3_stream_processing",
  "task_index": 1,
  "x": {"stage": "draft", "queue": "priority", "required": "FIFO"},
  "candidates": [{"id": "peer-b", "version": "v1"}, {"id": "peer-c", "version": "v1"}],
  "chosen": {"id": "peer-b", "version": "v1", "propensity": 0.5},
  "delivery": {"sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
  "recipient": {"id": "peer-a", "action": "use"},
  "judgment": {"decision": "accept", "source_index": 5},
  "producer_contract": {"status": "PASS", "coverage_complete": true},
  "terminal": {"status": "PASS", "source_index": 9},
  "evidence_version": "ev-3"
}
```

所有后续量都是这个事件的投影或派生值：

| 符号 | 来源 | 上例中的实例 |
|---|---|---|
| `x_t` | `e.x` | `{"stage":"draft","queue":"priority","required":"FIFO"}` |
| `C_t` | `e.candidates` | `peer-b@v1, peer-c@v1` |
| `a_t,p_t` | `e.chosen` | `peer-b@v1, 0.5` |
| `o_t` | `e.delivery` | 交付 digest 为 64 个 `a` |
| `j_t,m_t` | `e.judgment`, `e.recipient` | `accept`, `use` |
| `y_e` | 固定 `label_mapping_version` 对 eligible 事件的映射 | `accept → 1.0` |
| `r_e` | responsibility scorer 的 typed eligibility 输出 | 此例为 `1.0`，但只在 scorer contract 与 action 归因通过后成立 |
| `k_e` | `source_index` | judgment 在 5 到达，terminal 在 9 到达 |
| `v_e` | `e.evidence_version` | `ev-3` |

如果字段缺失、版本不一致、权限边界不成立或 scorer 返回 `UNKNOWN`，相应事件的 `r_e=0`，不会被改成负例。

## 2. 固定编码与局部选择

一个固定、不可训练的哈希编码把任务与 peer 身份变成 `φ_t(v)∈R^d`。候选实现先固定 `d=64`，每一维是 signed hashing 后的 `{-1,0,+1}` 计数，再做 `||φ_t(v)||_2≤1` 归一化；输入只来自 `x_t`、候选的 `(id,version)` 和公开 workflow 字段。哈希种子和 `encoder_version` 写入 decision event，confirmation 前不能改变。

当前状态属于一个本地 peer neighborhood，不读取全局其他 agent 的私有记忆。给定状态参数 `θ_t`，候选 `v` 的分数为：

$$
s_t(v)=\sigma\!\left(\phi_t(v)^\top\theta_t\right),
\qquad
\pi_t(v)= (1-\varepsilon)\,\operatorname{softmax}_{v\in C_t}(s_t(v)/T)+\varepsilon/|C_t| .
$$

其中候选实现固定 `ε=0.10,T=1.0`，并把实际抽样概率 `p_t=π_t(a_t)` 封存。上例中 `C_t` 有两个 peer，若两者分数相同，则 `π_t=(0.5,0.5)`，抽到 `peer-b` 后 `p_t=0.5`。未来真实实验可以比较参数，但不能在看到 confirmation 结果后改动这些初始值。

## 3. 有界双时间尺度状态

状态由四部分组成：

1. `θ_ref∈R^d`：稳定锚点，默认从零初始化；
2. `A_fast,b_fast∈R^d`：最近 `B=256` 个 eligible 事件的逐维充分统计量；
3. `W_fast`：这 `B` 个事件的 `(key,φ,r,y)` 小窗口，用于过期和撤销；
4. `H_old`：最多 `K=128` 个固定旧事件的 `(φ,y)` reservoir，用于锚点保护。

每个事件只维护逐维量：

$$
A_{fast,i}=\lambda+\sum_{e\in W_{fast}}r_e\phi_{e,i}^2,
\qquad
b_{fast,i}=\sum_{e\in W_{fast}}r_e y_e\phi_{e,i},
$$

其中 `λ=1`。窗口预测参数为：

$$
\theta_{raw,i}=b_{fast,i}/A_{fast,i}.
$$

为了限制旧能力被一次新反馈覆盖，输出参数是锚点周围的投影：

$$
\theta_t=\theta_{ref}+\operatorname{Proj}_{\|\delta\|_2\le\rho}(\theta_{raw}-\theta_{ref}),
\qquad \rho=2.0.
$$

因此 `||θ_t−θ_ref||₂≤2.0`；在 `||φ||₂≤1` 时，任一候选的线性分数相对锚点最多改变 `2.0`。这不是“没有遗忘”的证明，而是一个可检查的变化上界。

## 4. 反馈闸门、重复与延迟修正

事件 key 固定为 `(delivery_id,evidence_version,source_index)`。到达一个 feedback 时按以下顺序处理：

```text
feedback(e):
  1. 校验 delivery/recipient/action/version/hash lineage。
  2. 若 scorer 是 UNKNOWN、权限不成立或 key 已被 supersede，返回 UNKNOWN/no-op。
  3. 从 label_mapping_version 得到 y_e∈[0,1]，从 responsibility gate 得到 r_e∈[0,1]。
  4. 若 key 已在 W_fast，用旧 (r_old,y_old) 反向减去其逐维贡献。
  5. 若 source_index 在当前 watermark 之后，把新 (r_e,y_e) 加入 W_fast；窗口超过 B 时先进者出窗并反向减去贡献。
  6. 保存 key、source_index、state_version 和 state_digest；同一 key 的重复事件不再更新。
  7. 每 G=32 个合法事件检查一次 H_old；只有 recent loss 下降且 old loss 不超过 ε_old=0.05，才令 θ_ref←θ_t 并清空 fast window。
```

`W_fast` 内的 correction 是 O(d) 的加减，因而不会重新训练 backbone。超出窗口的 correction 进入 `correction_queue`，当前决策不使用它，并记录 service lag；只有下一次 checkpoint replay 通过后才可进入状态。这个保守规则把“无法廉价撤销”标成可审计的 UNKNOWN，而不是悄悄覆盖历史。

上例中，`judgment.accept` 在 source index 5 到达，若 producer contract 和 action 归因通过，则 `r=1,y=1`；terminal 在 index 9 到达并 supersede 同一 evidence version 时，先删除旧贡献，再加入新映射。若 recipient 自己的 integration 失败但 producer contract PASS，责任 scorer 输出 `r=0`，该事件不会惩罚 `peer-b`。

## 5. Future assignment 的使用边界

在下一 task 开始前，assignment policy 只能读取 `θ_t`、公开 `H_old` 摘要和封存 evidence digest；它必须把 `assignment_id`、`evidence_ids`、`state_version`、`decision_digest` 和 propensity 写入 decision sidecar。F=0 的对照仍执行同一 task，但忽略 evidence；F=1 才允许上述读取。只有当 mutation（保持 chosen peer 和 propensity 不变、修改 evidence）能使 decision digest 失败时，才算证明 policy 实际消费了 evidence。

## 6. 可重放性质与复杂度

- 首次 feedback、窗口内 correction 和 eviction 都是 O(d)；selection 是 O(|C_t|d)；每 G 个事件的旧 reservoir 检查为 O(Kd)，摊销更新成本为 `O(d+Kd/G)`。
- 状态大小上界为 `O(d(B+K))`；候选版本替换默认新 key，不覆写旧状态。
- `feedback_id/key` 去重保证一次更新；`source_index` 和 watermark 保证乱序输入按固定规则重放；snapshot 保存所有计数、窗口 key、anchor、版本和 digest，restore 后下一事件结果必须逐字节一致。
- 这几个不变量必须通过零调用 mutation tests，再进入真实实验；当前文档尚未声称它们已通过。

## 7. 必须对比与停止条件

同一 `φ`、候选、propensity、预算和 event stream 下，至少比较 frozen/no-update、raw acceptance、terminal-only、contextual trust、RLS/linear associative comparator、周期 refit 和本候选方法。若 contextual trust 或 RLS 在同信息下解释全部收益，不能把 anchor/window 组合写成主创新；若窗口带来及时性却造成 old-root 遗忘或完整成本恶化，也不能声称目标满足。

## 8. 当前状态

这是一个可运行性候选，尚未锁为 active method，也没有真实 API、独立 root、16-cell factorial 或 A800 结果。下一步是为 typed projection、responsibility sidecar、event-time interleaving、correction、snapshot/restore 编写零调用不变量测试；通过后才讨论是否把本候选提交为 active method v1.1。
