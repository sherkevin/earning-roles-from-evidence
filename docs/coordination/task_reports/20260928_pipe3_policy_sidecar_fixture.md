# 2026-09-28 PIPE3 policy-sidecar integration fixture

## 任务

验证 PIPE3 pinned material adapter 的真实 source ownership 与 sidecar/manifest/replay
contract 能否连通。只使用 seed-0 固定材料，不调用 LLM、scorer 或 GPU。

## 实际执行

命令：

    python3 scripts/peerrolebench_pipe3_policy_sidecar_fixture.py \
      --out-dir experiments/logs/n03_pipe3_policy_sidecar_fixture_20260928_v2

fixture 使用 PIPE3 的 producer.py、processor.py、models.py、sink.py，经
attach_pipe3_delivery、prepare_pipe3_action 和 validate_pipe3_action_result 生成实际
artifact digest；随后构造 strict PeerRoleLedger、UNKNOWN recipient judgment、terminal
fixture outcome、Decision/Feedback sidecar 和独立 manifest，调用同一 canonical replay gate。

提交 8fc5637 后的 v2 日志结果：

- passed=true，ledger/sidecar status 均 PASS；
- UNKNOWN judgment 不更新，terminal fixture 只更新 1 次；
- manifest root 为
  844ad362c195ce4a790a6fad8bc4c0dc8594cf1e17959cbb0f300dc6a44cf625；
- artifact digest 为
  1529b41e454f5a1f7c8c48a7366bd50fe58be8c91686e773d3afe9d7afc693a2；
- real_api_calls=0、gpu_jobs=0、scientific_claim_allowed=false。

## Goal 对照

| 标准 | 状态 | 说明 |
|---|---|---|
| PIPE3 source ownership→ledger→sidecar | QUALIFIED_OFFLINE | pinned seed-0 材料可以生成并回放完整结构 |
| benchmark/scorer 资格 | OPEN | 没有执行真实 producer/recipient 或独立 hidden scorer |
| baseline parity | OPEN | 只有 terminal-only fixture policy，没有比较矩阵 |
| 真实 LLM/实时训练/A800 | OPEN | 本任务无 API/GPU，也不提供科学效果 |
| Goal 变更 | UNCHANGED | 没有降级或修改请求 |

这个 fixture 证明的是接口连通，不是 PIPE3 已成为 benchmark，也不是 label 信号真实、
可靠或能提升角色分派。
