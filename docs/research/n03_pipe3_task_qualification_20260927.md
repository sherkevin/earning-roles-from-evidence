# N03 PIPE3 任务契约、隐藏评分与隔离资格

日期：2026-09-27。范围：无 LLM 的前置资格检查，不是 benchmark 结果，也不是
peer-role 方法效果实验。源码固定为 `TeamBench@d185aef1916fd86a9ba554d581fd256319a973af`。

原始配置、逐事件日志和汇总结果：
[`config.json`](../../experiments/logs/n03_pipe3_task_qualification_20260927/config.json)、
[`raw.jsonl`](../../experiments/logs/n03_pipe3_task_qualification_20260927/raw.jsonl)、
[`summary.json`](../../experiments/logs/n03_pipe3_task_qualification_20260927/summary.json)。

## 本轮检查

本轮生成 PIPE3 的 seed 0、1、2，验证三件事：

1. producer 和 recipient 的公开文件、写权限、交付路径是否互斥且稳定；
2. hidden tests/expected 是否留在父进程，不能进入 agent payload；
3. 选择、交付、判断、consumer action、独立评分、role update 是否有严格顺序，
   并把已经验证过的 macOS 访问/资源 canary 接到同一份运行日志。

运行记录显示：`llm_calls=0`、`gpu_jobs=0`、`pytest_invoked=false`、
`native_grader_invoked=false`、`network=false`。TeamBench checkout 的 commit 和
clean 状态均符合预期。

## 结果

| 检查 | 结果 |
|---|---|
| seed 0/1/2 任务契约 | 3/3 PASS |
| producer 可写路径 | `producer.py` |
| recipient 可写路径 | `processor.py` |
| read-only support | `models.py`, `sink.py` |
| hidden files | `tests/__init__.py`, `tests/test_pipeline.py`, `tests/test_serialization.py` |
| 账本顺序 | 6 个事件全部通过，selection 在 execution 前，update 在 score 后 |
| isolation canary | listed access/resource checks PASS |
| production sandbox / same-process gold protection | 未通过资格，仍为 false |

hidden score 只出现在父进程的 `independent_score` 事件中；recipient payload 不含
tests 或 expected。producer 与 recipient 的写权限没有交集。账本校验拒绝重复 event
ID、交付前判断、评分前更新等顺序错误。

## 结论边界

本轮通过的是 **PIPE3 preflight qualification**，因此可以进入下一步真实
producer→recipient 小流的准备；它没有关闭 N01，也没有把 PIPE3 冻结为最终 benchmark。
还缺：

* 真实 agent 执行及隐藏评分，包含多事件、字段缺失、异常和正常 integration；
* 完整 producer contract、recipient 自有工作、sink adoption 和责任证据的端到端账本；
* 独立 task-root 的 development/confirmation 划分；
* 完整 API/token/tool/返工成本和 UNKNOWN 规则的真实验证。

隔离 canary 的边界也保留：它证明列举的文件、网络、fork 和资源访问约束可工作，
不证明 production sandbox，也不解决 native pytest 与 candidate 共享 Python 进程的
同进程评分问题。因此下一步仍不能调用 GPU 或声称 benchmark 已资格通过。
