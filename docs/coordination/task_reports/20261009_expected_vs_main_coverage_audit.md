# Expected v5 与当前主 PDF 的完整性复核

日期：2026-10-09。目的：核查全部实验承诺是否都有可见的预期数值，不能只检查表号、行数。

## 结论

**内容行列对应，表号已过期，完整实验覆盖未通过。** Table 7 的 8 行与 Table 8 的 4 格都有预期数值；
Table 5 的 9 个实验行都存在，但部分行只填写代表性指标。
之前 v5 的“对应全部实验矩阵”表述过宽。已有算术审核仍成立，不足的是覆盖审核粒度。
本次不修改数字、不改正文、不降低 Goal，也不将规划区间改称实测置信区间。

## 核查对象与方法

- 主 PDF：`artifacts/aamas2027/main.pdf`，SHA256 `78bef256a9a97f89c7dd52826d6b176574d1ef9645d9685526d9de2d3b054bc7`。
- Expected PDF：`artifacts/aamas2027/expected_experiment_matrix.pdf`，SHA256 `2756d7faa76c0ea2379f08a26ef17e7dd0ca0f24ffac4da42a5f794c49feea05`。
- 直接抽取两份 PDF，复核相应 LaTeX 和 expected JSON；渲染目视检查主稿第 7 页与 expected 第 2 页。
- 独立 Codex gpt-6-sol 审查员 `expected_history_audit` 重新核查实际 PDF，未沿用旧 pass 结论。
- 主稿 Table 5 在第 7 页；Table 7、8 在第 8 页。Expected 对应第 2 页及第 1 页。

## 本轮期间的主版变化

核查开始时主稿为 `3df34bd4…`，表号 4/6/7；最终校验检测到并行写作已将主稿升级为
`full_body_20261009_v4`（`32e69ea4…`），增加事件顺序表后目标表号变为 **5/7/8**。
独立审查员重新核对后确认三个结果表的 9/8/4 行内容未变。Expected PDF 仍印旧编号，
且其来源哈希仍指旧稿，因此当前不仅指标不全，表号映射也过期。原来源哈希保留为历史，
登记过期状态及最新核查哈希；不能只改哈希让未更新的 PDF 看起来已同步。

随后标题更新再次发布 `short_title_20261009_v1`（`78bef256…`）；保存该 PDF 快照并重新读取，目标表号仍为 5/7/8，三表行列与漏项结论不变。下文按此最终快照登记。

## 表内逐行覆盖

| 主稿对象 | Expected 覆盖 | 判定 |
|---|---|---|
| Table 7：8 个主要结果端点、两方法和差值 | 所列单元都有数值；区间明确为 planning range | 规划数值覆盖；不是实测 CI |
| Table 8：4 格效用与成本 | 4 格齐全，主方法与 Table 7 一致 | 规划数值覆盖；不是实测 CI |
| Table 5 RQ1-I | 三方法 Brier、log loss、ECE | 所列摘要指标覆盖 |
| Table 5 RQ1-II | 两方法 Brier、跨根 Brier、退化差 | 所列摘要指标覆盖 |
| Table 5 RQ2-I | 两臂 change、quality、adoption、rework | 所列摘要指标覆盖 |
| Table 5 RQ2-II | 两臂 utility、cost | 所列摘要指标覆盖 |
| Table 5 RQ2-III | 稳定场景两臂 utility、max share、min propensity；稀疏效用 | 所列摘要指标覆盖 |
| Table 5 RQ3-I | 4 个常态 payoff、RARE update p50/p95/state、两方法高负荷 payoff/p95 | **部分**：每个 updater 的性能和时延/状态未完整展示 |
| Table 5 RQ3-II | 两臂 forgetting、recovery、backlog、agreement | 所列摘要指标覆盖；正文更广的 drift/版本情景仍未覆盖 |
| Table 5 RQ4-I | 混合总体 UNKNOWN/coverage/FA/precision/no-op；脚注分层 coverage/FA | **部分**：完整分层及 scorer/版本失败情景、发布和有效更新覆盖率未给齐 |
| Table 5 RQ4-II | 部分消融 utility、去 gate 的 FA、interaction | **部分**：消融 cost、单独 delay-handling、selected-only 等未给齐 |

## 漏项来源：排版遗漏与尚未定义不能混为一谈

**JSON 已有但 PDF 没有完整展示：**

- Contextual、RLS、SGD、periodic refit 等常态 payoff、update p50/p95、state、backlog；PDF 将 updater 压缩成一个代表值。
- 全部已有消融的 cost、quality 与 without correction/replay 的结果；PDF 仅保留部分 utility。
- 四格消融各臂 adoption/rework；主稿 RQ2 结果段需要的 full-arm rework .21 仅在 JSON。

**预期 PDF/JSON 仍无完整对应，必须补设计或依据：**

- 主稿 Table 4 的 closest published adapter 没有确定名称和对应结果；在线 logistic 对照也未独立列数值。不能给未定义实现随意填数。
- 单独关闭 delay handling 与关闭 delayed updater 是不同干预，不能用同一个 .448 混作两项；selected-only 约束消融未独立定义。
- publish/read/update 全链 p50/p95、service lag、replay time、完整服务资源/成本；硬件预算和 selector bytes 不能替代实测内存与成本。
- 观察发布率、归因通过率、合法更新率及各自分母；mutation UNKNOWN .498 不能替代在线 outcome 缺失率。
- 版本替换、乱序反馈、重复/修正、scorer failure 的独立结果；峰值和均值遗忘未分开。
- 正文声明的 AUC（有定义时）、propensity-weighted future quality、跨 source producer 的 later-owner 转移、count-only 控制尚无完整数值映射。
- 按 root 的结果、ITT/per-protocol 数量与不确定性/异质性报告仍不完整。

Table 1/2/3/4/6 属于定位、事件顺序、状态、基线、分母定义表，不应硬填结果。
但是 Table 4 和正文承诺的实验仍须映射到某个结果单元；“它不是结果表”不能豁免其基线覆盖。

## 修复顺序与衡量方式

1. 先在新版本中同步表号 5/7/8，再从已有 JSON 补齐每个 baseline/ablation 的可见数值，以 Table 5 的分面或配套明细表达，保持 Table 7/7 不变。
2. 对真正缺失的条件逐一明确比较臂、样本群、指标/单位、合理值依据；不为凑齐版面批量生成数字。
3. 建立 `主稿承诺 → 比较臂 → 指标 → expected 数值位置` 的逐项清单。不能用 9/9 行存在充当全部实验覆盖。
4. 重新独立审核全覆盖与数值关系，通过后才能把覆盖状态升级。当前唯一预期版仍为 v5，但标记为部分覆盖、待补齐。

独立审查结论：三张表结构对应，Table 7/7 显示单元有规划值；Table 5 及正文实验承诺未全部覆盖。
对 Goal 的贡献是明确了真实漏项，未完成的仍是完整对标交付和真实实验验证。
可复用资产是 v5 已核验的数值、分母定义和逐表编号；本次没有运行推理 API、benchmark 或 GPU 实验。
