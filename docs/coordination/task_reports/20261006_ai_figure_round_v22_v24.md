# Task report — AI figure round v22–v24 (2026-10-06)

状态：`PARTIAL`（图形表达门通过；科学证据门仍开放）

## 目标对应

本轮只处理写作/图形标准中“图表达机制、不要把文字堆成卡片”的要求：Figure 2
必须显示三类信息边界，Figure 3 必须显示实验轨道、policy arms 和 endpoints，且
不把它们画成一个笼统的 dashboard。没有修改 Goal 或科学验收标准。

## 冻结与操作

- v22 以 v20 为唯一输入；v23 以 v21 为唯一输入；v24 以 v23 为唯一输入。
- 每次编辑的具体视觉变化写入各目录的 `prompt.md`，历史 PNG/PDF 不覆盖。
- 本轮没有调用 LLM/API、GPU 或 Nebula；使用 Codex 内置 image-generation tool，
  再用 `sips` 将生成 PNG 转成论文嵌入 PDF。

## 结果

- **v22 Figure 2**：移除左侧大色块和泳道外框，改用彩色竖线、开放水平规则和留白；
  `EPISODE`、`PUBLIC EVIDENCE`、`LOCAL DECISION` 三条泳道及三条跨泳道关系保留。
- **v23 Figure 3**：把厚重圆角面板改成三个开放列和细分隔线；作为中间版本保留。
- **v24 Figure 3**：进一步移除四个 policy label 填充卡片；RARE 仍用蓝色文字和圆点
  高亮，但不再像额外 benchmark 卡片。

当前正文资产是 v19/v22/v24。使用
`article/aamas2027/build/figure_set_v19_v22_v24_review_20261006/main.pdf` 做实际版心复核：
正文 8 页、参考文献从第 9 页开始、引用已解析、`overfull_boxes=0`。

## 标准对照

- 已满足：版本可回退、提示词可追溯、两张图的卡片化缺陷已针对性修复、纸面缩放可读。
- 部分满足：AI 栅格图的字体和最终打印质量仍需提交版 PDF 再核验；这不影响当前内部
  图组选择，但不能把视觉检查当作科学证据。
- 未满足/不适用：benchmark 资格、baseline parity、真实结果、方法效果和科学投稿门。

## 下一步

没有新的具体视觉缺陷前，不再盲目生成 v25；继续主线 benchmark/baseline 与科学证据
工作。若正文机制改变，只从 v19/v22/v24 的原始提示词做定点编辑。

`goal_change_requested=false`
