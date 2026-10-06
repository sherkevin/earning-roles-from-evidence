# N03-next-r5.74 — C1 bounded PIPE3 live development card

- **日期：** 2026-10-06
- **状态：** `DESIGN_FROZEN_PENDING_REAL_RUN`
- **Goal change requested:** `false`
- **scientific_claim_allowed:** `false`

## 目的

C0 只验证了 RARE 与 `contextual_trust_linear` 的公共输入、候选命名空间和
snapshot/restore。C1 将它们和 `no_update` 放入同一条有限的 PIPE3 development stream，
让每个 chosen candidate 真正进入 delivery → recipient judgment → use/rework → adoption /
terminal outcome，并在合法 delayed credit 后记录第三次执行前选择。

这张卡只回答“单 root 的实时 runner 和第一条信息/assignment 接缝能否产生可审计记录”。
它不回答跨 root 泛化、peer specialization、benchmark 冻结或 RARE 的质量优势。

## 冻结合同

- root：TeamBench pinned PIPE3 `PIPE3_stream_processing`，seed 0；只有一个 structural root。
- arms：`no_update`、`contextual_trust_linear`、`RARE`；独立 policy state、raw log 和 outcome namespace。
- candidate menu：`peer-b@v1`（预注册 P2 serialization defect）与 `peer-c@v1`（对应修复快照）；
  两者共享 fixture model/tool envelope，不能解释为不同专家。
- source bootstrap：固定选择 `peer-b@v1`，先取得一个独立 producer-defect source episode；
  model 自报不具备标签权限。
- 每臂三次决策；每次最多一条 judgment 和一条 action API 请求；不重试、不替换任务。
- API：真实 `内部/qwen3.8-max`，thinking disabled，streaming，judgment 1024、action 2048。
- 公开输入：`matrix-features-v1`、64 维 bounded feature、同菜单、read-cut、arrival、propensity、
  state cap 和成本字段。
- 任何 digest、ownership、lineage、完整性或成本失败都写 `UNKNOWN`，不补标签、不改分母。

正式卡：[`n03_c1_pipe3_bounded_live_dev_v1.json`](../../../configs/aamas2027/n03_c1_pipe3_bounded_live_dev_v1.json)

## 零调用资格回执

确定性 actor 注入只用于 runner/ledger 合同测试，不是模型结果：
[`n03_c1_live_contract_qualification_20261006_v1/`](../../../experiments/logs/n03_c1_live_contract_qualification_20261006_v1/)。

- 三臂均完成 source gate、evidence publication、future assignment、delayed update 和第三次选择；
- `contextual_trust_linear` 与 `RARE` 各更新一次，`no_update` 更新为 0；
- 0 real API、0 GPU、`scientific_claim_allowed=false`；
- 定向测试：`tests/test_peerrolebench_c1_live_contract.py`，1 passed。

## 真实运行后的判定

只有真实响应通过 SSE 完整性、公开 judgment schema、action writable-path、三类 scorer、ledger
replay 和成本记录，才将对应臂标为 `COMPLETE_DEVELOPMENT_ONLY`。任一臂失败仍保留完整原始响应
并标为 `UNKNOWN`。即使三臂都完成，本卡也只能关闭“单 root live development seam”；独立 root、
confirmation split、few-shot/temporal 泛化、完整 baseline parity 和 scientific efficacy 仍未通过。
