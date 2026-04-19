# Round1 v3 — 配对统计附录（peer 为基线）

**任务集合**：`artifacts/round1/run_20260411_102202/fixed_peer_calibrated/raw_inputs.jsonl` 对应的 200 个 `task_id`（各方法目录下 `parsed_predictions.jsonl` 对齐）。

**指标**：逐题 `answer_f1`；**均值差** = mean(peer F1 − 对照 F1)，与聚合表上 F1 差一致。

## 1. Bootstrap 95% CI（配对差分的均值）与符号检验

对每一对照方法，在 **非平局** 子样本上：\(W\) = peer 更优的题数，\(n\) = 非平局题数；**双侧符号检验** \(H_0: p=0.5\)（精确二项）。Bootstrap：对 200 个配对差分有放回重抽样 10 000 次，取均值的分位点 CI。

**复现命令**：

```text
python scripts/compute_paired_bootstrap.py ^
  --run-dir artifacts/round1/run_20260411_102202 ^
  --baseline fixed_peer_calibrated ^
  --compare central_orchestrator central_orchestrator_with_reflection fixed_self_calibrated fixed_static_roles fixed_self_claim single_agent ^
  --metric answer_f1 ^
  --n-bootstrap 10000 ^
  --seed 42 ^
  --out-csv artifacts/round1_v3_paired_stats.csv
```

（Linux/macOS 将 `^` 换为 `\`。）

## 2. 结果表（摘自 `artifacts/round1_v3_paired_stats.csv`）

| compare | n_tasks | n_ties | mean(peer−compare) F1 | boot 95% CI | sign p (two-sided) | wins_peer / wins_compare |
|---------|---------|--------|-------------------------|-------------|---------------------|---------------------------|
| central_orchestrator | 200 | 182 | 0.015233 | [−0.012673, 0.045551] | 0.237885 | 12 / 6 |
| central_orchestrator_with_reflection | 200 | 167 | 0.016095 | [−0.023564, 0.056488] | 0.48685 | 19 / 14 |
| fixed_self_calibrated | 200 | 171 | 0.017723 | [−0.017040, 0.052966] | 0.136046 | 19 / 10 |
| fixed_static_roles | 200 | 182 | 0.015233 | [−0.012673, 0.045551] | 0.237885 | 12 / 6 |
| fixed_self_claim | 200 | 148 | 0.033559 | [−0.018917, 0.086296] | 0.33175 | 30 / 22 |
| single_agent | 200 | 148 | 0.033559 | [−0.018917, 0.086296] | 0.33175 | 30 / 22 |

## 3. 解读（附录用语建议）

- 相对 peer 的 **平均 F1 优势** 在点估计上为正，但 **bootstrap CI 均跨 0**（\(α=0.05\)），不宜宣称「显著优于」；更稳妥表述为 **同批数据上略高、不确定性较大**。
- **符号检验**：在非平局子集上 p 均 **> 0.05**，与 CI 结论一致。
- `fixed_self_claim` 与 `single_agent` 在本 run 的逐题 F1 **完全一致**（故统计行相同），可合并叙述或只保留其一入正文。

## 4. 诚实结论（避免过度声称显著性）

本附录基于 **n=200**、**同一 Hotpot 子集**；配对检验针对 **答案 F1**，**未**对启发式 token 成本做联合推断。在 **bootstrap CI 跨 0、p>0.05** 的前提下，主文宜以 **效应量叙述 + PAR / 过早接单率 + 可追溯案例**（见 `round1_v3_central_orchestrator_metrics.md`）支撑方法对比，**避免**将「略高的平均 F1」写成统计显著优势。

## 5. 全量 7405（三主）配对与主表

**n=200 子集以外**的 Hotpot validation 全量（7405 题 × `fixed_peer_calibrated` / `fixed_static_roles` / `fixed_self_claim`）的配对统计、主表 CSV 命名、与 **实测 API token** 对齐方式，见 **`artifacts/round1_v3_statistics_fullval.md`**；合并产物为 `artifacts/round1/round1_v3_main_table_fullval.csv` 与 `artifacts/round1_v3_paired_stats_fullval.csv`（全量完成后应覆盖 pilot 占位内容）。
