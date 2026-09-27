# Task report：neutral DIST1 v2 live episode / 2026-09-27

状态：`UNKNOWN`（真实 API 链完成生成，但 producer scorer 覆盖不完整；没有 role
evidence、future assignment 或 controller update）；`goal_change_requested=false`。

## 运行条件与预算

使用已提交的
[`n03_peerrole_dev_neutral_v2.json`](../../configs/aamas2027/n03_peerrole_dev_neutral_v2.json)，
`dist1-neutral-v2` 公开接口，provider `内部`、model `qwen3.8-max`、thinking disabled，
seed 0。准备阶段已经通过 adapter/provenance/runtime/scorer 的零调用门；本次只发一个
episode，未发 seed 1，也未启动 PIPE3 或 GPU。原始证据目录为
[`n03_peerrole_dev_neutral_v2_prepare_20260927`](../../experiments/logs/n03_peerrole_dev_neutral_v2_prepare_20260927/)。

三个真实 API 请求均 HTTP 200、`end_turn`、usage 完整：

| stage | wall(s) | input | output |
|---|---:|---:|---:|
| producer | 10.349 | 958 | 529 |
| judgment | 7.429 | 1,688 | 294 |
| consumer | 5.586 | 1,975 | 356 |
| total | 23.364 | 4,621 | 1,179 |

## 观察到的真实行为

producer 返回了 queue/priority 的完整源码，已经采用 v2 公开契约的
`get() -> (message, receipt)`、`ack` 和 `nack`。recipient 的 judgment 为
`accept_with_rework`，置信度 `0.95`，明确指出原 consumer 未解包 tuple、未确认 receipt、
未在异常时 nack。consumer 只修改了 `mqueue/consumer.py`，实现了解包、成功 ack、失败
nack 和只记录 message。

这说明 v1 暴露的接口歧义在 v2 文本中已被模型读取并用于实际修复；但它不等于 producer
质量标签，也不等于角色学习收益。

## 为什么仍然是 UNKNOWN

producer-only scorer 的 P2、P3、P4、P7 通过；P1、P5、P6 返回 `UNKNOWN`，原因是模型
生成的 `PriorityTask` 把带 default 的 `_seq` 放在无 default 的 `message` 之前，导致
dataclass 定义在导入时抛出：`TypeError: non-default argument 'message' follows default
argument`。这不是 scorer timeout，也不是公开 v2 contract 的返回顺序问题，而是候选
producer 输出的可执行性缺陷。由于 scorer 的 coverage 不完整，`label=null`；不能把它
当作 producer 的负标签，也不能用 consumer 的下游结果替代 producer correctness。

runner 在本次生成后停在 `awaiting_source_review`。随后补上的 runner guard 明确规定：
有 producer scorer 的 card 若返回 UNKNOWN、缺 coverage 或缺 label，就在 evaluate 前关闭
episode，禁止追加 terminal outcome、role evidence 和 controller update；这落实了
[ADR 0030](../../user/decisions/0030-unknown-scorer-boundary.md)。本次没有执行 evaluate，
因此没有伪造完整链，也没有把 `accept_with_rework` 写成学习信号。

## Goal 对照

| 标准 | 状态 | 说明 |
|---|---|---|
| 真实 API 与交付/判断链可审计 | `PARTIAL` | 三次真实请求、raw SSE、源码、digest、ledger 6 事件均保存 |
| 公开契约与模型交互可执行 | `PARTIAL` | queue/ack/nack 被正确理解；priority 生成仍有可执行性错误 |
| producer label 可更新角色证据 | `OPEN` | scorer coverage 不完整，按规则无 label/evidence/update |
| recipient judgment 的 situated 信息价值 | `OPEN` | 没有 terminal outcome，不能比较 baseline |
| benchmark/root/baseline 冻结 | `OPEN` | candidate manifest 仍未冻结，PIPE3 未确认 |
| RARE、实时更新、遗忘和 A800 | `OPEN` | 没有科学效果或训练证据 |

## 决策与后续

本 episode 的 API 路径只保留为“v2 契约能被真实模型读取、但当前 producer 输出仍会
触发 scorer coverage UNKNOWN”的诊断证据。该 integration card 不再补请求；v1 UNKNOWN
与本次 v2 UNKNOWN 不合并。下一步应先在离线材料中修正/扩大 producer scorer 对
dataclass/source-import 错误的 disposition，并完成第二 root 与强同信息 baseline 的
资格门；只有获得完整、可解释的标签链后，才讨论 N04/N05 的方法和 A800。
