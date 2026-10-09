# earning-roles：Learning Roles from Situated Peer Judgments

本仓库的目标是验证：真实 recipient 对具体交付的判断和使用，能否形成可归因的 producer role evidence，改变未来责任分派，并改善未见任务的团队质量与完整成本。项目目标章程是 [`docs/coordination/GOAL.md`](docs/coordination/GOAL.md)，目前不能因失败或数据不足自动降级。

**论文唯一主版：[`artifacts/aamas2027/main.pdf`](artifacts/aamas2027/main.pdf)。** 各轮迭代保存在其下一层目录；完成的改动先合并到主稿源文件，再编译、检查并同步主版，保留旧版本。流程见 [论文维护说明](article/aamas2027/README.md) 与 [ADR 0050](docs/user/decisions/0050-canonical-main-pdf-and-versioned-builds.md)。

## 当前唯一研究入口

| 文档 | 唯一生效登记入口 |
|---|---|
| 故事线与创新点 | [当前版本登记表中的“故事线与创新点”](docs/research/canonical/README.md) |
| 方法论 | [当前版本登记表中的“方法论”](docs/research/canonical/README.md) |
| Benchmark + baseline + 实验计划 | [当前版本登记表中的“Benchmark + baseline”](docs/research/canonical/README.md) |
| 三份评价标准 | [`docs/research/canonical/README.md`](docs/research/canonical/README.md) |
| 决议索引 | [`docs/user/decisions/README.md`](docs/user/decisions/README.md) |
| 当前任务与 Goal 对照 | [`docs/coordination/TASK_REPORTS.md`](docs/coordination/TASK_REPORTS.md) |
| 论文/投稿材料 | [`docs/paper/aamas2027/REQUIREMENTS.md`](docs/paper/aamas2027/REQUIREMENTS.md) 与 [`article/aamas2027/README.md`](article/aamas2027/README.md) |

## 当前科学状态

故事线已经收敛到 `situated judgment → attributable role evidence → future assignment → quality/cost`。方法最终 backbone/updater 尚未锁定；RARE 是待验证候选，不是已证明算法。`PeerRoleBench-TB` 仍是候选，PIPE3 仍需通过 runner/scorer/lineage 资格，强同信息 baseline、独立 confirmation stream、实时性/遗忘结果和 A800 challenger 均未完成。历史真实 API 失败、UNKNOWN 和有限链路都保存在 `experiments/logs/` 与 dated task reports 中，不能被整理任务改写。

## 目录原则

- `docs/research/canonical/` 只登记六类 active 文档；`docs/research/versions/` 存版本正文。
- `docs/coordination/` 放任务状态和逐项 Goal 对照；`docs/user/decisions/` 只放一个小的已对齐决议一文件。
- `experiments/logs/`、`artifacts/` 和 `references/` 保存可复现证据、原始失败和来源；不把它们写成 active 规范。
- `article/` 只放可编译论文源与构建材料。
- 重组前来源的字节副本见 [`docs/archive/document_reorganization_20260928/`](docs/archive/document_reorganization_20260928/)。

详细结构见 [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)。
