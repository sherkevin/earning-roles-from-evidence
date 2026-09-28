# N03 PIPE3 policy-sidecar integration contract

日期：2026-09-28
状态：DESIGN_READY / NOT_RUNNER_INTEGRATED
前置：n03_policy_sidecar_schema_20260928.md、n03_policy_sidecar_stream_replay.md。

这份文件只规定真实 PIPE3 runner 以后怎样接入已经通过离线资格的 sidecar；它不把
当前 DIST1 runner 的旧事件补默认值，也不冻结 PIPE3 benchmark 或 baseline。

## 1. 事件边界

### Selection

在 task start 前，selector 根据公开 task context 和候选菜单调用 policy，生成完整
DecisionSidecar：候选 ID/version、base score、概率、chosen index、propensity、
state/model/schema/RNG 版本和 selected_at。同一字段同时用于 actor 的实际 dispatch
和 policy 的 replay；runner 不允许重新采样一个“等价”选择。

随后只写原生 peer_selection ledger event 和一条对应的 manifest record。manifest
保存 sidecar digest、ledger record hash、protocol event type/id，并按 episode 顺序形成
独立 hash-chain。sidecar payload 不直接注入原生 dataclass，避免破坏 protocol replay。

### Delivery and recipient judgment

producer_delivery 必须引用 selection ID，producer ID/version 必须等于 chosen candidate。
交付 artifact digest、producer contract score、recipient action 和 recipient judgment 分开
记录；正常的 recipient 自有 processor/sink 工作不能直接改写 producer label。

recipient 在 terminal scorer 运行前生成 FeedbackSidecar(disposition=unknown)，只保存
decision/raw observation 和责任 lineage，不携带 policy label。它可以被用于审计，但不能
调用 observe_feedback。

### Terminal outcome

只有独立 scorer 完成、责任关系满足、label mapping 版本已预注册且 provenance=public
时，才生成 eligible public terminal sidecar。其 arrived_at 和 delay 必须与 selection
的 selected_at 一致；producer ID/version 必须与 chosen candidate 一致。任何 scorer
timeout、权限错误、覆盖不完整、artifact mismatch 或责任不确定都写 UNKNOWN/INVALID，
不更新 policy。

## 2. 更新闸门

episode 的合法顺序固定为：

canonical ledger replay
  -> sidecar record/event/digest validation
  -> manifest hash-chain validation
  -> producer/recipient/action/artifact responsibility gate
  -> feedback arrival-order replay
  -> policy update

replay_policy_sidecars 已经实现前四项中的 ledger/sidecar/manifest 部分以及反馈排序、
UNKNOWN no-update；传入 `require_responsibility_lineage=true` 时还执行 v3 的 delivery/action/
artifact 逐跳 lineage 检查。真正 runner 还必须把 sidecar 和 manifest 在每个 episode
结束时封存，再把同一 snapshot 交给所有 baseline；不能让某一 baseline 看到 private scorer
或另一个 baseline 尚未收到的 future outcome。

## 3. Runner 接入位置

当前 peerrolebench_real_closed_loop.py 是 DIST1 历史 runner，不能直接宣称已支持该
contract。PIPE3 root-specific runner 应增加以下显式 seams：

1. select_peer(...) -> DecisionSidecar：只在 dispatch 前调用；保存 sidecar 与 manifest。
2. seal_delivery(...)：绑定 producer/version、artifact digest 和 selection ID。
3. seal_judgment(...)：保存 recipient 的 raw decision/action plan，label 仍为空。
4. seal_terminal_outcome(...)：经过独立 scorer/责任 arbiter 后再填 public label 或 UNKNOWN。
5. replay_before_update(...)：调用 canonical ledger + manifest replay；失败返回 UNKNOWN/INVALID。
6. publish_snapshot(...)：原子保存 policy state、manifest root 和 episode watermark，供后续
   task 读取，避免 half-written update。

每个 seam 都必须有 version/hash，且能在零 API fixture 中重放。当前 seed-0 fixture 已经
用 pinned PIPE3 material adapter 走通 producer delivery、recipient action、strict ledger、
sidecar 和 manifest replay；这只证明接口连通，不是 scorer 或科学效果。不得先改 live runner 再用
历史 N02 ledger 伪造这些字段。

## 4. 不同项目共享与不共享

Peer select 和 tool select 可以共享 DecisionSidecar、manifest、delay/UNKNOWN/replay、
snapshot/update API；两者仍分别提供 candidate identity、label mapping、scorer、action
cost 和 benchmark split。共享底层事件接口不能把 tool execution correctness 当作 peer
responsibility evidence，也不能把两个项目的结果合成一个主指标。

## 5. Gate 与 Goal 对照

| Gate | 当前状态 | 解锁条件 |
|---|---|---|
| sidecar schema/manifest/replay | QUALIFIED_OFFLINE | 已有 170 tests 与五格 strict fixture |
| PIPE3 source/material/scorer/IPC | OPEN | root-specific runner 真正生成上述事件并通过独立进程资格 |
| baseline parity | OPEN | 同一 snapshot、信息、探索、预算和 task-root split |
| real LLM chain | CLOSED | 不能在前述 gate 通过前启动新的 PIPE3 API 链 |
| A800 training | CLOSED | 先有真实 signal 和明确训练瓶颈 |

Goal v1.0 未修改；这份 contract 只是把下一道证据门写清楚，不能替代 benchmark freeze
或方法效果。
