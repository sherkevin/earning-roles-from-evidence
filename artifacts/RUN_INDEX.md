# RUN_INDEX — `artifacts/` 下所有 `run_*` 目录的状态总表

> 每个 run_* 一行；任何新跑 / 归档 / 损坏必须同步更新本文件。
> 创建日期：2026-04-19。维护者：科学家。

---

## 0. 状态标签

| 标签 | 含义 | 论文是否引用 |
|---|---|---|
| ⭐ **canonical** | 当前论文主表 / 主分析直接来源 | 是 |
| 📦 **archived** | 早期阶段证据，论文降级为 guidance-only / appendix | 部分 |
| 🔬 **forensic** | 用作故障 / 损坏 forensic evidence，不能删除 | 不是 |
| 🟡 **dead** | 0 MB / 失败 / 被取代 / 早已被覆盖；可考虑清理 | 否 |
| 🧪 **smoke / reference** | 一次性 smoke 或 backbone / provider check | 否 |

---

## 1. mainline gpt-4.1-mini 包

### `round2_gpt41mini/`（chain-200，gpt-4.1-mini）

| run dir | 大小 | 子方法数 | 状态 | 备注 |
|---|---:|---:|---|---|
| `run_20260414_115739` | 20.6 MB | 3 | ⭐ **canonical** | **当前论文 §4.2 主表来源**：peer / static / self_claim 三方法 200 样本，validated [OK]。Coordinator note 在 `round2_gpt41mini_coordinator_note.md` |
| `run_20260414_115609` | 7.5 MB | 1 | 📦 archived | Agent2 Session6 早期单方法启动，被 _115739 取代 |
| `run_20260414_115614` | 13.2 MB | 2 | 📦 archived | Agent1 Session6 重复尝试，被 _115739 取代 |
| `run_20260414_120253` | 7.5 MB | 1 | 🟡 dead | 单方法残留 |
| `run_20260414_120528` | 7.5 MB | 1 | 🟡 dead | 单方法残留 |

### `round2_gpt41mini_fullval/`（chain-7405，gpt-4.1-mini）

| run dir | 大小 | 状态 | 备注 |
|---|---:|---|---|
| `run_20260414_135408` | (大) | ⚠ **partial valid + 🔬 forensic** | **peer_calibrated 有效**（F1=0.7703，n=7405，写入论文 §4.3）；**static_roles + self_claim 被 model drift 污染**（kuaipao.ai 静默路由到 gpt-5.1）。详见 `round2_gpt41mini_fullval/fullval_corruption_triage_note.md`。**绝对不可删除** |

---

## 2. archived Stage-1 GLM 包

### `round1/`（GLM chain）

| run dir | 大小 | 子方法数 | 状态 | 备注 |
|---|---:|---:|---|---|
| `run_20260413_075132` | **762.6 MB** | 3 | 📦 **archived canonical (GLM fullval)** | **GLM 7405 全量主表来源**（写入 `round1_v3_main_table_fullval.csv` + `round1_v3_statistics_fullval.md` §5）。EMNLP 主线已切到 gpt-4.1-mini，本包降级为 guidance-only |
| `run_20260411_102202` | 35 MB | 8 | 📦 **archived canonical (GLM 200)** | **GLM chain-200 八方法主表来源**（含 single_agent / central_orchestrator / fixed_random_forward 全 baseline）。论文 GLM appendix 唯一引用 |
| `run_20260411_132631` | 5.7 MB | 1 | 📦 archived | `fixed_self_calibrated` 同 jsonl 补跑，写入 main_table 时强制覆盖 |
| `run_20260413_051931` | 478.9 MB | 3 | 📦 archived (abandoned partial) | 早期 fullval 启动，因 ZHIPU_API_KEY 未设置卡死，被 _075132 取代 |
| `run_20260411_091922` | 13 MB | 3 | 📦 archived | round1 200 样本 v2 |
| `run_20260411_063741` | 7.5 MB | 3 | 📦 archived | round1 100 样本平行 |
| `run_20260411_063319` | 7.5 MB | 3 | 📦 archived | round1 100 样本备用 |
| `run_20260411_053608` | 3.1 MB | 3 | 📦 archived | round1 50 样本起步 |
| `run_20260411_063219` | 0.3 MB | 1 | 🟡 dead | 单方法残留 |
| `run_20260411_132001` | 0 MB | 1 | 🟡 dead | empty |
| `run_20260411_154646` | 0 MB | 1 | 🧪 smoke | usage 字段 1-sample smoke |
| `run_20260411_155306` | 0 MB | 1 | 🟡 dead | empty |
| `run_20260411_155418` | 0 MB | 1 | 🟡 dead | empty |
| `run_20260412_013734` | 0 MB | 1 | 🟡 dead | empty |
| `run_20260412_014823` | 0 MB | 1 | 🟡 dead | empty |
| `run_20260412_021010` | 0 MB | 1 | 🟡 dead | fullval 启动失败残壳 |
| `run_20260413_074122` | 0 MB | 1 | 🟡 dead | empty |

### `round1_star/`（GLM star）

| run dir | 大小 | 状态 | 备注 |
|---|---:|---|---|
| `run_20260413_055929` | (~7 MB) | 📦 **archived canonical (GLM star)** | star × 三方法 200 样本，**论文 appendix 唯一 star 证据来源**。结论：star 拓扑下三方法表现塌缩到一致 |
| `run_20260413_052853` | (~7 MB) | 📦 archived (early try) | 被 _055929 取代 |

### `round1_gpt41mini_baseline/`

