# 0027：recipient payload 与 selected delivery 的 IPC 探针通过

日期：2026-09-27。
状态：Accepted as a bounded runtime diagnostic。

## 背景

0025 只验证了一个 producer payload 的 sandbox RPC 可见性。Goal ER-G3 还要求 recipient
看到真实选中的 delivery，且 delivery 路径、版本和 digest 能绑定到 selection/lineage。

## 结果与决定

新增 16 KiB 有界 RPC（原 4 KiB 上限保留为默认值）后，seed-0 的 recipient payload 和
producer-owned selected delivery 通过 pinned sandbox 到独立 worker。worker 验证了
recipient allowlist、delivery SHA-256 和 payload role；读取临时 operator-only ledger
被拒。父进程同时生成 selection→delivery→recipient-dispatch 的 hash-chain fixture，
event ID 唯一且 lineage 绑定通过。

因此本次 `recipient_dispatch_verified=true`、`runtime_lineage_probe_verified=true`。
这仍不是 LLM agent 执行、hidden scorer 隔离、真实 ledger replay 或 benchmark 资格；
`scientific_claim_allowed=false` 保持不变。后续必须覆盖真实 producer/recipient 输出、
多事件/异常路径和 actual runner 的 scorer/ledger 边界。
