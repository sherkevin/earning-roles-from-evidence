# Task report — Self-audit of the profile/evidence/delayed-residual fusion

- **日期**：2026-10-05
- **状态**：BLOCKED_BY_EVIDENCE
- **对应 Goal**：ER-G2 方法有效性、创新性、实时性和稳定性；ER-G4 可识别实验
- **goal_change_requested**：false
- **审查模式**：AAMAS methodology-focus；独立 Codex devil's-advocate 复核；公开先例核对

## 1. 被审查的候选

候选融合包括三层：

1. 由历史 evidence 压缩出的文字 profile embedding；
2. 从相似历史任务检索的 episodic prototypes/evidence；
3. 由 delayed later outcome 更新的小型 residual head。

目标分数把三层与 base score、cost 和 exploration 合并。

## 2. 结论评分

| 门 | 当前判断 | 分数（10 分） | 原因 |
|---|---|---:|---|
| 可实现性 | 部分通过 | 7.0 | 可用冻结 encoder、经验库和小型 CPU head 实现；但 profile 版本、Top-K、head 更新和回滚合同尚未落地 |
| 标签有效性 | 不通过 | 4.0 | `y^J`、`y^L`、UNKNOWN、未选择候选和 judge reliability 尚未形成完整可训练合同 |
| 任务泛化 | 不通过 | 4.5 | embedding 相似度可能只反映主题/Agent 身份；尚无未见 task family 和时间切分结果 |
| 稳定/实时 | 部分通过 | 5.5 | append-only memory 和小状态有潜力，但画像刷新、遗忘、漂移、延迟和 backlog 尚未实测 |
| 可识别性 | 不通过 | 3.5 | profile 与 prototype 可能重复计算同一证据；融合权重和残差 head 的独立贡献尚未隔离 |
| 创新性 | 条件性偏弱 | 3.5 | profile routing、能力向量相似度和动态语义匹配已有公开先例；目前真正可区分的是责任/时序/跨 owner transfer，但还没有完成机制化和实验识别 |

**总判定：不通过当前方法门。** 这不是 Goal 降级，也不是否定 profile idea；它表示当前
版本不能写成“已经达到有效性和创新性要求”。

## 3. 关键问题

### 3.1 同一标签被重复使用

如果文字 profile 和 episodic prototype 都从同一批 `y^J` 生成，再把二者相加，模型会
把同一证据计算两次。表面上看像两条互补路径，实际上无法知道收益来自哪里。

### 3.2 延迟标签没有完全隔离

`y^L` 是未来 assignment/use 的结果，不能和源 episode 的 `y^J` 混成一个分数。当前
候选只说 residual head 使用 `y^L`，但没有固定其输入快照、更新窗口、负样本和校准方式。

### 3.3 语义相似度不是能力匹配

任务和画像都包含“队列”一词，不代表该 Agent 能在当前版本、当前责任位置完成任务。
需要 task-only、identity prior、profile permutation 和 topic-matched controls，否则无法
排除词汇重合、Agent 热度或评价者风格。

### 3.4 选择偏差仍然存在

只有被选择的 Agent 有反馈。未选择候选不能自动成为负例；若没有探索和 propensity 修正，
画像会越来越偏向早期被选中的 Agent。

### 3.5 多模态能力没有正式状态

单一文字画像会抹平一个 Agent 的多个能力方向；原型方案提出了多原型，但尚未规定聚类、
原型数量、负原型、版本替换和容量淘汰。

### 3.6 “融合”本身还不是创新机制

[FlyRoute](https://arxiv.org/abs/2605.22057) 已有 success-store、profile distillation、
检索和探索；[AgentNet](https://proceedings.neurips.cc/paper_files/paper/2025/file/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html)
已有能力向量相似度分配；[DyTopo](https://arxiv.org/abs/2602.06039) 已有语义匹配动态拓扑。
所以“画像 + embedding + memory + head”如果没有独特的 label/credit 时序和可反驳效果，
审稿人会把它看作工程组合。

## 4. 修正后的候选原则

不再让三层共享同一时间段的证据：

```text
profile snapshot P_k     ← 只由 read cut ≤ k 的旧证据压缩
memory delta D_(k,t)      ← 只由 profile snapshot 之后的新 y^J 组成
delayed residual θ        ← 只由已经完成 future assignment/use 的 y^L 更新
```

选择时使用 `P_k + D_(k,t) + residual(θ)`，并在每个输入上记录 snapshot/version/digest。
画像刷新时封存旧 profile、清空或重新标定 delta，不能让同一 evidence 同时作为 profile 和
delta 再进入 head。

## 5. 必须补的实验和通过条件

CPU 零 API 原型必须包含：

1. temporal read-cut 和 task-family holdout；
2. profile-only、prototype-only、residual-only、full fusion、no-memory、RLS；
3. profile/prototype permutation、task-only embedding、identity prior、topic-matched kNN；
4. 0/1/K-shot、feedback sparsity、candidate version shift 和 delayed feedback；
5. per-episode predictions、Brier/calibration、regret、future utility、latency、memory、
   UNKNOWN、forgetting 和 clustered bootstrap/randomization interval。

候选只能在以下条件同时满足后进入真实 API：

- full fusion 在至少 3/4 个未见 task family 上超过最佳简单 baseline；
- profile/prototype permutation 退化到 chance；
- residual 更新改善 feedback 到达后的窗口，同时不损害 cold-start；
- 没有 future evidence 泄漏，且每条样本的来源时间可重放；
- 贡献来自预注册的 delayed responsibility transfer，而不是任意调权重。

## 6. 当前动作

继续保留用户的 profile embedding 作为 cold-start/profile baseline；将“分时间快照、分标签、
分职责”的修正版作为候选方法 v0.2；在通过 CPU gate 前，不启动新的 API/A800，也不把
融合方案写成最终创新。历史失败和当前不通过状态保留，不修改 Goal。
