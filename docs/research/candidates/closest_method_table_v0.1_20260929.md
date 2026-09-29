# Candidate closest-method table v0.1

- **状态**：`CANDIDATE_NOT_ACTIVE`
- **目的**：把“不是已有 trust/bandit/role coordination 的同义改写”变成逐项可执行审查；不是穷尽式文献综述。

| 近邻 | 观察/输入 | 归因与传播 | 时序/更新 | assignment | 本项目必须证明的差异 |
|---|---|---|---|---|---|
| REM-style role coordination | interaction outcomes and role observations | role taxonomy shared for partner choice | interaction-driven role update | future partner choice | recipient-owned integration must not become producer evidence; delayed contradictory evidence must be reversible |
| task delegation with third-party impressions | task/context competence, impressions, dependency outcomes | third-party impressions can propagate | delayed/bandit-like competence update | delegate next task | typed producer/recipient/sink ownership plus independent later-use target under same budget |
| Meta-Team L2-style downstream reflection/profile | interaction traces and post-task result; teammate profiles | qualitative profile can affect later recruitment/team structure | post-task L2 profile update; L3 scaffold update | later recruitment/structure | closest semantic candidate, but original terminal/trajectory information is wider; requires an independently implemented public-information adapter and fixed profile schema |
| reputation / pooled controller | public or pooled history | broad public reputation | aggregate update | menu or pool selection | local graph, different future owner, public evidence digest and no private memory leakage |
| delayed contextual trust/bandit | context, selected feedback, propensity, arrival delay | usually peer-level trust | delayed contextual update | pre-execution choice | same-information adapter must be unable to reproduce responsibility-safe correction, or novelty fails |
| raw acceptance / terminal-only | recipient accept or terminal result | no explicit ownership | direct label or terminal label | selection | situated judgment must add independent out-of-sample information beyond these signals |
| diagonal RLS / online logistic / periodic refit | fixed features and labels | updater-specific state | incremental or batch refit | chosen policy | updater is comparator; any gain must come from responsibility/late/public mechanism, not ordinary optimizer |

## Mandatory audit columns for each faithful adapter

For every row, record source, exact information fields, hidden fields, public/private state, responsibility semantics, selected-only denominator, arrival/correction semantics, state capacity, exploration, model/API/tool/token cost, and assignment timing. A name-only citation is not a baseline.

## Current result

严格标准下，ArtifactRole 没有可直接复现的 published drop-in closest baseline：现有工作没有同时覆盖 artifact handoff、recipient use/judgment、producer attribution、selected-only、arrival/correction 和 later assignment。允许独立按论文语义重实现时，Meta-Team L2 是唯一进入候选的近邻，状态为 `NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`；它不能被写成 upstream reproduction。DecisionBench 只作 selector/delegation control，CooperBench 只作 collaboration substrate，graph-ipd/PeerSelect 只作机制副轨。

Meta-Team 候选必须拆成 `L2-original-info`（宽信息上限诊断）、`L2-public`（主同信息比较）和 `L2-ablation`（profile-only/no-L3）。在固定 profile schema、摘要预算、公开事件边界、selected-only、event-time/correction、later assignment、成本和独立 history 前，baseline 仍是 `NOT_FROZEN`。四事件 stream 仍只是最小 adapter test，不能替代这些 qualification。
