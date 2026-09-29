# Round 0 — independent devil's advocate

- **Role**：AAMAS rejection case
- **Source**：local independent agent; read-only; no repository edits
- **Confidence**：文档事实和方法未闭合判断高；prior-art 排查不是穷尽式

## POSITION

题目值得研究，但当前 active 文档尚未给出足以排除强替代解释的完整算法。应判为“不通过方法验收，保留研究主线”，不能把方法未通过解释为 Goal 被否定。

## STRONGEST OBJECTIONS

### D1 prior-art threat

2013 REM（Trust-based role coordination）已从交互表现演化角色 taxonomy，并向未来 partner choice 提供角色信息；2026 JAAMAS task delegation model 已包含 third-party impressions、task-context competence、bandit selection、依赖传播与部分惩罚。因此“第三方评价→角色传播→未来选择”本身不足以立住独特创新。真正可能的差异是：recipient integration 错误会污染 producer evidence，而迟到矛盾结果可以撤销/校正；这必须写成唯一可计算机制。

### D2 circularity/leakage

若 responsibility gate 读入要预测的 producer contract，再在 gate 后样本上证明 judgment 预测该 contract，信息增量可能来自 contract 筛选或泄漏。需字段到达表和 `gate-only/judgment-only/gate+judgment/contract-only` 对照，目标必须是 gate 未使用的独立 later-use。

### D3 exchangeable peers

若 peers 同模型、同 prompt、无持久状态，则给定任务下 `E[Y_t|x_t,a_t=v]=μ(x_t)`；identity-based selector 只能追逐随机幸运者。必须定义 `H_u` 的自然演化与产出读取路径，并做 identity permutation。

### D4 interface, not algorithm

`U` 和 RARE 仍是任意接口。没有唯一目标、状态、更新、assignment 和 late correction，就无法回答是哪一个机制产生收益。

### D5 candidate-only algebra risks

历史 RARE-Anchor 草图存在待复核的代数风险：在 `d=1, φ=1, y=1, λ=1, ρ=2` 时，consolidation 可能把刚学到的 `θ=.5` 刷回 `θ=0`；`superseded` 和 `correction_queue` 也可能无界增长。这不是 active 方法结果，必须先做零 API 单测，不能直接写论文。

### D6 factorial interaction is insufficient

更新和读取同时打开就有效的普通串联系统也会产生正交互 `M(U,F)=cUF`。因此 factorial 只能检验必要性，不能单独识别创新；必须用完整机制与同信息 nearest control 比较，并用 independent live histories 测闭环效用。

### D7 realtime/stability trade-off

速度上界不能推出同时适应 drift 和不遗忘；不可区分的概念漂移甚至可能要求互相冲突的目标。必须区分可由 context/version 区分的 drift 与不可区分 drift，分别定义 retention target、backlog 和恢复窗口。

### D8 benchmark cannot yet separate record system from role learning

当前 benchmark 仍缺 authority/root/runner parity、later assignment 和独立 stream。责任记录系统通过不等于 role learning 通过；PeerSelect payoff 不能替代 ArtifactRole recipient/adoption 链。

## DECISION TESTS

K1–K8 见 `claims.jsonl` 及 manager synthesis：信息增量、闭环 assignment、同信息替代、归因泄漏、在线预算、稳定成本、重放唯一性和持久 peer 差异。

## RECOMMENDATION

优先顺序：近邻机制差异表 → 字段到达/独立目标表 → peer 持久状态与身份置换 → candidate RARE 零调用代数复核 → method lock → benchmark/baseline parity。暂不启动 A800。
