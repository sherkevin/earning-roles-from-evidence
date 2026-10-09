# PIPE1 原生执行前隔离审计

日期：2026-10-08。结果：**直接复用原生 harness 被阻止**。

零调用复核用 pinned TeamBench commit `d185aef1916fd86a9ba554d581fd256319a973af`
的本地 harness 建立临时目录，实际调用同一 `make_executor_config` 的工具配置。
Executor 可以读取 workspace、reports/expected、task brief；shell 为 unrestricted。
另从源码确认 `run_all` 调 generator 时没有传 `task_dir`，所以动态 spec/brief 不会
写入 TaskOrchestrator 随后读取的位置。

原始结果：[isolation audit logs](../../../experiments/logs/n03_pipe1_isolation_audit_20261008_v1/)。

## 科学解释

这不是“模型已经作弊”的实验证据，而是说明实验环境允许作弊且角色材料可能为空。
在此条件下运行 Planner/Executor/Verifier，任何质量差异都无法归因于 peer 消息或
评价选人。full-spec relay 仍是应保留的强控制，但必须和 generated planner 使用
同一安全、同一可见性、同一成本的 executor 环境。

因此没有调用 API，也没有把 PIPE1 写入 active benchmark、没有改变历史结果、没有
启动 GPU。修复边界和可复用部分见[修复卡](../../research/candidates/pipe1_isolation_repair_v0.1_20261008.md)。

| 三份标准 | 本轮证据 | 仍缺什么 |
|---|---|---|
| 故事线/创新 | 排除了“环境泄漏造成的伪协作增益” | J 对未来责任分派的真实增量 |
| 方法 | 明确了 pre-action route 的隔离和 pre-Verifier 读数边界 | 合法在线更新、独立收益、实时/稳定/时效性 |
| Benchmark/baseline | 证明 PIPE1 目前不能作为公平可执行 benchmark；full-spec relay 仍是必要强控制 | 修复 runner、exact scorer、完整成本、独立 root/stream |

Goal 和六份 ACTIVE 文档没有降级，科学 gate 仍关闭。
