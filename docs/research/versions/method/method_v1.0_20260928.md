# 方法论与训练合同 v1.0

- **状态**：`ACTIVE`
- **生效日期**：2026-09-28
- **类别**：method
- **前一版本**：无；历史候选见 `docs/archive/document_reorganization_20260928/`
- **目标约束**：[`docs/coordination/GOAL.md`](../../../coordination/GOAL.md) ER-G2

`ACTIVE` 只表示这是当前唯一的方法合同，不表示算法已经验证或 backbone/updater 已经选定。

## 1. 方法要解决的最小数学问题

每个 episode 先给出任务上下文 `x_t` 和合法候选 producer 集合 `C_t`。选择器在执行前选择一个候选 `a_t ∈ C_t`，候选产生交付 `o_t`，真实 recipient `j_t` 读取并采取动作 `m_t`。独立 contract/later-use 检查产生结果 `y_t`；不可归因、不可见或资源失败的事件为 `UNKNOWN`。

选择器在时刻 `t` 只能使用公开历史和当前上下文：

$$
 a_t \sim \pi_\theta(\,\cdot\mid x_t,C_t,R_t),
$$

其中 `R_t` 是已到达且通过责任过滤的 role evidence；隐藏 gold、未来结果、private scorer 和其他 policy 的记忆不能进入当轮决策。

一条 feedback 只有在 `producer`、`recipient`、task/dependency context、delivery digest、版本、recipient action 和事件顺序都能绑定时才是 eligible。用 `g_t` 表示 episode `t` 的绑定事件，用 `τ_t` 表示它到达的序号；到达批次为 `B_k={g_t:τ_t=k}`。episode/decision 的索引 `t` 与 feedback arrival 的索引 `k` 不混用。第 `t` 次选择前的快照由预先定义的 watermark/replay 规则处理所有已到达事件得到；在线状态按到达批次演化：

$$
 R^{(k+1)}=U(R^{(k)},B_k),\qquad
 B_k=\{g_t:\tau_t=k\}.
$$

`U` 必须对每个 eligible 事件一次更新、对 UNKNOWN/INVALID 事件 no-op、可重放、可处理延迟/乱序且有界，并记录 update latency、状态字节数和完整成本。延迟/乱序不能靠到达时间直接改写 episode 顺序；候选规则必须在实验前固定为 watermark 或 immutable event-log replay，并记录 service lag。
在第 `t` 次决策前，令 `k_t^-` 为该决策封存时已处理的最大 arrival index，选择器实际读取 `R_t=Snapshot(R^{(k_t^-)})`；这个 snapshot/watermark 规则必须随 decision event 写入 ledger。

## 2. 角色状态和公共/私有边界

角色状态必须区分：

- `P_v(c)`：producer `v` 在职责情境 `c` 下、可按权限共享的公共 evidence；
- `B_u(v,c)`：owner `u` 对 `v` 的私有 trust；
- `H_u`：owner 自己的经验/技能状态；
- `W_t`：workflow、依赖和权限的可审计状态。

主张是 `P_v(c)` 是否能帮助未来 owner 选择，而不是把某个 owner 的私有信任重命名为公共角色。所有 policy 使用相同的初始状态、机会、预算和信息规则；各自 live history 可以因选择不同而自然分叉，不能把 proposed policy 的 realized memory 复制给 control。

## 3. 候选核心机制：RARE

`Responsibility-Aware Role Evidence (RARE)` 是待验证候选名，不是已锁定算法。它要求先经过责任门：recipient 的判断必须与实际使用/修改/拒绝动作绑定，producer-owned contract 与 recipient-owned integration 分开计账，无法归因则 `UNKNOWN`。只有过滤后的事件才进入角色状态。

候选实现采用小状态充分统计量和受保护增量更新；可用的最小接口是：

```text
choose(x, C, snapshot) -> (selected_peer, propensity, decision_digest)
feedback(event) -> {eligible_update | UNKNOWN | INVALID}
snapshot()/restore() -> versioned state
```

状态的具体表示（计数/均值、上下文线性状态或冻结表示加小 head）和更新器（RLS、online logistic/SGD、周期 refit 或新 updater）必须作为正交实验条件选择。RLS、Laya、AnyJev 和普通 bandit 只能作为实现或比较器，不能先验地称为创新。

一个可运行的候选形态是：将 `g_k` 编码为 bounded feature `φ_k`，维护每个 `(producer, context, version)` 的可交换统计量 `S_k`，以信赖域或旧任务 holdout 检查拒绝会显著增加遗忘的写入。此处不预先指定唯一 `q-u` 公式；历史 RARE 草图中把 `UNKNOWN` 与负证据混合的风险仍未解决，不能直接移入论文主结果。

以下三项仍是实现前的硬缺口：`context` 的词表/哈希、容量与淘汰及跨 context 泛化；早到的 situated judgment 在 later outcome 到达后的校正/撤销语义；事件重复、校正重复和 checkpoint/replay 的幂等规则。它们没有定义前，`U` 只是接口合同，不是完整可运行算法。

## 4. 必须证明的三个性质

**实时性。** 反馈到达后只更新必要的局部状态；报告 update 和选择端到端 p50/p95、service lag、状态大小、token/tool/GPU/人工成本。

**时效性。** 在预注册的 task/peer drift 后，未来选择在窗口 `W` 内响应；延迟和乱序 feedback 通过固定 replay/watermark 规则处理。

**稳定性。** 旧 task/root holdout 的峰值和平均性能下降、恢复窗口、UNKNOWN 率都要有独立 stream 证据。出现明显遗忘时不能用扩大窗口或删除旧数据来改写结果。

## 5. 与 baseline 的关系

必须在相同 `φ`、信息、propensity、预算和历史可见性下比较：uniform、no-update、raw acceptance、terminal-only、contextual trust/bandit、pooled controller 和 RARE；训练方式再正交比较 RLS、online logistic/SGD、periodic refit 与候选增量 updater。若 RARE 没有超出同信息 trust/bandit 的预先声明增量，主创新不成立。

## 6. 实现与上线流程

1. 先冻结事件 schema、可见性、责任门、UNKNOWN 和 replay 规则。
2. 用零 LLM fixture 做 schema、重复、乱序、资源失败和 snapshot/restore 检查。
3. 用一个 root 的最小真实流诊断信息价值，不把它当效果。
4. 资格和强 baseline 通过后，再开独立 root、独立 live history 的开发卡。
5. 只有真实信号和明确瓶颈成立，才选择一个 backbone/updater 做 bounded A800 challenger。
6. 每次更新写 append-only event、state digest、版本、延迟、成本和结果；失败/UNKNOWN 永不回写。

## 7. 当前未决事项

最终 backbone、表示维度、更新器、遗忘保护阈值、漂移窗口和 assignment policy 均未锁定。它们必须由 benchmark qualification、离线数学检查和强 baseline 的真实瓶颈共同决定；本文件不把 Laya、AnyJev 或 Qwen 直接指定为最终答案。

## 8. 对照标准

方法审查使用 [`method_v1.0_20260928_eval.md`](../evaluation/method/method_v1.0_20260928_eval.md)。故事边界见 [`storyline_v1.0_20260928.md`](../storyline/storyline_v1.0_20260928.md)，可执行实验卡见 [`benchmark_baseline_v1.0_20260928.md`](../benchmark-baseline/benchmark_baseline_v1.0_20260928.md)。
