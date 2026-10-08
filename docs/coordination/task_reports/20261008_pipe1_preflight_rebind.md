# PIPE1 preflight native rebind integration

日期：2026-10-08
状态：`QUALIFIED_ZERO_CALL_NATIVE_REBIND`

## 目的

前一轮已经单独修复并资格化 adapter–route join，但 PIPE1 preflight 仍可以只读取结构化 route receipt。这样会允许两个各自形式上有效、但没有经过 native event 重算的对象继续组合。本文记录把 native rebind 接入 preflight 的零调用修复。

## 实现

修改：

- `scripts/peerrolebench_pipe1_preflight.py`
  - 新增 `pipe1-adapter-rebind-bundle-v1` 输入合同；
  - 读取 `adapter_result`、`native_events`、`adapter_request`；
  - 调用 `validate_adapter_route_join` 重新计算 native projection；
  - 将 `adapter_route_join` 单独列为 preflight check；
  - 新增 `--adapter-bundle` 和 `--require-adapter-join`；
  - 历史 v2 调用仍可读取，只有新调用显式要求 rebind 时才把缺失 bundle 阻断为 `BLOCKED`。

- `tests/test_peerrolebench_pipe1_preflight_route_receipt.py`
  - 缺失强制 bundle；
  - 合法 bundle 与 route receipt 一致；
  - 序列化结果篡改 chosen peer 后，native join 返回 `UNKNOWN`，preflight 返回 `FAIL`。

## 验证

执行前写入配置和 JSONL 运行记录：

`experiments/logs/n03_pipe1_preflight_rebind_20261008_v1/`

- 命令：`python3 -m pytest -q tests/test_peerrolebench_pipe1*.py`；
- 结果：`44 passed`；
- API/generator/candidate/GPU：均为 `0`；
- `scientific_claim_allowed=false`；
- 历史结果未修改；
- 初次测试中发现的 `CandidateRegistryEntry` 无法直接 JSON 序列化问题已作为 fixture 序列化错误保留在 `raw.jsonl`，修复为写入 registry payload 后重跑通过。

## 端到端回执补充

随后补充了 full preflight 状态机测试，单独保存在
`experiments/logs/n03_pipe1_preflight_rebind_20261008_v2/`：

- `python3 -m pytest -q tests/test_peerrolebench_pipe1*.py`：`46 passed`；
- strict mode 缺少 bundle 在完整 receipt 中为 `BLOCKED`；
- 合法 bundle 在完整 receipt 中留下 `adapter_route_join=PASS`；
- 即使 rebind 通过，整条 PIPE1 preflight 仍为 `BLOCKED_PRE_EXECUTION`，因为后续真实执行前置条件仍未满足。

## 结论边界

这只证明 preflight 的组合边界会重新绑定 native selection/evidence/source index；它没有证明真实 source→target 执行、模型判断、责任标签、later-use、baseline parity、成本或方法收益。PIPE1 仍是候选路线，科学投稿 gate 不变。

## 下一步

在任何真实 API 预算之前，仍需完成 provider/timezone pin、精确 scorer、完整 source→artifact→target ledger、独立 root、same-information baseline parity、later-use 与完整成本合同。此回执不能单独触发 live runner 或 A800。
