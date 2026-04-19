# Round1 v3 — API `usage` 与启发式成本（分列）

## 1. 管线变更（Session 5）

- **`workspace/idea04_core/llm_client.py`**：`extract_usage(response)` 读取智谱返回体中的 `usage`（`prompt_tokens` / `completion_tokens` / `total_tokens`）。
- **`workspace/idea04_core/methods.py`**：每次 `call_llm` 后将 usage 记入当前 hop 的 `AgentOutput.usage_calls`（一 hop 内可能有多段调用，例如 CO+Reflection）。
- **`workspace/idea04_core/runner.py`**：`raw_model_outputs.jsonl` 每行增加 **`usage_calls`**（`list`）；`metrics.json` 增加：
  - `api_prompt_tokens_per_sample`、`api_completion_tokens_per_sample`、`api_total_tokens_per_sample`（对样本内所有 hop、所有调用求和再对样本取平均）
  - `cost_normalized_f1_api` = `answer_f1 / (api_total_tokens_per_sample / 1000)`（与启发式 `cost_normalized_f1` 并列）

## 2. 从 artifacts 复现「两列成本」

1. 跑**新**实验后打开 `.../<method>/metrics.json`，同时读取：
   - `token_cost_per_sample`（启发式，沿用 `120 + hop_count * 180`）
   - `api_total_tokens_per_sample`（实测）
2. 或将各方法 `metrics.json` 合并进 `artifacts/round1/round1_v3_main_table.csv`（`scripts/run_round1_v3.py` 的 `write_summary` 已包含上述字段列；**旧 run** 无 API 字段时对应列为空）。

## 3. 验证样例（1 题 smoke）

目录 `artifacts/round1/run_20260411_154646/single_agent/` 为 Session 5 单次 API 调用 smoke：`raw_model_outputs.jsonl` 首行含 `usage_calls`，`metrics.json` 含非零 `api_total_tokens_per_sample`。可与主实验 200 样本 run 区分，按需保留或删除该 `run_*`。

## 4. 主表合并命令（示例）

在已有 `run_*` 下刷新 v3 主表行（不重跑模型，仅读磁盘上的 `metrics.json`）：

```text
python scripts/run_round1_v3.py --config configs/round1_hotpotqa.yaml ^
  --samples-jsonl artifacts/round1/run_20260411_102202/fixed_peer_calibrated/raw_inputs.jsonl ^
  --methods fixed_peer_calibrated,fixed_static_roles,central_orchestrator ^
  --artifacts-root artifacts/round1 ^
  --resume-run-dir artifacts/round1/run_20260411_102202
```

（仅当这些方法目录下已有 `metrics.json` 时才会更新行；**含新 usage 的 metrics 需用当前 runner 代码重新跑完整实验** 后才会填满 API 列。）

## 5. chain-200 主表 vs 实测 API：**方案 B（已写死）**

经与 Session 6 分工对齐，**不**对 `artifacts/round1/run_20260411_102202` 八方法做「仅为回填 API」的整表重跑（**方案 A** 弃用，成本与论文叙事由 7405 承担）。

- **`artifacts/round1/round1_v3_main_table.csv`**：继续表示 **chain、同批 200 题** 的启发式成本与核心指标；**API 列可留空**（旧 `metrics.json` 无 `api_*`）。
- **实测 token / `cost_normalized_f1_api`**：以 **7405 全量 canonical run**（见 `round1_v3_statistics_fullval.md`）及合并产物 **`round1_v3_main_table_fullval.csv`** 为主；论文 §4 须 **脚注说明** chain-200 与 fullval 的分工，避免读者误以为 200 表含实测 token。

全量跑通后，可用 `run_round1_v3.py --merge-summary-only --summary-csv-name round1_v3_main_table_fullval.csv` 维护 fullval 表（见 `round1_v3_statistics_fullval.md` §4）。
