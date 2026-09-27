# 0025：单 producer payload 的 IPC 可见性探针通过

日期：2026-09-27。
状态：Accepted as a bounded runtime diagnostic。

## 背景

ADR 0024 要求证明材料适配器生成的 payload 真的能进入候选进程，并且 operator-only
ledger 不会随 payload 暴露。此前只有静态 digest，没有 runtime dispatch 证据。

## 结果与决定

运行 [`n03_pipe3_payload_runtime_preflight_20260927`](../../experiments/logs/n03_pipe3_payload_runtime_preflight_20260927/)
后，单个 seed-0 producer payload 通过现有 pinned sandbox 的 stdin/RPC 到独立 worker：
worker 解析了角色、source-files 和数量，且读取临时 operator ledger 得到拒绝。
因此该次 `payload_dispatch_verified=true`、`runtime_dispatch_verified=true`。

这只证明一个 producer payload 的候选可见性边界。它没有证明 recipient payload、
真实 agent 代码、hidden scorer、operator ledger replay、exact-once lineage 或
benchmark 资格；`scientific_claim_allowed=false` 保持不变。下一步仍需在版本化
runner 中覆盖 producer/recipient 两种 payload、delivery attachment、多事件/异常
路径和真实账本回放。
