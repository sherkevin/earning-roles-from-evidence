# PIPE3 baseline parity card v0.2 — candidate contract

日期：2026-10-07
状态：`DESIGN_ONLY / CANDIDATE_NOT_FROZEN`
对应 Goal：ER-G1–ER-G4；不修改 Goal，不解冻 benchmark，不启动 API/A800。

## 为什么做这一步

当前最主要的科学缺口不是继续增加 adapter glue，而是让 benchmark、baseline、信息边界和
统计单位在同一条可识别的 live 流里闭合。旧卡把 `contextual_trust` 写成 strongest
control，但它没有消费 RARE 的公共 `phi`；旧的 `contextual_trust` 只能保留为 diagnostic。
本卡把 `contextual_trust_linear` 明确为同信息 strongest comparator，并把 closest
published adapter 的 `NO-GO` 变成显式矩阵行，禁止静默遗漏。

## 本卡冻结的候选合同

- 主轨仍为 ArtifactRole，开发候选 root 为 `PIPE3_stream_processing`；当前没有确认 root。
- 臂集合固定为 `uniform`、`no_update`、`raw_acceptance`、`terminal_only`、
  `contextual_trust_linear`、`pooled_controller`、`RARE` 和 `Meta-Team-L2-public`。
- 所有臂共享 candidate registry/menu、材料、可见 read cut、arrival、propensity、预算、
  sandbox/scorer 和完整成本字段；每臂拥有独立 policy/history/output namespace。
- `contextual_trust_linear` 读取与 RARE 相同的公共 `phi`、menu、base score、arrival、
  propensity 和 cost，使用预注册 feature-aware diagonal RLS；context-only Beta arm 只作
  diagnostic，不承担 strongest-control 结论。
- `Meta-Team-L2-public` 只有在 profile parser、公开信息边界、assignment consumer、
  成本和 independent history 都能执行时才可进入；否则必须保留一行 `NO-GO`，不能删掉后
  声称完成 published baseline。

## 识别与统计要求

事件顺序必须是 delivery → Qp/J/A/Y → typed observation/attribution gate → public
publication → later assignment（在 target selection 前）→ target action/use → 独立 later
outcome → selected-only delayed credit。recipient-only、mixed、资源失败、绑定不完整和
scorer 覆盖不足都进入 `UNKNOWN/no-update`，并保留在分母。结果单位是独立 live stream，
而不是把同一 stream 的 episode 行当作独立样本；主结果按 stream 聚类给出 95% 区间。
确认阶段需要第二个 structural root，除非在执行前另有精度分析并共同确认。

必须同时报告 source quality、future utility/adoption/rework/regret、完整成本、在线
p50/p95、state bytes、service lag、旧 root 遗忘/恢复、UNKNOWN 率和 replay 一致性。少于
这些字段的结果不能打开 benchmark/baseline 科学闸门。

## 零调用验证

配置先写入 `experiments/logs/n03_baseline_live_parity_candidate_v0.2_20261007/config_snapshot.json`，
随后进行了 14 项 JSON/时序/矩阵一致性断言：通过。原始回执、配置哈希和摘要见同目录的
`validation.json` 与 `summary.json`。本次 `0` API、`0` generator、`0` candidate、`0` GPU、
`0` policy update；这只是合同验证，不是 benchmark 结果。

## 与 Goal 的差距

这一步把“应当比较什么、如何公平比较、什么情况必须 UNKNOWN”写成了单一候选卡，关闭了
旧卡中 strongest baseline 名称歧义和 closest adapter 静默缺失问题。它没有解决 benchmark
authority、第二 structural root、真实 later-use、真实成本、独立历史或方法收益，因此
G3/G4/G5 仍为 `OPEN`。下一次进入真实 API 前，必须先逐项解除 activation blockers，并
重新审查是否获得新的实验预算。

证据：[`n03_baseline_live_parity_candidate_v0.2.json`](../../../configs/aamas2027/n03_baseline_live_parity_candidate_v0.2.json)，
[`validation.json`](../../../experiments/logs/n03_baseline_live_parity_candidate_v0.2_20261007/validation.json)。
