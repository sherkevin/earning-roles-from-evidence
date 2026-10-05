# N03-next-r5.70：C0 candidate parity hardening

日期：2026-10-05
状态：`PARTIAL`（hardened candidate preflight 通过；live/scientific parity 未开始）
`goal_change_requested=false`

## 为什么需要这一轮

r5.69 的 C0 只证明了两个 policy 的基础 input digest 和 namespace 隔离。独立复核指出还
缺少四个可审计约束：arm namespace 的唯一性、policy config 的运行时绑定、shared state
cap，以及 chosen candidate/outcome/feedback 的错绑拒绝。另一个具体问题是 fixture 实际
schema 为 `matrix-features-v1`，而 candidate config 错写为 `hash64-v1-public`；这说明
如果不预绑定 schema，baseline 会在第一次输入时自我接受错误版本。

## 保留的失败

v2 运行只写入 config，随后在 policy construction 前失败：

- error：`ValueError: feature schema does not match policy`；
- runner_started=`false`，policy_updates=0，0 API/0 GPU；
- 失败回执：[`failure.json`](../../../experiments/logs/n03_c0_candidate_parity_qualification_20261005_v2/failure.json)。

该失败没有覆盖或改写 v1/v2 历史文件。

## v3 修复与冻结

v3 将 comparator 绑定到 fixture 的真实 schema `matrix-features-v1`，并固定：

- `hash64-v1`、64 维、temperature=1、exploration=0；
- linear ridge config、RARE window/reservoir/pending capacity；
- receipt-level state cap `1 MiB`；
- 每个 arm 的 policy version、factory 和唯一 namespace digest；
- outcome 只在选择完成后生成，ID 由 namespace、offer 和 chosen key 哈希绑定；
- feedback 必须携带匹配 namespace，不能跨 arm 更新。

## 结果

v3 回执：
[`summary.json`](../../../experiments/logs/n03_c0_candidate_parity_qualification_20261005_v3/summary.json)
，逐 policy 原始记录：
[`raw.jsonl`](../../../experiments/logs/n03_c0_candidate_parity_qualification_20261005_v3/raw.jsonl)。

7/7 cases 通过：正例公共 input digest 相同、两臂各自 selected-only update、独立 outcome
namespace、state cap/snapshot replay，以及以下六个负例均在 runner 启动前 UNKNOWN、0 update：
public input digest mutation、duplicate namespace、factory mutation、state-cap mutation、
chosen-key mutation、cross-arm feedback。

这仍然是 candidate-only CPU qualification。outcome 只是 namespace receipt，不是交付质量、
recipient adoption、later assignment 或真实 label；`baseline_frozen=false`，
`scientific_claim_allowed=false`。

## 下一步

将 v3 的 card/namespace/schema/state-cap 校验接入 canonical live runner，并把选择结果
接到每个 arm 自己的真实 delivery、recipient judgment/use/repair、adoption、later
assignment 和 terminal outcome。只有独立 outcome 真正由 chosen candidate 决定后，才能运行
一条有界 PIPE3 development API stream；当前不启动 A800，也不把 C0 写成 RARE 优势。
