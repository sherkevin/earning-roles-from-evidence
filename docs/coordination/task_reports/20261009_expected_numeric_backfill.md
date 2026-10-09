# 数值回填候选：保持正文文字不变

## 最终更新：v2 通过并同步主版

用户随后明确允许微调表格恢复 8 页、正文文字不变，已记 ADR 0054。
v2 只调整 Table 5 的字号（7.5 pt）、行高、列宽和列间距，恢复 **8 页正文 + 2 页参考文献**。
独立复核后撤回不明确的 backlog p95、max-share、min-propensity 填值。
82 个原始占位槽中，50 个完整填写，2 个仅填写已确定的子指标，30 个原样保留；
计入部分填写的子指标空项，PDF 共保留 33 个 xx。
其余源文经重建校验一致；独立 Codex 审查通过，0 overfull、0 未解析引用。
当前主 PDF 同步为 `artifacts/aamas2027/expected_backfill_20261009_v2/main.pdf` 的
带水印预期预览。正式实证源文 `article/aamas2027/main.tex` 未混入预期结果。
当前主 PDF 的可复现源文为版本目录 `source/main.tex`，在 master 登记中明确记录。
保留缺值和实测 CI 的 xx，未声称已补齐全部实验，未关闭科学 gate。
下文保留 v1 初次构建的过程记录，不代表最终主版状态。

## 用户要求与范围

把现有 expected 数值回填主 PDF 的表格和正文 xx；只替换数字，不改文字。
预期数值不能变成实测结果，主观规划区间不能充作正文标注的实测 95% CI。
本轮生成明确标为 EXPECTED -- NOT OBSERVED 的内部预览候选。

## 已完成

- 固定当前主版 `78bef256a9a97f89c7dd52826d6b176574d1ef9645d9685526d9de2d3b054bc7`，保存原 PDF、源文及登记文件。
- 原稿 82 个 xx 中，53 处存在明确对应值，已逐项替换；29 处保留。
- 替换内容只包含数字、符号和数值分组标点；以原文区间重建候选源文，确认 xx 区间外逐字节不变。
- 没有把规划范围填进 95% CI，没有把 mutation UNKNOWN 当在线 outcome 缺失率，也没有补造服务成本等缺值。
- 作者、标题、段落、表头、图、公式、参考文献及模板源文件均未主动修改。
- 数值替换在隔离的构建源文中进行，实证稿 `article/aamas2027/main.tex` 保留；PDF 增加可见的预期值标识。
- 编译成功，无 overfull、无未解析引用；已渲染查看第 1、7、8 页，全部页面有预期标识。

## 当前冲突与主版状态

替换较长数字后自然重排为 **9 页正文 + 2 页参考文献**，原主版为 8 + 2 页。
不能同时声称“完全不改其余内容”和“恢复原 8 页排版”。尚未压缩字体、行距或改写正文。
已就“接受预期预览暂为 9 页”与“允许仅调整表格排版恢复 8 页”向用户提出选择。
选择返回前，**不替换 canonical main.pdf**，候选已在 Preview 打开。

## 可复核产物

- 候选：`artifacts/aamas2027/expected_backfill_20261009_v1/main.pdf`
- 每处替换及保留理由：同目录 `replacement_map.json`
- 数值来源快照：同目录 `expected_values_snapshot.json`
- 文字不变、编译和页数记录：同目录 `build_config.json`、`verification.json`
- 原始备份：同目录 `before_main.pdf`、`before_main.tex`、`before_main_pdf_master.json`
- 可复现脚本：`scripts/backfill_expected_main_20261009.py`

## 与 Goal 对比

已完成有来源的数值回填预览，没有完成全部数值识别、8 页限制或真实实验验收。
没有运行新的推理 API、benchmark 或 GPU 实验，没有降低科学标准。
可复用的是逐占位符的映射和可逆源文差异；后续真实结果可沿相同位置替换，不能按预期挑选实测结果。
