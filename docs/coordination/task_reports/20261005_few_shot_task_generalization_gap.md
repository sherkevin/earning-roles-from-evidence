# Task report — Few-shot task generalization is an open scientific gate

- **日期**：2026-10-05
- **状态**：BLOCKED_BY_EVIDENCE
- **对应 Goal**：方法 G1/G2；benchmark G3（task-family split、闭环效用和实时更新）
- **goal_change_requested**：false

## 发现

当前 `contextual_trust_linear` 在固定的 `hash64-v1`、64 维 bounded feature 上做
selected-only diagonal RLS。它可以逐条更新候选选择状态，但它不是一个显式的
few-shot 任务记忆，也没有执行“从历史任务库检索相似任务，再用相似任务表现支持当前
选择”。因此目前不能宣称已经解决任务泛化。

## 需要的功能

对于新任务 `x_t`，系统应在严格的历史 read-cut `M_{<t}` 内：

1. 为当前任务和候选 Agent 形成可复现表示；
2. 从历史交接证据中检索相似任务/相似角色条件；
3. 用相似记录的接收者 judgment、later outcome、时间和成本形成候选支持度；
4. 将支持度、全局先验、风险/成本和探索项合成为选择分数；
5. 在延迟反馈到达后追加记忆，并只对已绑定的 selected candidate 做一次更新。

可作为待验证的抽象形式：

```text
z_t = Encoder(task_t, role_context_t)
N_t = TopK(sim(z_t, z_e), e in M_<t)
support(c) = weighted_mean(label_e for e in N_t with candidate c)
utility(c) = prior(c) + support(c) - cost/risk + exploration(c)
```

这只是候选模型，不是已接受的最终方法；`Encoder`、相似度、K、时间衰减、跨角色
匹配和 path-credit 规则均需通过实验确定。

## 现有延迟反馈接缝

现有 `DelayedPolicyAdapter` 已把 source evidence publication、future assignment
和 later selected-only update 分开，并按 sealed read-cut 防止未来结果泄漏。它可以作为
记忆层的原子写入与回放边界，但当前存储/更新状态还不是可证明的相似任务检索器。

## 必须补的实验

- 按 structural task root 做 leave-one-root-out 和时间切分，禁止随机行切分造成近重复泄漏；
- 比较 no-memory、uniform、普通 `contextual_trust_linear`、最近邻/加权检索、
  pooled history 和 RARE candidate；
- 设置 0/1/K 条 support 的 few-shot 曲线，以及新候选版本、角色漂移和任务组合漂移；
- 报告 assignment-level future utility/regret、later adoption/terminal quality、
  latency、memory size、cost、UNKNOWN 分母、旧任务遗忘和置信区间；
- 预注册 read-cut、候选菜单、propensity 和相似度版本，确保 later outcome 不进入早期检索。

## 当前结论

这条问题必须进入方法和 benchmark 验收标准。当前工程资格只证明了延迟更新接缝和
固定特征合同可运行，不能证明 few-shot 泛化、任务相似度有效或选择收益。未完成上述
离线设计和匹配 baseline 之前，不启动新的 API/A800 科学实验，也不把 RLS 或固定
hash 特征写成最终创新。
