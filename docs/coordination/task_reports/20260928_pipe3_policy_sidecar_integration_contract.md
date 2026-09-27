# 2026-09-28 PIPE3 policy-sidecar integration contract

本任务把已通过离线资格的 sidecar/manifest/replay 具体化到未来 PIPE3 runner 的 seam：
selection、delivery、recipient judgment、terminal outcome、replay-before-update 和
snapshot publish。重点是把 producer contract、recipient 自有 integration、adoption、
terminal label 和 UNKNOWN 分开，避免再次把正常 consumer repair 当成 upstream failure。

这只是设计 contract；没有启动 API、Nebula、GPU，也没有改变历史 N02 ledger 或 Goal。
详细字段和 Gate 见 n03_pipe3_policy_sidecar_integration_contract_20260928.md。

## Goal 对照

| 标准 | 状态 | 原因 |
|---|---|---|
| 故事线与责任语义 | MAINTAINED | 明确 situated judgment、责任归因和 future assignment 的接口边界 |
| benchmark/scorer 可复现 | OPEN | PIPE3 尚未从真实 runner 生成 sidecar/manifest |
| baseline 公平比较 | OPEN | policy snapshot、信息和成本共享尚未接入 live episode |
| 实时训练/效果/A800 | OPEN | 本任务没有真实 API/GPU 或科学结果 |
| Goal 变更 | UNCHANGED | 没有降级或修改请求 |

## 下一步

先做 root-specific PIPE3 runner seam 的零 API fixture：实际生成 selection/delivery/
judgment/outcome sidecar 和 manifest，并通过相同的 canonical replay；只有这个 fixture 和
独立 scorer IPC 资格通过，才重新评估是否值得用极小真实 API 链验证 label 信号。