| run dir | 状态 | 备注 |
|---|---|---|
| `run_20260414_083033` | 📦 archived | Session 4 早期 gpt-4.1-mini 单方法 baseline，已被 round2_gpt41mini 取代 |

---

## 3. 机制 / 敏感性 ablation（GLM）

| 目录 | run dir | 状态 | 备注 |
|---|---|---|---|
| `round1_ablation_baseline/` | `run_20260413_060223` | 📦 archived | refreshed v3 baseline，F1=0.5597，写入 `round1_v3_mechanism_ablations.md` |
| `round1_ablation_baseline/` | `run_20260413_073844` | 🟡 **dead (invalid)** | ZHIPU_API_KEY 未设置导致全 0；Agent3 Session1 已标注勿用 |
| `round1_ablation_evidence/` | `run_20260413_052853` | 📦 archived | 放大 evidence window，F1=0.5819 |
| `round1_ablation_nogate/` | `run_20260413_053007` | 📦 archived | 关闭 decomposer 门控 |
| `round1_ablation_notcpb/` | `run_20260413_052853` | 📦 archived | 关闭 TCPB 终局更新 |
| `round1_sensitivity_margin_low/` | `run_20260414_062134` | 📦 archived | accept_margin=0.01 |
| `round1_sensitivity_margin_high/` | `run_20260414_082332` | 📦 archived | accept_margin=0.04 |
| `round1_sensitivity_gate_low/` | `run_20260414_083023` | 📦 archived | gate_threshold=0.80 |
| `round1_sensitivity_gate_high_glm/` | `run_20260414_105024` | 📦 archived | **正确的 GLM gate_high run** |
| `round1_sensitivity_gate_high/` | `run_20260414_102629` | 🧪 reference (accidental) | 因 LLM_BACKEND=oversea 残留导致**实际跑了 gpt-4.1-mini**，作为 bonus 数据点保留 |

---

## 4. runtime / provider 验证

| 目录 | run dir | 状态 | 备注 |
|---|---|---|---|
| `model_backbone_check/` | `run_20260414_062110` | 🧪 reference | GLM smoke (10 样本) |
| `model_backbone_check/` | `run_20260414_062253` | 🧪 reference | gpt-4.1-mini smoke (10 样本)，证明 backbone 控制可控 |
| `provider_fallback_check/` | `run_20260414_135133` | 🧪 reference | NVIDIA llama-3.3-70b 低并发 smoke，OK |
| `provider_fallback_check/` | `run_20260414_135402` | 🧪 reference | NVIDIA 4 worker 压力测试，429 burst |
| `provider_fallback_check/` | `run_20260414_135536` | 🟡 dead | Agent3 重复 NVIDIA 调用，F1=0 (rate limit) |
| `runtime_integrity_guard/` | `run_20260415_030656` | 🔬 forensic | guard 触发 forensic |
| `runtime_integrity_guard/` | `run_20260415_030738` | 🧪 reference | GLM-5.1 positive smoke (5 样本) |
| `runtime_guard_smoke/` | `run_20260415_030923` | 🧪 reference | guard 正向 smoke |

---

## 5. round0 历史冒烟

| 目录 | run 数 | 大小 | 状态 |
|---|---:|---:|---|
| `round0/` | 9 | 7.3 MB | 📦 archived（短文阶段最早 50 样本冒烟，全部已被 round1 取代） |

---

## 6. smoke 残留（可考虑批量清理）

| 目录 | 大小 | 状态 |
|---|---:|---|
| `round1_smoke_live/run_20260413_051819` | 0 MB | 🟡 dead |
| `round1_smoke_new/run_20260413_051725` | 0.1 MB | 🟡 dead |
| `round1_smoke_parallel/run_20260413_125110` | 0 MB | 🟡 dead |
| `round2/` (空目录) | 0 MB | 🟡 dead (placeholder ghost) |

---

## 7. 论文当前主表的"四个数字源"快速查找

| 数字 | 来源 run dir | csv 文件 |
|---|---|---|
| **chain-200 主表 (gpt-4.1-mini)** | `round2_gpt41mini/run_20260414_115739/` | `round2_gpt41mini/round2_gpt41mini_main_table.csv` |
| **fullval-7405 peer_calibrated 一行 (gpt-4.1-mini)** | `round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/` | `metrics.json` 直接读 |
| **fullval-7405 三方法 (GLM, archived)** | `round1/run_20260413_075132/` | `round1/round1_v3_main_table_fullval.csv` |
| **chain-200 八方法 (GLM, archived appendix)** | `round1/run_20260411_102202/` | `round1/round1_v3_main_table.csv` |
| **star-200 三方法 (GLM, robustness appendix)** | `round1_star/run_20260413_055929/` | `round1_star/round1_star_main_table.csv` |

---

## 8. 清理候选（汇总到 `SCIENTIST_TODO.md § 决策池`）

| 类别 | 数量 | 总大小 | 备注 |
|---|---:|---:|---|
| `🟡 dead` empty / 残壳 run | 14 个 | < 1 MB | 删除影响零，但建议**论文 camera-ready 后**再清 |
| `🟡 dead` smoke 残留目录 | 4 个 | < 0.5 MB | 同上 |
| `📦 archived` GLM 大 run（保留为 sanity comparison） | 2 个 | **1.24 GB** | **不要删除**，论文 appendix 仍引用 |
| `🔬 forensic` 损坏 run | 1 个 | (大) | **永远不要删除** |

详见 `SCIENTIST_TODO.md` 中 `U-005-cleanup-decide`。
