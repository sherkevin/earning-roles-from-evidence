# 第二 structural root 决策备忘录 v0.1

日期：2026-10-07

状态：`CANDIDATE / NOT A DECISION`。本文件只把现有证据整理成可选择的 root split，
不修改 active benchmark，不打开 API/GPU 预算，也不把任何工程资格写成科学结果。

## 决策问题

当前 parity card 把 `PIPE3_stream_processing` 保留为 development candidate，但
`benchmark_baseline_v1.1` 和旧 manifest 仍写着 DIST1 development / PIPE3 confirmation。
在任何新的真实 baseline 之前，必须选择一个与 PIPE3 结构不同、并在执行前封存的
confirmation root。这个选择会改变 benchmark split，因此不能由失败结果或排版工作静默完成。

## 候选证据

| 候选 | 已有可复用证据 | 主要未关闭门 | 对 AAMAS 主张的风险 |
|---|---|---|---|
| `PIPE2_data_pipeline` 的 CSV overlay derived root | 10/10 seed 的 material shape audit；10/10 fixture 的 sandbox producer/recipient/adoption qualification；15/15 typed responsibility chain controls；严格 gate 已能把唯一 direct-use producer-defect 分支与 recipient repair 分开 | overlay 的 benchmark authority 尚未共同确认；仍无真实 recipient judgment、later assignment、独立 later outcome、完整成本和七臂 live parity；5 个 seed-equivalence 类不能被拆成独立样本 | 审稿人可能认为它是自造修复层或同一 generator 的变体；必须公开上游 TeamBench 语义和 overlay 的最小差异 |
| `PIPE1` native Planner/Executor/Verifier route | 原生材料、source→target route receipt、adapter/join、native material binding 和多项 fail-closed preflight 已复用；结构上明显不同于 PIPE3 | 22 项 preflight 只有 11 PASS；exact target scorer、source→artifact lineage、actor visibility、Verifier attestation、timezone/provider、budget、ledger route、relay control、identity randomization 未完成 | 直接启动会把路线接缝误写成 benchmark 结果；工程补齐成本和真实 API 风险都较高 |
| `DIST1_queue_race` | 原始 TeamBench 来源和早期 consumer checks | native grader 不执行真实 consumer；priority scorer 覆盖盲点已被真实 N02 结果暴露；完整 producer correctness、later use 和 independent outcome 尚未闭合 | 终局 consumer 分数会把 producer 缺陷、recipient integration 混在一起，不能支撑责任归因主线 |

## 当前建议

若目标是最短路径得到一条可识别的第二 root，优先把 **PIPE2 derived root** 作为
confirmation candidate 继续做低成本资格化；但只有在确认“CSV overlay 是公开、可复现、
不改变 TeamBench 任务语义的派生 benchmark 层”后，才可把它写入新的 active manifest。
若 benchmark 权威性必须完全依赖原生上游材料，则选 PIPE1，但应接受它还需要一轮
route/scorer/visibility 资格工作，不能为了赶进度直接发真实 API。

无论选择哪一个，DIST1 不应再作为主线 confirmation root。它可以保留为历史工程诊断，
不能用来填补责任归因证据。

## 选择后必须冻结的共同合同

1. root/source/generator/scorer/ledger/material hash 与 development/confirmation split；
2. `uniform`、`no_update`、`raw_acceptance`、`terminal_only`、
   `contextual_trust_linear`、`pooled_controller`、RARE 七臂及显式 closest-method `NO-GO`；
3. same menu、public read-cut、arrival/propensity、selected-only、完整成本和 UNKNOWN 分母；
4. producer contract、recipient action/use、adoption、later assignment、独立 later outcome；
5. 新 API 预算、provider/model/timezone、停止规则和 stream-clustered 统计。

在这些条件共同确认前，`baseline_frozen=false`、`scientific_claim_allowed=false`、
`api_runs_allowed=false` 和 `gpu_runs_allowed=false` 必须保持不变。

## 来源

- [candidate manifest consistency audit](../../coordination/task_reports/20261007_candidate_manifest_consistency_audit.md)
- [PIPE2 derived candidate report](../../coordination/task_reports/20261003_pipe2_derived_candidate.md)
- [PIPE2 gate reachability report](../../coordination/task_reports/20261003_pipe2_gate_reachability_audit.md)
- [PIPE1 preflight report](../../coordination/task_reports/20261007_pipe1_preflight.md)
- [selection-value/native-handoff screen](../../coordination/task_reports/20261007_selection_value_and_native_handoff.md)
