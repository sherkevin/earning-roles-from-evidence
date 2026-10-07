# 正文实际页数修正与写作压缩 — 2026-10-07

状态：`PARTIAL`；`goal_change_requested=false`。对应 ER-G5；不改变 ER-G1–ER-G4。

## 目的与衡量标准

用户要求正文恰好八页，参考文献不计入，并保持完整论文框架、三张图和实验矩阵。
本轮检查的是实际包含正文的页面，而不是简单计算参考文献起始页减一。成功标准为：
正文最后一页为第 8 页，讨论与结论全部在这八页内，第 9 页起只有参考文献；官方
模板不变，引用全部解析，没有 overfull boxes，并逐页检查布局。

## 发现与保留的失败

旧检查器直接用 `References` 的起始页减一，漏掉了同一页上方的讨论和结论。
因此 v1 和此前被指为 current 的 `paper_figure_refresh_v2_20261006` 实际均有九页正文，
之前的“正文八页”结论错误。本轮没有据此推断所有历史 PDF 都九页；其他旧回执中
依赖相同公式的精确页数结论应视为待重新核验。

- [v1 原始 PDF](../../../artifacts/aamas2027/terminal_measurement_20261007_v1/main.pdf)
  与原始 manifest/verification 保留；[追加修正](../../../artifacts/aamas2027/terminal_measurement_20261007_v1/correction.json)
  明确标记拒绝晋升，实际正文 9 页。
- 删除内部 result-entry 表、重复执行清单并压缩讨论后的
  [v2](../../../artifacts/aamas2027/terminal_measurement_20261007_v2/main.pdf)
  仍有九页正文，仅结论末尾约 60 多个词溢出；新检查器确实返回失败。
- v3 进一步删除与方法章节重复的 phase-rule 段落。历史失败文件没有覆盖。

[检查器修复](../../../scripts/build_aamas2027.py)按文字位置识别参考文献页上是否仍有
正文，排除页眉页脚；[三项 PDF 控制](../../../tests/test_aamas_content_page_count.py)
覆盖正文/引用混排、纯引用页和无参考文献的文档。原始复核、运行前 config 与测试输出
见[检查日志](../../../experiments/logs/aamas2027_content_page_count_20261007_v1/result.json)。
这是版式回归，不是实验效果测试，使用 0 API、0 GPU。

## 写作内容与审查

保留问题、方法、公式、全部实验矩阵行、结果占位、三张图和反驳条件。删掉的是
内部重复检查清单和过长的开发执行叙事；没有通过缩字体、改页边距或改官方 class
满足页数。补入测量上的必要区分：producer 合规与终端可用分开，no-update 同样
接受终端评估；assignment credit 的资格不等于结果进入分母的资格。

独立 Codex `gpt-6-sol` 协作者复核当前英/中文差异，没有发现因压缩丢失的科学不变量
或新增无证据主张：信息边界、时序、UNKNOWN、完整成本与一次性更新仍在方法节。
本轮修改的中文段落同步到 [FORMAL_PAPER_ZH.md](../../paper/aamas2027/FORMAL_PAPER_ZH.md)。
本轮复用现有工作树图形输入，并在各版本的 source snapshot 中保存实际构建用图；
未修改或接管图形资产的在途工作。公开复现应使用对应 snapshot 中的完整 source，
不能将不同版本的正文与图形混用。

## 最终构建

[v3 当前内部 PDF](../../../artifacts/aamas2027/terminal_measurement_20261007_v3/main.pdf)
已通过编译和目视核验：总计 9 页，正文恰好 8 页，参考文献从第 9 页开始且该页不含正文。
第 8 页完整容纳讨论与结论；正文全页缩略图和第 8/9 页大图已查看。三张图、五张表
及完整实验矩阵保留；22 条参考文献引用解析，0 overfull。官方 class/bst/by.pdf 摘要未变。
既有 `ifx` 模板兼容警告仍记录，未被解释为科学或格式全部合格。

PDF SHA-256：`8cc5f0adcb25488a3622e5e4c349ed2ccc618259093f5e34486372e42f662d40`。
[构建前配置与日志](../../../experiments/logs/n03_terminal_measurement_paper_20261007_v3/config.json)、
[编译核验](../../../artifacts/aamas2027/terminal_measurement_20261007_v3/verification.json)、
[完整源文件快照与目视记录](../../../artifacts/aamas2027/terminal_measurement_20261007_v3/manifest.json)
均已保存。此处晋升只针对当前内部稿的正文页数，不代表三份科学审核通过或允许投稿。

## 对 Goal 的回看

修正的是论文验收测量和叙事重复，不是降低页数要求或科学要求。
尚无新的角色学习、稳定性或实时训练效果可以填入正文。最终训练方法、两个合格
root、强基线独立 histories 与确认结果仍未完成；科学投稿 gate 保持关闭。
本轮科学优先级另见[回归主线报告](20261007_scientific_next_step_reconciliation.md)。
