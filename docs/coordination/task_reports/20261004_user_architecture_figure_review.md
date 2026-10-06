# 用户提供的“本地协作与角色账本流程图”复核

日期：2026-10-04

## 结论

这张图已经从概念流程图提升为有架构层级的 framework 图，但还不能作为
投稿终稿。它的视觉结构合格，科学语义仍有五处需要修正。

## 与样例库的对照

相较于之前的 v5/v6，这张图已经具备样例库中优秀 framework/architecture
图的主要层级：

1. `LOCAL PEERS` 给出参与者与候选关系；
2. `SITUATED EPISODE` 给出 producer、artifact、recipient 和 execution trace；
3. `EARNING ROLES ENGINE` 内含 `JUDGMENT`、`ATTRIBUTION`、`ROLE LEDGER`、
   `STATE READ` 四个子模块；
4. `PEER SELECTOR` 给出概率/探索/封存决策；
5. `OUTCOME` 和底部虚线回路给出跨时间反馈。

因此，它不再只是“Deliver → Select”的概念流程。结构层级已经接近
CollabLLM、Agentic Supernet 和 ToolkenGPT 的架构图语法。

## 评分

| 维度 | 分数 | 说明 |
|---|---:|---|
| 架构层级 | 8.4 | 有参与者、内部模块、中间对象、决策和反馈 |
| 主阅读路径 | 8.2 | 左到右清楚，中央模块有视觉中心 |
| 图面可读性 | 8.1 | 文字密度已可接受，节点层级较清楚 |
| 视觉质感 | 7.8 | 版式稳定，但仍偏示意图，数据对象细节较少 |
| 科学语义一致性 | 6.6 | attribution、delayed credit、轨道关系仍有歧义 |
| 投稿可用性 | 7.0 | 可作为候选底稿，修正语义后再转矢量 |

## 必须修正的问题

1. `EARNING ROLES ENGINE` 暗示最终模型架构已经确定。当前方法只锁定
   public `RoleEvidence`、read-cut 和可替换 representation/updater，建议改为
   `EARNING ROLES PROTOCOL` 或 `EARNING ROLES`。
2. `ATTRIBUTION` 目前看起来只接收 `JUDGMENT`。真实归因还依赖 producer
   contract、recipient action、changed paths 和 ownership/完整性判断。应让
   `path diff` 或 `execution trace` 也进入 attribution，或在 caption 中明确。
3. 底部 `OUTCOME` 虚线目前直接指向 `ROLE LEDGER`，容易被读成后续结果回写
   源 evidence。应明确它更新的是未来 selector/policy state，不能回写已经封存
   的 source ledger record。
4. `accept / revise` 把判断空间固定成二值；当前协议允许 reject/unknown 等
   状态。建议改为 `judgment`，具体标签在 caption 中解释。
5. `LOCAL PEERS` 与 producer/recipient 轨道被画成一条必经链，可能误导为
   ArtifactRole 和 PeerSelect 两条实验轨道始终共享同一图结构。应标注
   `candidate menu` 或用轻量虚线表示可选关系。
6. `STATE READ` 的紫色条没有说明是 read-cut state。应加极短标签
   `read-cut`，并在 selector 附近标出 `assignment`，让输出对象闭合。

## 接受标准

修正上述语义后，这张图可以作为 Figure 1 的架构候选；当前版本只能作为
视觉与布局底稿，不能直接进入正文。下一步不应再增加文字，而应修正箭头
端点、模块命名和 caption 的责任边界，然后生成矢量版并做双栏缩放检查。
