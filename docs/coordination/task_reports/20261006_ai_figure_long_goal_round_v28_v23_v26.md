# AI figure long-goal round — v28/v23/v26 (2026-10-06)

状态：`PARTIAL`（完成一轮三图 AI 重绘；尚未通过最终生产和纸面验收）

## 本任务对应的 Goal 标准

本任务对应 `GOAL.md` 的 ER-G1（故事线必须形成可读、可审计的论文因果链）以及论文图计划的
一句话/30 秒/版式/版本测试。它只验证图形表达，不证明 benchmark、baseline、在线更新或科学效果。
Goal 没有修改，`goal_change_requested=false`。

## 冻结内容与真实操作

运行前冻结了当前正文候选 v27/v22/v24、三张图的语义顺序、Figure Plan v2 的颜色和责任边界，
并读取本地 topconf-paper-figure-gallery 的 CollabLLM、VideoPoet、DPO 样例。三次输出均由 Codex
内置 `image_gen` 生成，模型标识由服务端隐藏；没有把结果标注为 image2.5。每张图都保存完整
prompt、输入参考路径、原始生成输出路径、项目内副本和 SHA-256，详细 receipt 在
`experiments/logs/figure_ai_long_goal_round_20261006/receipt.json`。

## 本轮候选

| 图 | 候选 | 本轮改善 | 当前判断 |
|---|---|---|---|
| Figure 1 | v28 | 去除巨型标题和卡片，改成单一水平叙事主轴；使用 peer/artifact/judgment/evidence/read-cut/seal/outcome glyph | 三图中最接近样例库的开放叙事，但 peer token 仍带轻微头像化；保留候选 |
| Figure 2 | v23 | 保留三泳道和 BEFORE SELECTION/AFTER SEAL，统一为 document/speech/gate/ledger/read-cut/seal glyph | 语义最清楚，仍需纸面小尺寸检查；保留候选 |
| Figure 3 | v26（v25 保留为中间版） | 保留 tracks/policies/endpoints，去掉 award/gear/clock，改用 ledger/seal/pulse/gate glyph | 与前两图更统一，但左侧 peer token 仍有人形倾向；保留候选 |

## 已满足、部分满足、未满足

- **已满足**：三图都完成 AI 重绘；历史版本和完整 prompt 未覆盖；语义顺序与故事线保持一致；
  三图开始共享同一套开放式构图、细线、颜色和对象化 glyph。
- **部分满足**：图形叙事和样例库风格接近度明显改善，但尚未完成独立审查；生成图仍是栅格输出；
  Figure 1/3 的 peer glyph 仍可能被审稿人看作通用 avatar。
- **未满足**：TrueType/矢量生产门和最终打印生产门；AI 栅格输出仍不能被称为最终投稿资产。

## 版心与灰度复核

将 v28/v23/v26 的候选 PDF 临时放入正文图位后，在隔离目录
`article/aamas2027/build/figure_set_v28_v23_v26_fresh_20261006/` 构建真实论文：10 页总页数、
正文内容 8 页、参考文献从第 9 页开始、引用解析、0 overfull；verification SHA-256 为
`fecbab50d546f562d462ccbbefa4db8e517bfb757658f31a7a2c188d73cccb27`。候选图以 1050 px 宽度
模拟约 7 英寸版心，并生成 Generic Gray Gamma 2.2 灰度副本；三张图的阶段标签、箭头、时间边界、
policy rows 和 endpoint labels 仍可辨认。纸面截图保存在本目录对应的
`paper_scale_fresh/`、`paper_scale_candidates/` 和 `grayscale/` 中。

基于这组证据，v28/v23/v26 晋升为当前正文候选；v27/v22/v24 仍保留为回退版本。这个晋升不关闭
最终生产门，也不改变科学 submission gate。

## 下一步

1. 对晋升后的 v28/v23/v26 继续做矢量/嵌入字体生产审查，不能用当前栅格 PDF 代替该门。
2. 若 peer glyph 或任何图形仍显得通用，重写完整 prompt，继续生成 v29/v24/v27；不得只做局部
   掩盖式修补。
3. 生产门关闭后再次构建论文，核对 caption、灰度和图文语义；历史版本继续保留。

失败、栅格格式或尚未通过审查都不会导致 Goal 降级。
