# 三张投稿图独立最终审查

日期：2026-10-07  
审查对象：当前活动正文图 overview.pdf（Figure 1，v30）、method_state.pdf（Figure 2，v32）、experiment_map.pdf（Figure 3，v34）  
审查性质：独立图稿审查；不修改活动图、历史版本或论文正文

对照文件：

- docs/paper/aamas2027/FIGURE_PLAN_v2.md
- docs/paper/aamas2027/GALLERY_FIGURE_STYLE_AUDIT_20261006.md
- docs/coordination/GOAL.md
- experiments/logs/figure_ai_long_goal_round_20261007_v30_v32_v34/receipt.json
- 纸面与灰度证据：同目录下 paper_scale/*_1050.png 与 grayscale/*_gray.png

## 审查方法

我同时检查了原始活动 PDF、对应 v30/v32/v34 生产 PDF、120 dpi 全尺寸渲染、1050px 纸面宽度渲染、1050px 灰度渲染，以及 PDF 的文字提取、TrueType 字体嵌入和底图保留。评价重点是图稿是否表达 situated judgment → responsibility evidence → future assignment → later outcome / delayed update，是否符合画廊审查中的一条主轴、对象化表达、短标签、受控颜色和单独反馈路径规则。

## 生产证据

三张活动 PDF 和三张对应的 v30/v32/v34 PDF 均为单页。每张图都包含一张 AI 生成的 raster 底图，并嵌入 Arial-BoldMT CID TrueType 字体：

| 图 | 页面尺寸（pt） | 可见文字 | 底图 |
|---|---:|---|---|
| Figure 1 | 2163.89 × 721.295 | TrueType，emb=yes、sub=yes、uni=yes | 1 张 RGB raster |
| Figure 2 | 1665.75 × 937.484 | TrueType，emb=yes、sub=yes、uni=yes | 1 张 RGB raster |
| Figure 3 | 1665.75 × 937.484 | TrueType，emb=yes、sub=yes、uni=yes | 1 张 RGB raster |

pdftotext 可以读出三张图的阶段标签、对象标签和关系标签；没有发现文字被栅格化后无法检索的情况。三张图的 1050px 和灰度文件尺寸分别为 Figure 1 的 1050×350，以及 Figure 2/3 的 1050×591。

这说明三张图通过了“AI 底图仍在、可见文字有嵌入字体、论文宽度和灰度版本可生成”的生产检查。它不等同于科学结果门或整篇论文的投稿就绪门。

## Figure 1 — Earning-roles loop

**评分：8.7 / 10**

### 语义因果链：9.0

图从 peer context 和 task 开始，沿着 artifact、recipient use、judgment、role evidence、read cut、future assignment、later outcome 形成单一主轴。灰色 UNKNOWN 分支把未能归因的情况从主证据流中分离；底部的 selected-only delayed update 把 later outcome 连接回未来状态。它能够支持图组计划中的一句话测试。

主要剩余歧义是：peer context 中的蓝色 A 与后续蓝色 producer 的对应关系依靠颜色和位置推断，没有写出 producer 标签；同时顶端从 JUDGMENT 到 LATER OUTCOME 的主线容易让快速读者误读为结果立即可见。底部 AFTER SEAL 和虚线回写已经缓解这个问题，但 caption 仍应明确 target outcome 在 assignment seal 后到达。

### topconf 视觉质感：8.3

优点是中央机制有视觉重量，颜色承担阶段职责，图形对象承担 artifact、judgment、ledger、read cut、seal 和 outcome 的含义；整体比模块卡片式版本更接近画廊中的连续 pipeline。

扣分点是图标来自统一的通用线性 glyph，细部层次和定制程度仍低于画廊中最成熟的 best-paper 主图；底部时间线和反馈路径在视觉上略轻，右半边的锁、仪表和货币图标比中央机制更醒目。它已经是可用的论文图，但还不是看一眼就有独特方法签名的最终视觉状态。

### 纸面可读性与灰度：8.5

1050px 版本的阶段标签、对象标签和主箭头清楚；灰度版仍能依靠线型、形状和明暗区分主要语义。底部的 SELECTED-ONLY DELAYED UPDATE、OBSERVED EPISODE 和 AFTER SEAL 在纸面缩小后是最弱的文字，仍可辨认，但不宜继续缩小图宽或减小字体。

### 标签、字体和图文一致性：9.1

标签短且与正文术语一致，Arial Bold TrueType 已嵌入。 UNKNOWN、READ CUT、FUTURE ASSIGNMENT 和 LATER OUTCOME 与正文的事件边界一致。需要在 caption 中补充 producer/recipient 的角色对应，不能只依赖颜色。

### 是否需要新的 AI prompt

**不需要新的 AI prompt。** 目前最有价值的改进属于 caption 或文字生产层：加强 A→producer、recipient→judgment 和 target-after-seal 的解释。如果重新生成底图，容易破坏已经通过的主轴和对象对应关系。

## Figure 2 — Evidence-to-role state

**评分：8.8 / 10**

### 语义因果链：8.9

三条泳道清楚分出 EPISODE、PUBLIC EVIDENCE 和 LOCAL DECISION。artifact 到 judgment 到 target 的事件链、judgment 投影到 project/gate/row 的证据链、以及 peers 到 read cut 到 sealed assignment 到 selected-only update 的决策链彼此分离。BEFORE SELECTION 和 AFTER SEAL 也把跨泳道关系放到了正确的时间位置。

剩余问题是 UNKNOWN / AUDIT 位于 gate 下方并通过灰色短线连接，第一次阅读时更像一个审计旁注，而不是 gate 的合法第三结果；caption 需要说明它代表无法证明责任归属的审计结果。顶端 target 与判断之间的实线箭头仍可能让读者以为 target 是同一时刻产生，虚线 AFTER SEAL 已经给出修正线索，但可以在 caption 里再明确一次。

### topconf 视觉质感：8.4

这是三张中最接近方法图范式的一张：开放泳道、连续箭头、少量对象 glyph 和受控的三色职责编码都有效。相较样例库中的成熟方法图，左侧泳道标题有两行文字，图形对比略弱，公共证据行和决策行的水平空间较空；视觉上仍有漂亮流程图的气质，尚未达到高度定制的机制图质感。

### 纸面可读性与灰度：8.7

1050px 与灰度版中三条泳道仍可区分，箭头方向、竖直边界和虚线关系清楚。PUBLIC EVIDENCE、LOCAL DECISION 在缩小后仍能读出，但两行标题的垂直间距较紧；关系标签 BEFORE SELECTION 和 AFTER SEAL 是最需要 caption 辅助的文字。

### 标签、字体和图文一致性：9.2

所有主要对象和泳道术语与正文方法段一致，字体可提取且嵌入。图中没有把某一种 backbone 或 updater 画成已经确定的实现，这一点符合图组计划中表示/updater 是可替换接口的约束。

### 是否需要新的 AI prompt

**不需要新的 AI prompt。** 视觉底图的结构已经正确；若继续改，应只调文字层的 UNKNOWN / AUDIT 位置或在 caption 中补充 gate 语义。重新生成会带来泳道边界、虚线关系和对象位置漂移风险。

## Figure 3 — Benchmark/baseline experiment map

**评分：8.6 / 10**

### 语义因果链：8.5

三列结构明确表达 tracks → policies → endpoints。左列区分 ArtifactRole 和 PeerSelect，中列列出 NO UPDATE、RAW ACCEPTANCE、CONTEXTUAL TRUST 和 RARE，右列给出 RQ1 information、RQ2 assignment、RQ3 service、RQ4 safety。顶部的 MATCHED INFORMATION • MATCHED COST 把公平比较条件置于全图上方，符合实验设计的主旨。

需要注意的是，图把 RARE 放在策略臂中。正文目前将 RARE 写成责任感知的角色证据/候选闭环机制，而不是已证明的最优更新器；这在图中是允许的，但 caption 和正文必须始终保持候选方法语气，避免读者把这张实验地图看成已完成的结果图。STREAM COMPARISON 标签说明中心策略到终点的比较，但没有进一步说明哪个终点只对应 PeerSelect、哪个终点只对应 ArtifactRole，这部分仍依赖 caption 和实验矩阵表。

### topconf 视觉质感：8.1

框架清楚，颜色和列职责稳定，图形对象与 Figure 1/2 统一。相较画廊中的高等级实验图，中心策略行仍主要由圆点、箭头和文字组成，缺少能够表达同信息、同成本、分轨评价的更强视觉编码；右列的 RQ endpoint glyph 很有效，但各行分隔线与左列轨道的视觉重量略不均衡。它作为实验地图合格，作为论文中最有记忆点的主图仍有提升空间。

### 纸面可读性与灰度：8.4

1050px 版本中标题、策略名和 RQ 标签清楚；灰度版仍可通过分栏、分隔线、箭头和圆点状态辨认。PRODUCER ATTRIBUTION、LOCAL SELECTION + DRIFT、CONTEXTUAL TRUST 和右列的两行 RQ 标签属于较小文字，打印时应保持当前全宽版式，不能改为半宽图。

### 标签、字体和图文一致性：9.2

ArtifactRole、PeerSelect、RARE、四种 policy arm 以及 RQ1–RQ4 与正文实验矩阵一致；字体嵌入和文本提取通过。图没有放入未经正文定义的数值或结果，因此不会制造虚假实验结论。

### 是否需要新的 AI prompt

**不需要新的 AI prompt。** 当前问题是实验矩阵的文字映射强度，而不是 AI 底图结构。若后续实验确认 PeerSelect 和 ArtifactRole 的终点集合不同，应该先更新实验矩阵和 caption，再决定是否调整文字层；不应为了目前的空结果位重新生成底图。

## 总结判定

| 图 | 语义 | 质感 | 纸面/灰度 | 字体/一致性 | 总分 | 判定 |
|---|---:|---:|---:|---:|---:|---|
| Figure 1 v30 | 9.0 | 8.3 | 8.5 | 9.1 | **8.7** | 生产通过，最终视觉部分通过 |
| Figure 2 v32 | 8.9 | 8.4 | 8.7 | 9.2 | **8.8** | 生产通过，最终视觉部分通过 |
| Figure 3 v34 | 8.5 | 8.1 | 8.4 | 9.2 | **8.6** | 生产通过，最终视觉部分通过 |
| **图组总体** | 8.8 | 8.3 | 8.5 | 9.2 | **8.7** | **PARTIAL** |

**总体判定：PARTIAL。**

三张图已经通过可复核的生产、纸面、灰度和主要语义门，可以作为当前正文候选。它们还不应被记录为最终投稿图冻结，原因有三点：

1. Figure 1 和 Figure 2 对 target-after-seal 的时间关系仍需要 caption 明确，快速浏览时存在轻微歧义；
2. Figure 3 的 RARE 仍是候选闭环机制，图文必须保持候选语气，并在最终实验矩阵冻结后复核终点映射；
3. 三张图的版式和字体已达到可用的 topconf 论文水准，但通用线性 glyph、中心策略行的抽象程度和底部小字仍比样例库中的最佳主图弱一档。

当前最小有效后续动作是更新 caption/图文一致性检查，并在实验矩阵冻结后重新做一次轻量审查。没有证据表明需要再发起一轮完整的 AI 重绘；若只为追求视觉质感而重绘，会增加语义漂移风险。科学投稿门、benchmark 门和方法效果门仍由 Goal 独立约束，本审查不改变它们的状态。

