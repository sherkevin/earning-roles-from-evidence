# PIPE2 typed handoff descriptor qualification

日期：2026-10-08。结果：`QUALIFIED_OFFLINE`；8 项定向检查通过，0 API、0 GPU、0
policy update。它是 schema/lineage 工程子门，不是 PIPE2 benchmark 资格、在线学习或
论文效果结果。

## 做了什么

针对 [compatibility audit](20261008_pipe2_observation_bridge_compatibility.md) 的
实际缺口，新增候选 descriptor：

- [implementation](../../../scripts/peerrolebench_pipe2_handoff_descriptor.py)
- [tests](../../../tests/test_peerrolebench_pipe2_handoff_descriptor.py)
- [candidate design](../../research/candidates/pipe2_typed_handoff_descriptor_v0.1_20261008.md)
- [config](../../../experiments/logs/n03_pipe2_handoff_descriptor_qualification_20261008_v1/config.json)
- [raw JSONL](../../../experiments/logs/n03_pipe2_handoff_descriptor_qualification_20261008_v1/events.jsonl)
- [summary](../../../experiments/logs/n03_pipe2_handoff_descriptor_qualification_20261008_v1/summary.json)

descriptor 分开封存：

1. producer `candidate_source_digest`；
2. PIPE2 opaque `artifact/extracted_rows.json` 的 path/schema/artifact digest；
3. producer contract、recipient pre/post manifest 与 changed-path digest；
4. J/A/source completion 的 identity，以及 future target/read-cut；
5. public projection 只暴露交付身份和时间，不暴露 recipient manifest 或 producer contract。

`delivery_artifact_sha256` 沿用 `validate_extracted_rows` 的 digest 语义，不能用 TeamBench
root digest、producer source digest、`output_sha256` 或 adoption status 代替。descriptor
本身强制 `policy_update_allowed=false` 与 `producer_credit_allowed=false`。

## 结果边界

测试覆盖 path/schema 不匹配、sealed digest 变化、source→target 时序、read-cut、changed
path canonicalization/traversal 和禁止 update/credit。8/8 通过。artifact digest 的新值
本身代表新的交付身份，只有在 runner 保持旧 sealed descriptor digest 或 external expected
digest 时才应被拒绝；测试明确记录了这个边界，避免把“格式合法”误报为“与历史交付一致”。

没有把 descriptor 接入 observation bridge、runtime replay 或 selector，也没有补写缺失
的 J/A/Y。当前 PIPE2 仍需真实 runner 记录 recipient pre/post manifest、显式 judgment、
action、独立 terminal outcome，并完成同信息 baseline parity；在此之前不调用真实
judgment/API/GPU。

## 三份标准对照

| 标准 | 本轮推进 | 仍未满足 |
|---|---|---|
| 故事线/创新 | 将“数据工件交接”和“责任观察”边界写成可检验接口 | 观察对后续责任分派的增量 |
| 方法论 | 固定 artifact/source/provenance 分离与 fail-closed 规则 | 合法 J/A/Y、延迟收益、实时/稳定/时效性 |
| benchmark/baseline | 为真实 PIPE2 可见性保留正确 adapter seam | root authority、live same-info parity、独立 histories、科学结果 |

因此本轮只关闭一个 descriptor 工程子门，Goal、active 文档、主版 PDF 和 scientific
submission gate 均未改变。
