# Round1 v3：自省校准（`fixed_self_calibrated`）vs 同伴校准（`fixed_peer_calibrated`）

本文档固化主文可用的**定性+定量**对照，与 `EMNLP_paper_draft.md` 中「同伴反馈优于纯自省校准」叙事一致。指标字段与 `metrics.json` 一致；`PAR` 即 `premature_accept_rate`（首跳接单且答案 F1<0.5 的样本占比，见 `runner.py`）。

## 1. 脚注：run 目录与样本对齐

| 方法 | 采用目录 | 说明 |
|------|-----------|------|
| `fixed_peer_calibrated` | `artifacts/round1/run_20260411_102202/fixed_peer_calibrated/` | v3 主实验锚点 run（与 `ENGINEER_TODO` 中 `round1_v3_F1_optimization` 一致）。 |
| `fixed_self_calibrated` | `artifacts/round1/run_20260411_132631/fixed_self_calibrated/` | 与 peer **同一条** `raw_inputs.jsonl`（由 `run_round1_v3.py` 显式指定 `run_20260411_102202/.../raw_inputs.jsonl` 复跑），同 `glm-4-flash`、同 `prompts/main_agent_prompt.txt` 版本。 |

汇总表 `artifacts/round1/round1_main_table.csv` 中 `fixed_self_calibrated` 行已与 **`132631` 的 `metrics.json`** 对齐；若历史草稿仍引用同 run 内另一份 self 目录，请以本脚注为准。

## 2. 固定对比表（n=200，chain，HotpotQA validation 切片）

| 方法 | Answer EM | Answer F1 | PAR | mean handoff | token/sample | cost_norm_F1† |
|------|-----------|-----------|-----|--------------|--------------|---------------|
| `fixed_peer_calibrated` | 0.475 | 0.5955 | 0.0 | 1.0 | 480 | 1.240553 |
| `fixed_self_calibrated` | 0.46 | 0.5833 | 0.005 | 1.7266 | 685.2 | 0.851263 |

† `cost_normalized_f1` = `answer_f1 / (token_cost_per_sample / 1000)`（与各方法目录 `metrics.json` 中字段一致）。

**可追溯文件**：

- Peer：`artifacts/round1/run_20260411_102202/fixed_peer_calibrated/metrics.json`
- Self：`artifacts/round1/run_20260411_132631/fixed_self_calibrated/metrics.json`

**摘要**：同伴校准在 F1、过早接单率、平均转发深度与成本归一化 F1 上均优于自省校准；自省路径更易出现**打满链长后由 synthesizer 接单**与**高 self 估计下的首跳接单**。

## 3. 代表性 Case

### Case A — 过早接单（`hotpotqa-0155`）

- **问题**：Where was the world cup hosted that Algeria qualified for the first time into the round of 16?
- **Gold**：Brazil  
- **Peer**（`102202`）：`decomposer` 因 competence 低于阈值 **forward → evidence_seeker**，2 跳后接单，预测 **Brazil**，EM/F1=1。路由摘录：`decision=forward, chosen_target=evidence_seeker` → `evidence_seeker` accept。  
- **Self**（`132631`）：`decomposer` 上 `competence=0.95`，策略 **直接 accept**，预测 **2014 FIFA World Cup**（答非所问），1 跳，F1=0。路由摘录：`fixed_self_calibrated: competence=0.95 >= threshold, accepting`。  

该对照说明：自省信号可把 decomposer 推到过高 self，**绕过**多跳场景下本应发生的转发；同伴门控 + 下游 gold 对齐的更新更易维持「先交给 evidence_seeker」的行为。

### Case B — 专长路由与链长（`hotpotqa-0044`）

- **问题**：Alfred Balk served as the secretary of the Committee on the Employment of Minority Groups in the News Media under which United States Vice President?  
- **Gold**：Nelson Rockefeller  
- **Peer**：`evidence_seeker` 2 跳接单，预测 **Nelson Rockefeller**，F1=1。  
- **Self**：沿链打满 **4 跳** 后由 **`synthesizer` 接单**，预测 **Lyndon B. Johnson**，F1=0。  

在 `parsed_predictions.jsonl` 全量统计上，**自省**侧 `accepted_node=synthesizer` 且 `hop_count≥4` 的样本远多于 **同伴**侧（同伴在 v3 门控下趋向浅层由 evidence_seeker 结束），与 `artifacts/round1_v3_convergence_compare.png` 中「synthesizer 盲目冲高、分工不稳」的曲线叙述一致。

## 4. 复现与校验

```bash
python scripts/validate_logs.py artifacts/round1/run_20260411_102202/fixed_peer_calibrated
python scripts/validate_logs.py artifacts/round1/run_20260411_132631/fixed_self_calibrated
```

专长对比图（若需重绘）：

```bash
python scripts/plot_dynamics.py --snapshots artifacts/round1/run_20260411_102202/fixed_peer_calibrated/competence_snapshots.jsonl:peer artifacts/round1/run_20260411_132631/fixed_self_calibrated/competence_snapshots.jsonl:self --out artifacts/round1_v3_convergence_compare.png
```
