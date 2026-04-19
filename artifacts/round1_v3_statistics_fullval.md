# Round1 v3 — 全量验证（7405）统计与主表

## 0. 当前状态（必读）

| 项目 | 状态 |
|------|------|
| **全量 7405×三主** | **进行中（若你正在本机后台跑）**：最近一次启动目录示例 **`artifacts/round1/run_20260412_021010/`**（以你终端 `New run dir` 为准）。**历史卡点**（10061）已通过 `llm_client` 代理策略/网络修复消除；若仍失败请查密钥与出网。 |
| **Pilot（n=3）** | 曾用于验证 `validate_logs` / bootstrap / merge 管线；**目录可能已从工作区删除**，不以固定 `run_*` 路径为准。Pilot 当时同样受 API 失败影响，`api_*` 为 0。 |
| **占位 CSV** | `round1_v3_main_table_fullval.csv`、`round1_v3_paired_stats_fullval.csv` 若存在小样本或空表数据，**7405 全量成功后务必用同文件名覆盖**。 |
| **一键后处理** | 全量跑完后：见仓库根目录 **`scripts/post_fullval_chain.ps1`**（传入 `RUN_FULLVAL` 相对路径）。 |

## 1. 启动全量 7405×三主（COORDINATION 约定）

输入：`artifacts/seed/hotpotqa_validation_full.jsonl`（7405 行）。三主方法：`fixed_peer_calibrated`、`fixed_static_roles`、`fixed_self_claim`。配置：`configs/round1_hotpotqa.yaml`（`topology: chain`）。

```text
cd /d d:\Codes\idea04

python scripts/run_round1_v3.py ^
  --config configs/round1_hotpotqa.yaml ^
  --samples-jsonl artifacts/seed/hotpotqa_validation_full.jsonl ^
  --methods fixed_peer_calibrated,fixed_static_roles,fixed_self_claim ^
  --artifacts-root artifacts/round1 ^
  --no-write-summary
```

记下输出的 **`New run dir: ...\run_YYYYMMDD_HHMMSS`**，下文记为 **`RUN_FULLVAL`**。全量耗时可数小时量级，建议后台执行并保留日志。

**一键后处理（推荐）**：全量三个子目录都产出 `metrics.json` 后，在仓库根目录执行：

```text
.\scripts\post_fullval_chain.ps1 -RunDir artifacts\round1\run_YYYYMMDD_HHMMSS
```

（等价于依次执行下面 §2–§4；路径按本机调整。）

## 2. 验收（每方法）

```text
python scripts/validate_logs.py RUN_FULLVAL/fixed_peer_calibrated
python scripts/validate_logs.py RUN_FULLVAL/fixed_static_roles
python scripts/validate_logs.py RUN_FULLVAL/fixed_self_claim
```

（或 `python scripts/validate_logs.py RUN_FULLVAL --all-methods`。）

## 3. 配对统计（baseline = peer）

```text
python scripts/compute_paired_bootstrap.py ^
  --run-dir RUN_FULLVAL ^
  --baseline fixed_peer_calibrated ^
  --compare fixed_static_roles fixed_self_claim ^
  --metric answer_f1 ^
  --n-bootstrap 10000 ^
  --seed 42 ^
  --out-csv artifacts/round1_v3_paired_stats_fullval.csv
```

（若日后扩展对照方法，在 `--compare` 中追加。）

## 4. 合并全量主表 CSV（不写回 chain-200 主表）

```text
python scripts/run_round1_v3.py ^
  --merge-summary-only ^
  --resume-run-dir RUN_FULLVAL ^
  --methods fixed_peer_calibrated,fixed_static_roles,fixed_self_claim ^
  --artifacts-root artifacts/round1 ^
  --summary-csv-name round1_v3_main_table_fullval.csv ^
  --no-canonical-self-override
```

说明：`--no-canonical-self-override` 避免把 `132631` 的 `fixed_self_calibrated` 注入 **仅含三主** 的全量表。

## 5. 全量 n=7405 结果（最终）

**Run dir**: `artifacts/round1/run_20260413_075132`  
**Validate**: `validate_logs.py --all-methods` → 三方法均 **[OK]**, 7405 samples, 100% coverage  
**Date**: 2026-04-14

### 5.1 主表摘要（`round1_v3_main_table_fullval.csv`）

| method | EM | F1 | MHC | PAR | token/sample | sample_count |
|--------|----|----|-----|-----|-------------|-------------|
| `fixed_static_roles` | **0.4455** | **0.5906** | 1.6655 | 0.0 | 631.2 | 7405 |
| `fixed_self_claim` | 0.4224 | 0.5691 | 2.0 | 0.0 | 840 | 7405 |
| `fixed_peer_calibrated` | 0.4231 | 0.5693 | 2.0 | 0.0 | 840 | 7405 |

MHC = mean_handoff_count，PAR = premature_accept_rate。

### 5.2 配对统计（`round1_v3_paired_stats_fullval.csv`，baseline = peer_calibrated）

| compare | n_tasks | n_non_tie | mean(baseline − compare) | 95% CI | sign_test p | 胜/负 |
|---------|---------|-----------|--------------------------|--------|-------------|-------|
| `fixed_static_roles` | 7405 | 984 | **−0.0213** | [−0.0273, −0.0155] | **p≈0** | peer 392 / static 592 |
| `fixed_self_claim` | 7405 | 48 | +0.0002 | [−0.0009, +0.0012] | p=0.885 | peer 23 / self 25 |

### 5.3 关键叙事

- **static_roles 显著优于 peer_calibrated**（F1 差 0.021，bootstrap CI 不跨零，p≈0）。n=7405 下此差异稳健，与 n=200 pilot 结论一致。
- **peer_calibrated 与 self_claim 无显著差异**（几乎无 non-tie 样本，sign_test p=0.885）：在全量数据上两者 F1 几乎等价（0.5693 vs 0.5691）。
- **cost-normalized F1**：static_roles（0.936）远高于 peer/self_claim（~0.678），因为 peer 与 self_claim 的 token 消耗均为 static 的 1.33×。
- **PAR=0 for all**：全量下没有出现过早接单，decomposer 多跳强制门控（`_is_multihop_question`）稳定生效。
- **论文叙事建议**：F1 层面 peer_calibrated 未能超越 static baseline；论文主要论据集中于 **PAR 差异**（chain-200 中 0.0 vs 1.0）与 **路径分歧率 48%**（见 `round1_v3_statistics.md`），而非 F1 绝对值。

## 6. 与 `round1_v3_statistics.md` 的关系

子集（200）配对结论见 **`round1_v3_statistics.md`**（含 §4）。**全量 7405** 的配对与叙事以 **本文档 + `round1_v3_paired_stats_fullval.csv`** 为准；可在 `round1_v3_statistics.md` 增加 **§5** 一句链回本文。
