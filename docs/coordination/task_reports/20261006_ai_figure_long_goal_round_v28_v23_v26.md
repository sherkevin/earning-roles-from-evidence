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
| Figure 3 | v26 | 保留 tracks/policies/endpoints，去掉 award/gear/clock，改用 ledger/seal/pulse/gate glyph | 与前两图更统一，但左侧 peer token 仍有人形倾向；保留候选 |

## 已满足、部分满足、未满足

- **已满足**：三图都完成 AI 重绘；历史版本和完整 prompt 未覆盖；语义顺序与故事线保持一致；
  三图开始共享同一套开放式构图、细线、颜色和对象化 glyph。
- **部分满足**：图形叙事和样例库风格接近度明显改善，但尚未完成独立审查；生成图仍是栅格输出；
  Figure 1/3 的 peer glyph 仍可能被审稿人看作通用 avatar。
- **未满足**：TrueType/矢量生产门、正文版心最终核验、灰度和打印核验；因此本轮没有晋升正文资产。

## 下一步

1. 先对 v28/v23/v26 做同一套纸面审查：7 英寸版心、最小字高、灰度、箭头方向、标签精度。
2. 若 peer glyph 或任何图形仍显得通用，重写完整 prompt，继续生成 v29/v24/v27；不得只做局部
   掩盖式修补。
3. 通过视觉审查后再把候选转换为正文资产，重新构建论文；生产格式门仍需单独关闭。

失败、栅格格式或尚未通过审查都不会导致 Goal 降级。
