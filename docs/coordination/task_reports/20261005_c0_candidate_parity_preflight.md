# N03-next-r5.69：C0 candidate parity preflight

日期：2026-10-05
状态：`PARTIAL`（candidate parity 工程子门通过；live/scientific parity 未开始）
`goal_change_requested=false`

## 目的与范围

在 r5.67 修复 feature/base-score 输入合同、r5.68 完成 A0/B0 决策后，运行一条最小
CPU-only C0 preflight。它只比较 `contextual_trust_linear` 与 `RARE` 两个 candidate arm，
不修改 active 七臂 manifest。目标是确认后续 live runner 的三个前置条件：

1. 两个 policy 消费同一 candidate menu、公共 `phi`、base score、read cut、arrival、RNG
   和版本字段；
2. 两个 policy 有独立状态 namespace，snapshot/restore 不交叉；
3. chosen candidate 会进入 arm-specific outcome namespace，不能复用另一 arm 已生成的
   outcome。

最后一项只验证命名和隔离接缝；receipt 中的 outcome 是 namespace 记录，不是质量 label，
不能被解释为 recipient 使用或 later-use 结果。

## 执行与证据

运行前配置、源码 hash、registry/schedule/RNG digest 写入：

[`experiments/logs/n03_c0_candidate_parity_qualification_20261005_v1/config.json`](../../../experiments/logs/n03_c0_candidate_parity_qualification_20261005_v1/config.json)

逐 policy trace 和汇总：

- [`raw.jsonl`](../../../experiments/logs/n03_c0_candidate_parity_qualification_20261005_v1/raw.jsonl)
- [`summary.json`](../../../experiments/logs/n03_c0_candidate_parity_qualification_20261005_v1/summary.json)

配置明确 `real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false` 和
`baseline_frozen=false`。输入来自已有 `PIPE3 recipient_only` hand-authored fixture，
没有重写或回填历史实验。

## 结果

1/1 C0 case 通过：

- 两个 arm 的 offer input digest 序列逐项相同；public stream 的 menu、registry、`phi`、
  read cut、arrival schedule、RNG、propensity 和 state schema 均被写入 digest；
- 两个 arm 各自独立完成 2 次 selection、1 次 selected-only update，snapshot/restore
  后状态一致；
- 4 个 outcome namespace 全部带有 policy namespace，跨 arm `outcome_id` 无碰撞；
- `contextual_trust_linear` 与 RARE 的 update 后 propensity 不同，说明它们确实是不同
  updater，而不是同一结果的别名。

这不是 live parity：fixture 的 delivery、recipient action、adoption、later assignment
和 outcome 没有按 chosen candidate 重新生成，也没有真实 LLM judgment 或 measured cost。

## 与验收标准的对照

- **benchmark/baseline**：公共输入与 namespace 工程子门进一步关闭；active manifest 仍
  是七臂，`contextual_trust_linear` 尚未成为正式 arm，baseline 仍 `NOT_FROZEN`。
- **方法**：same-`phi`、selected-only、snapshot/replay 的可执行接缝通过；responsibility
  gate、future assignment、later-use、独立 live history 和实时成本仍未验证。
- **故事线**：没有新增科学结果，不能写成“RARE 改善团队质量”或“自进化已被证明”。
- **Goal**：未请求任何降级。

## 下一步

将该 candidate preflight 的同信息合同接入 canonical live runner 设计，增加每个 arm 独立
的 chosen-candidate→delivery→recipient action→adoption→later outcome 生成；只有这些
结果和完整成本都独立记录后，才允许一条有界 PIPE3 development API stream。任何 shared
outcome、未来字段或错误 namespace 都应在 runner 启动前拒绝。
