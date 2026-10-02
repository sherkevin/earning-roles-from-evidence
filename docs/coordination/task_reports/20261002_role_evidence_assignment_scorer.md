# Stateless role-evidence assignment scorer — 2026-10-02

状态：`PARTIAL`。这是一个 assignment-side comparator seam，不是最终方法、不是 backbone
选择，也不是 benchmark 结果。本轮没有调用 LLM API、没有 GPU/Nebula 任务，Goal 与 active
method 没有修改。

## 目的

在不把 terminal quality 或 producer score 偷换成 situated judgment 的前提下，给
`RoleEvidenceOffer` 一个可执行的 public-input 到 assignment-score 映射。它复用现有
preview → assignment → commit 顺序，不调用持久 policy updater；因此发布 evidence 仍保持
`theta` 和 policy state 不变。

## 实现

新增 `scripts/peerrolebench_role_evidence_scorer.py`，版本为
`role-evidence-judgment-beta-v1`。对 read cut 前、按 candidate 绑定的公开 judgment 使用冻结
映射：

```text
accept            -> 1.0
accept_with_rework -> 0.5
reject_redo       -> 0.0
```

对 candidate `c`：

```text
mu_c = (1 + sum(label_j)) / (2 + n_c)
score_c = base_score_c + 2 * (mu_c - 0.5)
```

`quality_score`、producer `Qp`、private scorer 字段和 later outcome 不进入输入 digest。
每个返回值都携带 candidate 顺序、visible evidence ids、posterior means、scores 和
`input_digest`，便于与后续 assignment decision digest 对照。未知 judgment、越界 candidate、
read-cut 不合法或 base-score 形状错误会拒绝。

这是一个有明确先验和映射的 comparator，不是“我们的方法已经确定”。若未来把它作为主
assignment 规则，映射、先验、scale 和无 evidence candidate 的探索语义仍需在实验卡中冻结。

## 验证

`tests/test_peerrolebench_role_evidence_selection.py` 与 offer tests：初版回执 `9 passed`；
接入 preview wrapper 后的 v2 回执为 `10 passed`。新增
`preview_role_evidence_selection_with_public_judgment`，默认 hand-authored overlay 入口保持
不变。
配置、源码 hash、命令、原始 pytest 输出和 summary 保存在
[`n03_role_evidence_assignment_scorer_20261002`](../../../experiments/logs/n03_role_evidence_assignment_scorer_20261002/)
和 [`n03_role_evidence_assignment_scorer_20261002_v2`](../../../experiments/logs/n03_role_evidence_assignment_scorer_20261002_v2/)。

- 只修改同一 evidence 的 judgment，score 和 posterior 改变；
- 只修改 `quality_score`，score 和 public-judgment input digest 不变；
- 同一 menu、base score、fresh RNG、state 和 IDs 下，旧 hand-authored overlay 的选择仍不
  因 evidence 内容改变，继续作为当前 runner 的负向识别审计；
- B evidence 只能绑定 B 的 assignment subject，现有 selection/ledger invariant 未放宽。

这些是零调用工程验证，不能证明 judgment 的预测性、future utility、实时训练收益或 baseline
优越性。

## 尚未关闭的门

该 scorer 还没有接入七 arm live runner，也没有在同一菜单下为 B/C 都提供真实可归因 evidence
以测 decision mutation；raw acceptance 仍必须走独立 projection，terminal-only 仍只能读
terminal channel。第二 root authority、独立 live histories、成本和 statistical gate 仍
保持开放。
