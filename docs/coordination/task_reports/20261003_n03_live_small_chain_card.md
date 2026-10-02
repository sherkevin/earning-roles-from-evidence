# N03 真实小链 experiment card

日期：2026-10-03  
状态：`DESIGN_ONLY / NOT_RUN`。

## 本轮完成

基于 N02 严格回放和 PIPE3 现有 qualification seam，写入候选卡
[`n03_pipe3_real_closed_loop_card_20261003.md`](../../research/candidates/n03_pipe3_real_closed_loop_card_20261003.md)。
它把下一次真实 API 运行限制为一个 development seed、最多两个 episode、每 episode
producer/judgment/action 三次请求、无重试；只验证责任反馈是否可识别和可重放，不做
训练效果或 A800 实验。

卡片明确了必须在真实执行中记录的 Qp、judgment、ownership diff、independent outcome、
UNKNOWN 原因和 source-bound preview→assignment→commit，不允许手写 later assignment
或从 recipient outcome 反推 producer label。

## 为什么现在不直接运行

N02 已经证明 API transport 可用，但其 producer score 缺失；PIPE3 的零调用 runner 已
证明 scorer/action/offer 接缝可运行，真实 runner 尚未把这三者与 API actor 组合。直接
运行会把 runner seam、责任 gate 和 API 失败混在一起，无法解释结果。先把 card 和
现有 PIPE3 seam 对齐，下一小步才是实现 runner 的最小 branch；实现后先做 zero-call
replay，再决定是否消耗一个真实 API episode。

## Goal 对照

| 标准 | 状态 |
|---|---|
| 真实 situated judgment→attribution | `DESIGN_READY / NOT_RUN` |
| 两个 root 与 baseline parity | `OPEN` |
| online update/backbone/A800 | `NOT_RUN` |
| 论文科学结果 | `NOT_READY` |

`goal_change_requested=false`。本任务不修改 active benchmark、method、故事线或 Goal。
