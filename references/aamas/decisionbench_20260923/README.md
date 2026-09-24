# DecisionBench 一手来源索引（2026-09-23）

用途：界定本项目“从其他 agent 的判断学习角色”的近邻工作。此处只核对公开论文、代码和数据；没有运行 benchmark 或调用模型。论文使用 [arXiv v1](https://arxiv.org/html/2605.19099v1)，代码与数据链接钉在以下公开 Hugging Face revision，避免把以后更新的实现倒推为论文实现。

| 来源 | 固定版本 | 用途 |
|---|---|---|
| [论文 v1](https://arxiv.org/html/2605.19099v1) | arXiv:2605.19099v1 | 方法、实验和局限；尤其 [§3.1–3.3](https://arxiv.org/html/2605.19099v1#S3.SS1)、[§4.2](https://arxiv.org/html/2605.19099v1#S4.SS2)。 |
| [代码](https://huggingface.co/datasets/decisionbench/code/tree/08da513de448610cbe2f824989203edd73451f3c) | `08da513de448610cbe2f824989203edd73451f3c` | 公开、非 gated 的 runner、profile 生成和工具实现。 |
| [数据](https://huggingface.co/datasets/decisionbench/data/tree/614f9ef2aa06ba6dffbe539bf31a36e36ad4557c) | `614f9ef2aa06ba6dffbe539bf31a36e36ad4557c` | Stage-1/Stage-2 原始轨迹与聚合记录；[数据说明](https://huggingface.co/datasets/decisionbench/data/blob/614f9ef2aa06ba6dffbe539bf31a36e36ad4557c/README.md)。 |

## 论文和代码确认的事实

1. DecisionBench 的基本问题是选择是否委派、委派给哪个 **模型**。其候选池为 7 个厂商的 11 个有意异构的模型，任务来自 GAIA、τ-bench 和 BFCL；同一基准内按固定 seed 做 20/80 Stage-1 能力画像 / Stage-2 评估拆分。[论文 §3.1–3.3](https://arxiv.org/html/2605.19099v1#S3.SS1)。
2. C3 的“双 LLM judge”是 **agent 池外部** 的 Grok-4 和 Llama-4-Maverick，读取某个候选模型的 Stage-1 轨迹和统计，为它离线写能力卡。它们不是在协作任务中接收产物、判断是否采用或修复产物的工作伙伴。[论文 §4.2](https://arxiv.org/html/2605.19099v1#S4.SS2)；[profile_judge.py L1–18、L39–45、L244–256、L358–381](https://huggingface.co/datasets/decisionbench/code/blob/08da513de448610cbe2f824989203edd73451f3c/decision_bench/analysis/profile_judge.py)。
3. Stage-2 的 `call_model(name, subtask)` 把一个自包含子任务发给候选模型，返回其文本结果给 orchestrator。后者被提示自行核实、总结或行动；其工具日志记录委派的对象、子任务、输出和成本。[论文 §3.3](https://arxiv.org/html/2605.19099v1#S3.SS3)；[call_model.py L21–46、L119–156、L168–177](https://huggingface.co/datasets/decisionbench/code/blob/08da513de448610cbe2f824989203edd73451f3c/decision_bench/call_model.py)。
4. C3 卡作为 Stage-2 条件的一部分预生成，`read_profile` 从每个模型对应的 Markdown 文件读取并缓存；此实现没有用一次任务里 orchestrator 对委派输出的采用、拒绝或返工去在线更新卡片。[read_profile_tool.py L11–18、L81–96、L161–185](https://huggingface.co/datasets/decisionbench/code/blob/08da513de448610cbe2f824989203edd73451f3c/decision_bench/read_profile_tool.py)；[benchmarks_runner.py L262–278、L630–678](https://huggingface.co/datasets/decisionbench/code/blob/08da513de448610cbe2f824989203edd73451f3c/decision_bench/benchmarks_runner.py)。最后一句是对公开实现的判断，不能推广为该 substrate 禁止未来方法在线更新。
5. 公开 [Stage-2 数据说明](https://huggingface.co/datasets/decisionbench/data/blob/614f9ef2aa06ba6dffbe539bf31a36e36ad4557c/README.md)列出 `delegations.jsonl`、`traces/calls.jsonl` 和每任务的被委派模型/成本/结果。它们能观察“发给谁、返回什么”，却没有原生的 `recipient_verdict`、`downstream_use`、`repair_cost` 或由这种伙伴判断触发的**下一任务职责变更**字段。这是按公开 schema 与工具代码作出的范围判断，并非声称每条 trace 都未出现非正式核查/修改行为。

## 对本项目的边界与可复用点

DecisionBench 已覆盖“外部 judge 对旧轨迹总结能力 → orchestrator 选择异构 peer”的思想，不能把这个宽泛命题单独称为新颖。它的 C3 是 **benchmark 上的 reference profile intervention**，而不是本项目欲研究的“实际接收者评价交接产物，并把可归因的采用/返工证据用于后续可变职责”。上述区别仍是待实验证明的研究主张，不是现有方法的性能结论。

可复用的是固定 Stage-1/Stage-2 边界、委派事件与成本日志、公开原始轨迹、异构模型选择作为强近邻对照，以及将 judge 内容与画像交付渠道分别消融的设计。其现成 GAIA/τ-bench/BFCL 任务不能直接证明伙伴之间的必要依赖；若用其任务做我们的实验，必须另设且披露交接依赖、接收者判断及在线角色更新协议。
