# Task report — AI figure round v19–v21 (2026-10-06)

状态：`PARTIAL`（图形与排版门通过；科学证据门不适用且仍开放）

## 目标对应

本任务对应故事线/写作标准中的“图只承载一个机制主张”、方法标准中的“隔离
episode、public evidence、local decision 的时间边界”，以及 benchmark+baseline
标准中的“轨道、政策臂和终点必须可区分”。没有修改 Goal，也没有降低任何科学验收标准。

## 运行前冻结与输入

- v18/v19/v20/v21 的提示词分别保存在对应 `figures/ai_versions/` 目录；旧版本不覆盖。
- Figure 1 的语义不变量：read cut 先于 sealed assignment，later outcome 在 seal 之后，
  delayed selected-only feedback 只回到下一次 read cut，UNKNOWN 只进入审计分支。
- Figure 2 的三条泳道及三条跨泳道关系在提示词中预先写明。
- Figure 3 的 ArtifactRole/PeerSelect 分轨、四个 policy arm 和 RQ1–RQ4 endpoint
  在提示词中预先写明。
- 本任务未调用 LLM/API、GPU 或 Nebula；只使用 Codex 内置 image-generation tool
  生成图形候选，并使用 `sips` 将已生成 PNG 转为 PDF 以嵌入论文。

## 观察结果

纸面版心复核使用 `article/aamas2027/build/figure_set_v19_v20_v21_review_20261006/main.pdf`：

- 10 页总页数，正文 8 页，参考文献从第 9 页开始；
- 引用解析，`overfull_boxes=0`；
- Figure 1 在全宽位置保持一条开放主轴，`TASK` 标签补齐了灰色节点；
- Figure 2 的 episode、public evidence、local decision 三条泳道清楚，跨泳道箭头不交叉；
- Figure 3 在正文宽度下仍能辨认三个 panel、四个 policy arm 和四个 endpoint，且没有
  把 RARE 画成额外 benchmark 或把 RQ1–RQ4 合并成一个标量。

## 标准对照

- 已满足：图形版本留档、提示词留档、正文版心构建、页数和溢出检查、核心语义边界可读。
- 部分满足：AI 图中的文字仍需在最终投稿 PDF 版本再次以实际缩放核验；图形风格已接近
  参考库，但不把风格相似当作科学质量证明。
- 未满足/不适用：benchmark 资格、baseline parity、真实结果、方法效果和科学投稿门；
  这些不能由图形工作代替。

## 下一步

保留 v19–v21 为当前正文图组；若正文内容或审稿意见改变机制边界，只从保留的提示词
和候选版本做定点编辑，不重新绘制或覆盖历史资产。下一项主线工作回到 benchmark/
baseline 和科学证据门。

`goal_change_requested=false`
