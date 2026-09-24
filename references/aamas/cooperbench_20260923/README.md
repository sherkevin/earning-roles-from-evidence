# CooperBench 一手来源审计（2026-09-23）

范围：只读核对[论文 v1](https://arxiv.org/html/2601.13295v1)与[官方仓库固定提交 `63b9d44d9f39a02fccf5bf0052db48a917a011fd`](https://github.com/cooperbench/CooperBench/tree/63b9d44d9f39a02fccf5bf0052db48a917a011fd)。只缓存以下四个小型公开源码/文档供**引用和协议设计**，没有下载大数据、导入运行环境、执行 benchmark 或调用 LLM。下文把论文中的设计和 2026-09-15 仓库代码区分开，避免将不同版本混为一谈。

| 本地只读参考 | 固定上游来源 | Git blob SHA-1 | 本地 SHA-256 / 字节 |
|---|---|---|---|
| [runner_coop.py](runner_coop.py) | [runner/coop.py](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/runner/coop.py) | `304766f9b79a3f976c124d7036e4c90524a4ae0d` | `519102b19f00ed214b0a8808177a90c34d1392748f417ba38ad53518775383b9` / 15,444 |
| [runner_team.py](runner_team.py) | [runner/team.py](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/runner/team.py) | `ee0de582dc8957ffda01c6fbd355fa9318825355` | `91d5cdf96364de0d505ded0f1a41bfa2f1311ca6739f8b36818bfda88025f78d` / 17,699 |
| [eval_sandbox.py](eval_sandbox.py) | [eval/sandbox.py](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/eval/sandbox.py) | `e2157136b15196d99d76f3c9edada42a92a5a6a9` | `cd69b9ce6fd04425a31e8e45ecb3eb8dbf379cef9c746107aecd0d92a5f438fc` / 28,475 |
| [dataset_README.md](dataset_README.md) | [dataset/README.md](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/dataset/README.md) | `08663be68b5ae6497c8581e15b7dc4704dbb8466` | `08dbfcd69419edef935ab8aa4cf1d3af37d150397a34095bc94c9b844725299e` / 5,931 |

该固定提交的根目录没有 `LICENSE`/`LICENCE` 文件（官方 Git tree 与 `/license` API 均未返回）；树内同名文件属于 vendored agent，不能冒充 CooperBench 自身的许可原件。因此没有伪造或误缓存 `LICENSE`。项目的 [pyproject.toml](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/pyproject.toml#L1-L6) 声明 `license = {text = "MIT"}`，[数据说明](dataset_README.md)的 frontmatter 也标 `license: mit`；这两条是可核对的许可声明，非独立许可文件。

## 原生任务和模式

论文报告 12 个开源代码库、652 个双 feature 配对，目标是在同一基底仓库状态实现两项兼容但可能发生代码冲突的功能。[论文 §2](https://arxiv.org/html/2601.13295v1#S2)。这里的“真实”是**真实开源代码库与 PR 锚点**；论文 §2.3 明确说，部分相邻 feature 由作者扩展撰写，不能把 652 个配对都称为原样的真实用户 issue。[论文 §2.3](https://arxiv.org/html/2601.13295v1#S2.SS3)。当前[数据说明](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/dataset/README.md)将这些需求描述为真实 PR 拆分，并报告 199 个 feature、499/652 个金标准双补丁会直接冲突；这个版本措辞与论文的“PR 锚点 + 相邻构造”并不完全相同，引用构造过程时优先标明具体来源版本。

官方 [README](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/README.md)提供 `solo`（一人实现全部 feature）、`coop`（同级 agent 各预分配一项 feature、Redis 消息，可选共享 Git）、`team`（固定 lead/member 与任务列表）。[coop.py L149–152](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/runner/coop.py#L149-L152)确实预先绑定 agent→feature；[team.py L143–157、L228–231](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/runner/team.py#L143-L157)进一步预分配 task 并固定首位 agent 为 lead。agent 可以通过交流协商重分工，但这个选择不是基准的初始任务配置。

`coop` 保存 [conversation.json、每人轨迹、每人补丁、调用成本与步数](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/runner/coop.py#L172-L244)。因此可以追踪消息与实现变动，但原生日志并无结构化的交接产物、接收者 accept/reject、采纳比例、返工成本或由其引起的下一任务职责更新；从自由文本追认这些事件需要独立标注，不能直接当事实。

## 依赖与评分的准确边界

两个 feature 可能碰到同一代码逻辑，独立补丁需要兼容；这比 AppWorld 单人读→写任务更自然地制造协作压力。但 agent 各自可以独立完成 feature；自动合并和测试不构成**必须由一个人交付、另一个人判断后才能行动**的顺序交接。它也没有跨配对保留的身份/角色学习规则。

当前[测试代码 L93–122](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/eval/sandbox.py#L93-L122)对两份 agent 补丁建分支、尝试合并，再以两个 feature 的 `tests.patch` 跑测试；`both_passed` 是客观的双测试结果。**关键例外**：[L220–269](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/eval/sandbox.py#L220-L269)在合并冲突或缺输入时允许测 agent1 的单独补丁；若它独自通过两组测试，[`both_passed` 仍可为真、strategy 可是 `solo-agent1`](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/eval/sandbox.py#L271-L296)。因此官方成功分数证明功能达标，**不自动证明双人交接或 peer 工作被使用**。需并报 `merge.status/strategy`、双方轨迹及产物贡献，且把单人成功路径单列。当前代码中的这个 fallback 与论文原始流程表述可能不完全相同，比较历史结果时应钉住运行版本。

## 拆分、成本和项目适配

同一基底 task 的不同 feature pair 共享仓库状态、需求和测试模式。按 pair 随机划分开发/确认会泄漏；应至少按完整基底 task/feature pool 分组，强独立性可按仓库留出。[当前 flash/lite 子集按 pair 抽样](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/dataset/README.md#L79-L116)，适合跑通开发流程，不是我们角色学习结论的确认拆分。[`flash_10`](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/dataset/subsets/flash_10.json)又依据既有通过/失败信号人工挑选，更只能做 smoke。

操作成本比现有 AppWorld 高：本地 Docker 或云端 Modal/GCP、Redis 消息服务、12 个库跨 Python/TypeScript/Go/Rust 的依赖镜像和代码 agent 适配，以及实际模型 API 调用与成本记录。[README 安装与模式说明](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/README.md)。仓库 [pyproject.toml](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/pyproject.toml#L6)声明 Python ≥3.10，但 README 写 3.12+；运行前需实际预检。Idealab 与现有 agent adapter 的兼容性未经验证，本索引不声称可直接运行。

结论：CooperBench 是值得借用的**客观合并/测试基底和可追溯交互日志**，不是原问题的现成实验。要研究从接收者判断中形成角色，须在同一任务池上给初始同能力身份开放工作和伙伴选择，显式封存交接、接收者判定/使用/返工，再只用这些在线事件更新后续责任；保持测试器离线，加入相同预算的无学习/静态/乱序反馈对照，并披露所有新协议。先用 `flash_10` 做纯工程 smoke，再按 task 或 repo 分组做前瞻验证。
