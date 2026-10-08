# PIPE2 v2 typed handoff descriptor qualification

日期：2026-10-08。结果：`QUALIFIED_OFFLINE`；这是一个接口子门，不是 benchmark、
在线学习或论文效果结果。

## 任务目的

上一轮 compatibility audit 证明 PIPE2 的真实交付是 opaque
`artifact/extracted_rows.json`，而已有 source-file observation bridge 需要 recipient
看到 producer-owned source。v0.1 descriptor 能分离 source/artifact，但没有显式事件
绑定，也不能表示 J 与实际 A 的差异。本轮用新 schema v2 修复这些问题，同时保持 v1
历史回执不变。

## 执行与日志

- 配置：[card](../../../configs/aamas2027/n03_pipe2_handoff_descriptor_v2_qualification_20261008.json)
- runner：[script](../../../scripts/peerrolebench_pipe2_handoff_descriptor_v2_qualification.py)
- v2 结果：[summary/events](../../../experiments/logs/n03_pipe2_handoff_descriptor_v2_qualification_20261008_v2/)
- 第一次缺 hash 的失败：[v1 log](../../../experiments/logs/n03_pipe2_handoff_descriptor_v2_qualification_20261008_v1/)

执行前已经写 config；runner 读取真实 seed-0 public material，调用真实
`validate_extracted_rows`，随后只使用标记为 synthetic 的事件引用 fixture 检查
descriptor。没有执行 candidate code、native grader、LLM API、GPU 或 policy update。

## 结果

| 检查 | 结果 |
|---|---|
| producer 可见 `pipeline/extract.py`、recipient 不可见 | PASS |
| recipient 等待 `artifact/extracted_rows.json`，artifact schema/hash 独立 | PASS |
| delivery/J/A/outcome ID、事件类型、索引和 hash 绑定 | PASS |
| `accept + repair` mismatch 保留 | PASS |
| 缺 J/A/Y 事件引用 | fail closed，PASS |
| opaque delivery 混入 source manifest | fail closed，PASS |
| 定向 v1 + v2 tests | 19/19 PASS |
| descriptor + compatibility + material regression | 23/23 PASS |

## 解释边界

本轮关闭的是“v2 descriptor 能否表达并拒绝明显串线”的工程子门。synthetic event
fixture 不能证明 recipient 的真实判断或 outcome，也不能证明责任归因、未来选择、
实时更新或任何方法收益。v1 历史 schema 与报告没有被改写。

当前仍不能把 PIPE2 runtime receipts 回放成 J/A/Y，也不能启动选择器训练或 A800。下一
个有意义的动作是实现一个版本化 runtime adapter，让一次真实 episode 产生 native
delivery/J/A/Y 与接收方前后快照，再用同一信息重放 J-masked/count-only 对照；缺任何
绑定时保持 `UNKNOWN`。
