# PIPE1 adapter–route native rebind — 2026-10-08

状态：`QUALIFIED_ZERO_CALL_NATIVE_REBIND`

## 目的

独立审查发现，上一版 adapter–route join 只比较调用者提供的 adapter 结果与 route
receipt。若 adapter 结果在序列化后被篡改，内部的 chosen peer、evidence id 或
source-task index 可能与真实 ledger 脱钩，而 join 仍可能返回 `READY_FOR_PREFLIGHT`。
这会直接破坏责任归因，因此在任何 route preflight 前必须重新绑定原始事件。

## 修复

`scripts/peerrolebench_pipe1_adapter_route_join.py` 升级为
`pipe1-adapter-route-join-v2`：

- `native_events` 和完整 `adapter_request` 现在是 `READY_FOR_PREFLIGHT` 的必要输入；
  缺失时统一返回 `UNKNOWN`；
- join 内调用现有 `validate_source_target_fixture` 重新计算 native adapter；
- 逐字段比较 status、route readiness、更新边界、task identity、selection input、
  selection binding、source-target schedule 和 ledger snapshot；
- chosen peer、evidence ids、assignment 与 source-task index 的事后篡改都会被拒绝；
- `route_valid` 仍只表示可以进入下一道 preflight，不表示 attribution-ready、收益可用、
  真实 route 已执行或允许 policy update。

历史 v1 代码和回执没有被改写。

## 零调用验收

配置和原始输出保存在
`experiments/logs/n03_pipe1_adapter_route_rebind_20261008_v1/`。

- targeted adapter/offline suite：16 passed；
- route receipt、PIPE3 contract 回归：合计 41 passed；
- `py_compile` 通过；
- 缺少 native revalidation 输入：fail-closed；
- 篡改 chosen peer：fail-closed；
- 篡改 evidence/source index：fail-closed；
- API 0、generator 0、candidate execution 0、GPU 0、policy update 0；
- `scientific_claim_allowed=false`。

## Goal 对照

本轮关闭了一个会使责任链被伪造的工程资格漏洞，但没有增加 benchmark root、真实
recipient judgment、later-use、独立 future outcome、baseline parity 或在线训练效果证据。
PIPE1 仍是候选且未激活；科学投稿 gate 不变。
