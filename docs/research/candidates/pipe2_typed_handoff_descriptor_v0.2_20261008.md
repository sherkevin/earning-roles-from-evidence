# PIPE2 typed handoff descriptor v0.2（候选）

日期：2026-10-08。状态：`CANDIDATE / NOT ACTIVE / ZERO-CALL QUALIFIED`。

这是 v0.1 的兼容扩展，不改变 active method、benchmark 选型或 ADR0049。v0.1 的
`pipe2-typed-handoff-v1` 与既有资格化结果保持不变；新增实现使用独立的
`pipe2-typed-handoff-v2` schema，避免原地修改历史 payload。

## 1. 这次修正了什么

PIPE2 的交付是 `artifact/extracted_rows.json`，recipient 不接收
`pipeline/extract.py`。v2 仍把 producer source provenance、opaque delivery、recipient
source snapshots 与 later outcome 分开，但新增四项能让真实 runner 绑定事件的字段：

| 字段 | 约束 |
|---|---|
| `delivery_id` | 四个事件必须指向同一 delivery |
| `judgment/action` | 记录显式实际值；允许 J/A mismatch，保留 Scheme B 的 noisy observation |
| `*_event_index` | `delivery < judgment <= action <= outcome`，read cut 必须包含 outcome |
| `*_record_hash` | 记录 native ledger 的 sealed record hash；构造前必须提供四类事件引用 |

`outcome_status` 只接受独立 source outcome 的 `PASS/FAIL`；缺失或 UNKNOWN 不构造
descriptor。v2 不把 J/A 直接变成 producer credit，两个 update/credit flag 永远为
false。

## 2. 构造合同

```text
native ledger replay
  → delivery/J/A/outcome 四类事件引用与 hash
  → recipient pre/post source manifest（只含 transform/load/support）
  → opaque artifact path/schema/hash 独立绑定
  → v2 descriptor
  → 后续 observation/attribution gate（尚未接入）
```

`make_descriptor_from_snapshots` 只接受显式 `event_records` 和完整快照；它拒绝
缺 J/A/Y 事件、delivery ID 串线、错误时序以及将 `artifact/extracted_rows.json`
放入 source manifest。它本身不替代 canonical ledger replay，也不证明事件 hash 的
上游真实性；真实 runner 必须先 replay，再把 sealed 引用传入。

J/A 不强制一一映射。`accept + repair` 之类的组合可以被记录，因为观察的目的正是
保留 recipient 的判断与其实际行为之间的差异。是否属于某个 protocol action、是否
可进入后续 attribution，仍由原生 ledger 和责任 gate 单独判断；descriptor 不作奖励。

## 3. 已做的零调用验证

- 实现：[v2 descriptor](../../../scripts/peerrolebench_pipe2_handoff_descriptor_v2.py)
- 资格 runner：[v2 qualification](../../../scripts/peerrolebench_pipe2_handoff_descriptor_v2_qualification.py)
- 定向测试：[v2 tests](../../../tests/test_peerrolebench_pipe2_handoff_descriptor_v2.py)
- 配置：[qualification card](../../../configs/aamas2027/n03_pipe2_handoff_descriptor_v2_qualification_20261008.json)
- 结果：[v2 log](../../../experiments/logs/n03_pipe2_handoff_descriptor_v2_qualification_20261008_v2/)
- 首次遗漏 hash 的失败保留在：[v1 failed log](../../../experiments/logs/n03_pipe2_handoff_descriptor_v2_qualification_20261008_v1/)

v2 资格化读取了真实 PIPE2 derived adapter 的 seed-0 public material，并用真实
`validate_extracted_rows` 产生的 artifact schema/hash 做边界检查；19 项 v1/v2 定向
测试通过。v2 runner 使用的事件引用是明确标记的 synthetic contract fixture，**不是**
真实 recipient judgment、action 或 terminal outcome，因此：

```text
API calls = 0；GPU jobs = 0；policy updates = 0；scientific claim = false
```

## 4. 仍未关闭的科学门

1. 当前 PIPE2 runtime receipt 仍没有真实 J、A、independent Y 或 recipient pre/post
   snapshot，不能由现有 `output_sha256`/adoption 字段补写。
2. v2 还没有接 native ledger replay、observation publication、later assignment 或
   selector；benchmark 仍是 candidate derived root。
3. 还没有同信息 count-only/J-masked/terminal-only arms、独立 histories、完整成本和
   未见任务质量结果；不允许启动 A800 或填写论文效果表。

下一步是写一个版本化 runtime adapter：在一次有预算的真实 episode 中捕获 native
delivery/J/A/Y 与 recipient pre/post 快照，任何缺字段保持 `UNKNOWN`，然后用同一
menu/read-cut/arrival/propensity 重放一个 count-only 或 J-masked 对照。该 adapter
通过后才进入 N03 真实小流实验卡。
