# PIPE1 runner reuse audit — 2026-10-07

状态：`DESIGN_INPUT_ONLY`。子 agent 的审查请求因 429 限流没有产出；本报告由主 agent
直接读取现有源码完成。没有修改代码，没有调用模型、生成器、候选代码或 GPU。

## 可直接复用的模块

1. `scripts/peerrolebench_pipe3_live_contract.py` 是最接近 PIPE1 的零调用 contract：
   `validate_source_target_schedule()` 检查 assignment 早于 target selection/task start；
   `validate_ledger_key_binding()` 通过 `replay_ledger_events()` 检查 delivery、selection、
   producer score、judgment、action、outcome 的 artifact/peer 绑定；
   `validate_selection_receipt()` 检查 candidate registry、菜单顺序、概率、chosen index
   和 propensity；`classify_ownership()` 和 `unknown_no_update()` 可直接作为责任及
   UNKNOWN 分支的保守规则。证据：该文件第 47–70、73–99、102–125、128–165 行。
2. `scripts/peerrolebench_assignment_attestation.py` 已把“证据存在”和“选择前确实读取”
   分开：`AssignmentEvidenceOffer` 不携带 chosen peer/propensity，
   `build_consumption_attestation()` 与 `verify_consumption_attestation()` 绑定 offer、
   decision、state digest 和 read cut。它适合成为 PIPE1 的 selected-only 输入边界，不能
   直接替代真实 target assignment。
3. `scripts/peerrolebench_real_closed_loop.py` 可复用其外围生命周期：`append_event()`
   将 typed event 写入 ledger，`replay_gate()` 在更新/摘要前要求完整可重放链，
   `load_runner_materials()` 提供版本化 material adapter，`producer_score_gate()` 和
   `unknown_no_update` 语义可复用。它当前是 N02 的 producer/consumer runner，不应直接
   改写成 PIPE1 runner，否则会污染历史 card 与 frozen logs。
4. `scripts/peerrolebench_peer_history_binding.py` 的
   `build_history_binding_receipt()` 能在完整 native ledger 上绑定 source evidence、
   later assignment、target selection、target delivery/judgment/action/outcome 以及
   read cut。它只能在 target outcome 已封存后使用，不能提前生成 evidence 或充当 route
   receipt；当前实现还要求同一个 candidate key 和既有 `HistoryEntryV1`，需由适配层映射。

## 最小缺口

需要一个**独立的 PIPE1 adapter/runner**，按以下顺序消费现有模块：

1. 读取已绑定的 native seed 0/3 material 和 provider/TZ/budget card；
2. 由同一 append-only ledger 写入 source material/message/artifact/Executor/Verifier；
3. 在 target assignment 前生成 `AssignmentEvidenceOffer`，封存 selected-only read cut 与
   `DecisionConsumptionAttestation`；
4. 调用已有 `validate_selection_receipt()` 和 `validate_source_target_schedule()`，然后
   才允许 target selection/task start；
5. target 完成后调用 `validate_ledger_key_binding()`、`classify_ownership()`，再构造
   `HistoryBindingReceiptV1` 或显式 UNKNOWN；
6. 从同一 ledger 投影已通过的 `pipe1-route-receipt-v1`，并在出口执行
   `validate_pipe1_route_receipt()` 与 native material binding。

这个 adapter 是新的连接层，不是重写 ledger、attestation、history binding 或 runner
生命周期。它的第一版应只接受离线 event fixture；验收指标是合法顺序通过、任一 lineage/
read-cut/ownership/UNKNOWN mutation fail-closed，且 0 API/0 GPU。

## 尚不能复用的部分

- N02 `real_closed_loop.py` 的 `DECISIONS` 和 controller update 直接把 recipient action
  当成角色分数，违反方案 B 的 observation/attributable credit 分离，不能作为 PIPE1
  reward。
- `validate_ledger_key_binding()` 要求 producer score/judgment/action/outcome 已存在，
  因而只能是 terminal gate；它不能证明 source artifact 的实际质量或 producer 的因果
  责任。
- `peer_history_binding` 的 later credit 目前不检查完整目标修改归属、独立 Qp 和总成本；
  不能直接开启学习更新。

## 对 Goal 的影响

复用边界已经足够明确，下一步有意义的工作是实现上述零调用 adapter，并用 mutation
fixture 证明它不会把不完整 lineage 送入真实 route。当前仍没有 benchmark activation、
baseline parity、role-learning efficacy 或 A800 依据；科学投稿 gate 保持关闭。
