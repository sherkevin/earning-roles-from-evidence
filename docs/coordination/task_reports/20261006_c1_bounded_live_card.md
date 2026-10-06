# N03-next-r5.74 — C1 bounded PIPE3 live development card

- **日期：** 2026-10-06
- **状态：** `PARTIAL`
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

## 真实 API 运行回执

第一次启动尝试写入 `n03_c1_pipe3_bounded_live_20261006_v1/`，在任何 API 请求前因相对卡片路径
记录错误退出；该失败以 `startup_failure.json` 保留，API 请求数为 0，没有进入结果分母。

修复路径处理后，v2 真实运行共完成 10 个 `内部/qwen3.8-max` 请求（全部 HTTP 200、`end_turn`，
12,009 input tokens、6,184 output tokens，112.21 秒），但事后严格 ledger replay 发现：第三次
预执行选择被写成了没有后续 task 的因果选择，且 `no_update` 没有控制性 evidence record；v2
因此不能作为完整链条。原始数据保留在
[`n03_c1_pipe3_bounded_live_20261006_v2/`](../../../experiments/logs/n03_c1_pipe3_bounded_live_20261006_v2/)。

修复后 v3 再次使用同一冻结卡、同一真实 API 预算完成 10 个请求（全部 HTTP 200、完整 usage，
11,957 input tokens、5,938 output tokens）。结果如下：

| arm | API 请求 | 严格 replay | 延迟更新 | 运行状态 |
|---|---:|---|---:|---|
| `no_update` | 4 | PASS / complete | 0 | `COMPLETE_DEVELOPMENT_ONLY*` |
| `contextual_trust_linear` | 2 | 未形成完整 source chain | 0 | `UNKNOWN` / promotion blocked |
| `RARE` | 4 | PASS / complete | 1 | `COMPLETE_DEVELOPMENT_ONLY*` |

`*` 表示 protocol/API development chain complete，不表示 card 的完整 cost contract 已完成；
`scorer_seconds`、`update_seconds` 和 `state_bytes` 没有形成明确的汇总字段，因此 v3 不能用于
cost-sensitive policy comparison。

`RARE` 的源证据来自预注册的 `peer-b@v1` producer defect；目标反馈为 selected-only recipient
judgment，延迟 1 个 decision，到达后执行 1 次更新。更新前概率为 `[0.5, 0.5]`，更新后为
`[0.5305766310, 0.4694233690]`，第三次选择的 preview 为 `peer-c@v1`。这只是单一 PIPE3 root
上的实时接缝和状态改变回执；候选快照共享同一 model/tool envelope，不能解释为不同专家、不能
证明 peer specialization 或 benchmark 效果。v3 原始 response、ledger、scorer 输出和摘要均在
[`n03_c1_pipe3_bounded_live_20261006_v3/`](../../../experiments/logs/n03_c1_pipe3_bounded_live_20261006_v3/)。

独立复核确认 v3 的 10 个 `request_start/request_result` 一一对应，token 总数与报告一致；
`no_update` 的 16-event ledger 和 RARE 的 17-event ledger 均可独立严格 replay。context arm
在 source gate 前停止，没有独立的 completed `summary.json/ledger.json`，其 7-event 部分链和
停止原因保存在 root summary/raw 中，不能计入完成 episode 分母。

这里的 delayed update 有一个必须保留的信号边界：`RARE` 的更新 label 是后续 recipient
judgment 的 `accept=1.0`，而同一 later outcome 的 adoption quality 是 `0.5`。本卡验证的是
selected-only judgment channel 的一次状态更新，不是 terminal-quality 学习，也没有证明更新
带来质量改善。成本字段也尚未闭合：当前 `ConsumerAction.repair_cost` 对 `use` action 仍记录
action 调用耗时，汇总层缺少完整的 wall/scorer/update/state-byte 聚合；这些必须在后续正式
benchmark card 中修正或明确命名，不能直接作为 repair-cost 结论。随后已在 runner 中修正
`use` 的未来记录为 `repair_cost=0` 并保留 `action_wall_seconds`；v3 历史日志不改写，新的
成本汇总仍需在下一张版本化 card 中补齐。

还有一条 lineage 限制：`Feedback.source_event_id` 使用 policy-side
`policy-selection-RARE-1`，native ledger 中对应的是 `selection-RARE-1`；当前 replay 通过
assignment/task index 和候选一致性验证，但没有把这两个 event ID 做成同一条加密绑定。因此
v3 只能证明有一次可审计的 delayed update seam，不能声称已完成强 selected-only feedback
lineage。正式 benchmark card 必须加入 policy-selection ↔ native-selection sidecar 绑定及其
mutation rejection。

## 真实运行暴露的科学问题

`contextual_trust_linear` 在 source judgment 中被模型标成 `target_role=recipient`，因此严格
责任 gate 拒绝发布 producer role evidence；同一冻结输入下另外两臂得到 `target_role=producer`。
这说明当前 gate 对模型责任字段的随机响应敏感，三臂并未形成可直接比较的同一完成样本。它是
测量/责任归属问题，不是支持某个 selector 更好的结果。下一步应先完成离线的
“结构化 ownership contract 与模型 judgment 的分离”设计审查，再决定是否需要新的实时卡；在此
之前不把 v3 提升为 scientific baseline 或 A800 训练证据。

## 与 Goal 的对照

- 满足（工程子门）：真实 API 接通；每臂独立 namespace/state；source→delivery→judgment→action→
  outcome 可落盘；`RARE` 完成一次 delayed update seam；v3 的已完成 protocol ledger 可独立严格重放。
- 部分满足（G2/G3/G5）：单 root 的 live seam 已可运行，但 `contextual_trust_linear` 被 gate 阻断，
  没有三臂同一完成集，也没有跨 root、later-use 泛化或 peer specialization 证据。
- 未满足（G1/G4/G6/G7）：benchmark 冻结、强 baseline parity、独立结构 root/confirmation、
  scientific efficacy 和论文 submission gate 均保持开放。
- `Goal change requested=false`；没有因失败降低目标。

## 真实运行后的判定

只有真实响应通过 SSE 完整性、公开 judgment schema、action writable-path、三类 scorer 和
protocol ledger replay，才将对应臂标为 `COMPLETE_DEVELOPMENT_ONLY`；成本字段仍需单独审计。
任一臂失败仍保留完整原始响应并标为 `UNKNOWN`。即使三臂都完成，本卡也只能关闭“单 root live development seam”；独立 root、
confirmation split、few-shot/temporal 泛化、完整 baseline parity 和 scientific efficacy 仍未通过。

因此本卡整体状态保持 `PARTIAL`：两条 arm 关闭了开发链工程子门，一条 arm 的责任 gate 暴露了
可重复比较前必须先解决的测量问题；没有把任何结果提升为论文科学结论。
