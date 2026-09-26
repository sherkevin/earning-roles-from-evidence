# N03 TeamBench 候选任务静态筛选

日期：2026-09-26。源码固定为 `TeamBench@d185aef1916fd86a9ba554d581fd256319a973af`。

本轮只回答一个问题：在现有 TeamBench 中，是否存在第二个能够承载“上游交付、下游完成自己的工作、下游基于实际使用给出判断”的结构 root。没有运行生成器、候选代码、grader、pytest、LLM API 或 GPU；因此本文不能支持效果或学习结论。原始配置和逐文件静态证据见 [`config.json`](../../experiments/logs/n03_teambench_candidate_scan_20260926/config.json)、[`raw.json`](../../experiments/logs/n03_teambench_candidate_scan_20260926/raw.json) 和 [`results.json`](../../experiments/logs/n03_teambench_candidate_scan_20260926/results.json)。

## 判定标准

候选必须同时满足四个条件，不能用“文件里出现 consumer”代替：

1. 上游确实产生一个可交付物；
2. 下游仍有原任务本来就要求的独立工作，不能删掉已有代码再制造工作；
3. 下游真正读取或使用上游结果，且最终结果可以把上游交付质量、下游自身完成度和组合结果分开记分；
4. 这条依赖与当前 DIST1 的 queue/priority→consumer 结构不同，seed 变体不能冒充新的 root。

## 结论

**PIPE3_stream_processing 是目前最合适的第二个候选，并已通过父进程归因 smoke test，但仍未冻结。** 生成器明确生成 `producer.py`、`processor.py`、`sink.py` 和完整测试；producer 的 datetime 序列化错误会影响 processor，processor 自己还有 envelope 和编码两项独立错误，sink 会实际读取 processor 的输出（生成器 [`gen_pipe3_stream_processing.py:102`](../../references/benchmark_sources/TeamBench/generators/gen_pipe3_stream_processing.py:102)、[`gen_pipe3_stream_processing.py:144`](../../references/benchmark_sources/TeamBench/generators/gen_pipe3_stream_processing.py:144)、[`gen_pipe3_stream_processing.py:184`](../../references/benchmark_sources/TeamBench/generators/gen_pipe3_stream_processing.py:184)、[`gen_pipe3_stream_processing.py:246`](../../references/benchmark_sources/TeamBench/generators/gen_pipe3_stream_processing.py:246)）。原 spec 也明确区分 producer 的一项缺陷和 processor 的两项缺陷，并要求端到端流水线通过（[`spec.md:3`](../../references/benchmark_sources/TeamBench/tasks/PIPE3_stream_processing/spec.md:3)、[`spec.md:8`](../../references/benchmark_sources/TeamBench/tasks/PIPE3_stream_processing/spec.md:8)）。原 grader 源码包含 `produce → process → sink`、非 ASCII 和完整测试路径（[`grade.sh:144`](../../references/benchmark_sources/TeamBench/tasks/PIPE3_stream_processing/grade.sh:144)、[`grade.sh:207`](../../references/benchmark_sources/TeamBench/tasks/PIPE3_stream_processing/grade.sh:207)、[`grade.sh:300`](../../references/benchmark_sources/TeamBench/tasks/PIPE3_stream_processing/grade.sh:300)）。v1 归因 smoke test 发现宽松 `fromisoformat()` 掩盖上游格式错误；v2 按 spec 加入严格边界后四格控制矩阵完全可分，详细记录见 [`n03_pipe3_qualification_20260926.md`](n03_pipe3_qualification_20260926.md)。这些是资格证据，不是学习效果。

拟采用的责任切分如下：

| 角色 | 负责内容 | 评价方式 |
|---|---|---|
| producer | `producer.py` 输出 JSONL 事件 | 父进程直接检查 ISO timestamp、字段保真和输出格式；不通过 processor 反推 producer 正确性 |
| recipient | `processor.py` 将已收到事件变换并写给 sink | 记录 recipient 自己的变更、处理成功率、完整成本和最终 sink adoption |
| read-only support | `models.py`、`sink.py`、测试契约 | 作为共同环境；不能把 recipient 的 processor 修复归责给 producer |

因此，PIPE3 能承载我们的故事，但必须改造评分口径：原生 `pytest` 总分只能保留为复合结果，不能直接当作 peer judgment label。

## 备选与关闭项

**MULTI3_polyglot 是可保留的备选。** 它有 backend→frontend 的实际接口，生成器保证 backend、frontend、schema 层都有缺陷组合；原测试又用独立的 canonical wire object 测 frontend，便于拆开上游和下游得分。问题是 `shared/schema.json` 的责任必须先裁决，且 schema/round-trip 的组合检查不能直接解释为 recipient 对 producer 的判断。它暂不进入下一次真实调用。

**CROSS5_event_schema 只作 fallback。** 它的 producer/Java consumer 职责最清楚，且两侧都有原生缺陷；但 native grader 对 Java 只做括号和类名检查，没有执行真实 consumer。没有固定依赖的真实 consumer worker，就没有可接受的 adoption lineage，不能作为论文 benchmark。

**DIST3、NEG3 关闭。** DIST3 是单服务共享幂等存储，没有下游独立交付；NEG3 是排序决策问题，没有交付物、消费者或可归因 handoff。**INFRA2 只保留为 diagnostic-only**：planner→executor 信息分区有价值，但它没有下游消费者判断，不能替代我们的主线。

## 下一步门槛

下一步进入 PIPE3 的任务契约/隔离资格，不调用 LLM：

1. 固定一个 seed 和生成源码 hash，明确只读/可写路径；
2. 在父进程写出 producer contract probe、recipient integration probe 和成本/变更记录；
3. 人为构造“producer 正确、recipient 错误”和“producer 错误、recipient 正确处理”的控制样例，确认三类分数不混淆；
4. 这四格 smoke test 已通过；若任务契约或隔离门失败才转 MULTI3，不扩 N02，也不提交 GPU 作业。

这个顺序继续服务于原故事：我们要学习的是“谁在当前情境下交付得可靠、谁能在实际使用中判断并完成下游工作”，不是把一个任务的总 pytest 分数重命名为角色能力。
