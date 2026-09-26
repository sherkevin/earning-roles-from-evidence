# N03 PIPE3 归因资格 smoke test

日期：2026-09-26。源码固定为 `TeamBench@d185aef1916fd86a9ba554d581fd256319a973af`，任务为 `PIPE3_stream_processing`、seed 0。本轮执行的是生成任务代码的父进程控制样例，不是 LLM 候选实验；没有调用 LLM、pytest、native TeamBench grader、GPU 或网络。原始日志：[`v1`](../../experiments/logs/n03_pipe3_qualification_20260926/)、[`v2`](../../experiments/logs/n03_pipe3_qualification_20260926_v2/)。

## 为什么先做控制样例

我们要把三个对象分开：

- producer 是否交付了符合 spec 的 JSONL；
- recipient 自己的 processor 工作是否正确；
- 完整 producer→processor→sink 是否真正被采用。

如果只看原生 `pytest` 总分，三者会混在一起，不能作为 situated judgment 的标签。

## v1 暴露的真实问题

第一版只在父进程分别测 producer、recipient 和完整 pipeline。结果为：

| 变体 | producer 质量 | recipient 自有工作 | pipeline adoption |
|---|---:|---:|---:|
| 原始 | 0 | 0 | 0 |
| 只修 producer | 1 | 0 | 0 |
| 只修 processor | 0 | 1 | **1** |
| 两者都修 | 1 | 1 | 1 |

“只修 processor”时完整流水线通过，原因是 Python 当前运行时的 `datetime.fromisoformat()` 接受空格分隔的时间戳；它掩盖了 producer 的 spec 违规。这个结果说明原生完整 pipeline 不能直接证明 producer 交付被下游按契约接受。v1 的失败日志保留，不回写。

## v2 的修正与结果

v2 在 processor 解析前加入了 spec 已明确要求的边界断言：时间戳必须是带 `T` 的 ISO 字符串。这个断言不是新增业务义务，而是把 spec 第 9、35–37 行已经写明、却被 Python 宽松解析器隐藏的接口契约放回父进程评分。recipient 自有工作仍使用一个独立的、符合契约的 canonical 输入，因此不会把 producer 缺陷倒灌给 recipient 分数。

| 变体 | 修改文件 | producer 质量 | recipient 自有工作 | pipeline adoption |
|---|---|---:|---:|---:|
| 原始 | 无 | 0 | 0 | 0 |
| 只修 producer | `producer.py` | 1 | 0 | 0 |
| 只修 processor | `processor.py` | 0 | 1 | 0 |
| 两者都修 | `producer.py`, `processor.py` | 1 | 1 | 1 |

四个控制样例完全符合预期矩阵，`attribution_separable=true`。这只证明评分可以区分三类结果，不证明任何 peer 学习收益、任务难度或跨 seed 泛化。

## 对 benchmark 决策的影响

PIPE3 现在可以进入下一层“任务契约与真实 agent 运行前资格”候选，但还不能称为最终 benchmark。下一步仍需：

1. 固定 producer 可写、recipient 可写和只读路径；
2. 把 parent contract probe、recipient integration probe、最终 sink 结果和完整成本写入统一事件账本；
3. 冻结同信息的 no-update、terminal-only、总体可靠性和 contextual trust/bandit 对照；
4. 只在这些条件通过后，使用一个真实 producer→recipient 链验证 judgment 是否携带任务/消费者情境增量。

PIPE3 与现有 DIST1 的结构不同：DIST1 是 queue/priority 交付后由 consumer 集成；PIPE3 是 serialization/stream contract 交付后由 processor 变换并由 sink 采用。两个 seed 仍然属于同一个 PIPE3 root，不能当作两个独立任务。

独立复核也保留在 [`independent_review.json`](../../experiments/logs/n03_pipe3_qualification_20260926_v2/independent_review.json)：它确认 v2 的严格边界和四格 parent 矩阵合理，同时指出 seed、multi-event、非 ASCII、异常路径、字段完整性和 sink 业务结果仍未覆盖。因此当前结论仍是“通过归因 smoke gate，未通过 benchmark freeze”。
