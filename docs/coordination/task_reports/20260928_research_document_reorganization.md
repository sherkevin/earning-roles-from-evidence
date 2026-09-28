# 2026-09-28 研究文档重组与唯一 active 版本登记

- **状态**：`COMPLETE`（文档治理任务）；不代表科学 Goal 完成
- **对应 Goal**：ER-G1/ER-G2/ER-G3 的文档可审计性与变更控制；没有改变 Goal v1.0
- **goal_change_requested**：`false`
- **是否运行真实 API/GPU**：否；本任务不需要实验，未把文档整理冒充科学证据

## 已完成

1. 建立六个唯一类别：故事线与创新点、方法论、benchmark+baseline、以及三份对应评价标准。
2. 每类建立版本正文并写明 `ACTIVE`、生效日期、前一版本和职责；`canonical/active_versions.json` 保证每类只指向一个版本。
3. 将旧主线、旧合并评审规则、旧 benchmark candidate 和旧 StreamJEV method spec 做 SHA-256 字节归档；原路径改为兼容指针，防止它们继续被误读为当前规范。
4. 增加 `docs/research/README.md`，区分 canonical、版本、dated research report 和 archive。
5. ADR0039 仅记录文档职责边界和版本规则；它没有重新决定 RARE、PIPE3、backbone 或 baseline。
6. 独立复核后，在 active 方法/实验文档中显式保留 arrival-order、late-correction、context-capacity 和 baseline-input 合同缺口；没有把接口草图写成已完成算法。

## 与 Goal 对照

- **已满足**：当前故事的审计入口、方法开放状态、benchmark 候选状态和评价维度有唯一可定位来源；历史失败和候选未冻结状态保留。
- **部分满足**：文档已经定义需要的证据门，但真实 recipient judgment、future assignment、独立 root、强 baseline、实时性/遗忘和最终更新器仍未完成。
- **仍需方法设计**：延迟/乱序 replay、later-outcome correction 的幂等语义、context 状态容量/泛化和各 baseline 的逐事件输入合同尚未冻结。
- **未满足**：没有新增任何科学效果、benchmark freeze、backbone lock 或 A800 结果。

## 未完成原因

这是治理任务，不是用文档改写证据。未完成项属于当前实验资格、责任归因、强 baseline 和方法验证缺口，不能通过改写文档解决，也不能因为实验失败而降级 Goal。

## 下一步

读取六份 active 文档作为唯一研究入口；先完成 N03 当前 runner/lineage/scorer qualification 和同信息 baseline，再决定是否形成真实开发卡。只有真实信号与明确瓶颈出现后，才选择一个 updater/backbone 做 bounded A800 实验。

## 变更记录

旧来源副本与哈希见 [`docs/archive/document_reorganization_20260928/manifest.json`](../../archive/document_reorganization_20260928/manifest.json)。六份 active 文档的具体内容均保留“候选/未锁定/待验证”标记，没有把历史草图升级成结论。
