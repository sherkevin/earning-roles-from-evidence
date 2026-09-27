# Task report：producer-only scorer contract qualification / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。本轮把 producer 交付质量与
recipient 集成结果拆开，并完成一轮零 LLM 的 scorer qualification；没有把它写成
benchmark 分数、role-learning 效果或 Goal 降级。

## 1. 对照 Goal

- **ER-G3（归因安全、隐藏评分、可回放）**：部分满足。producer-owned 文件的 digest、
  独立 worker、response digest 和 UNKNOWN 语义已有可执行边界；producer-score event、
  ledger causal replay 和第二个结构 root 仍未完成。
- **ER-G4（真实、可审计实验）**：部分满足。本轮 fixture 配置、原始 response、失败/未知
  分类和源码 hash 均落盘；没有真实 LLM 请求，因此不支持科学效果结论。
- **ER-G1/ER-G2（situated judgment→future responsibility 与在线方法）**：未开始。本轮
  只修复观测和归因前置条件，不启动训练或 A800。

## 2. 运行前冻结与实际运行

冻结对象：pinned TeamBench `d185aef1916fd86a9ba554d581fd256319a973af` 的
`DIST1_queue_race` seed 0；producer 只拥有 `mqueue/queue.py`、`mqueue/priority.py`，
recipient 的 `consumer.py` 不进入 producer scorer；request schema、七项 check inventory、
digest 算法和 `PASS/FAIL/UNKNOWN` 规则见
[`docs/research/dist1_operator_producer_scorer_contract_20260927.md`](../../research/dist1_operator_producer_scorer_contract_20260927.md)。

实际运行是零 LLM、零 GPU、未调用 native `grade.sh` 的隔离 worker qualification：

- 原始 buggy source：`FAIL`，4/7 checks pass，目标缺陷包括 capacity、ack/nack 和
  equal-priority payload comparison；
- 独立手写 correct control：`PASS`，7/7，quality score 1.0；
- 只修 priority 的 near miss：`FAIL`，只通过 priority checks；
- 只修 queue ack 的 near miss：`FAIL`，仅 priority type-safety 失败；
- malformed source：`UNKNOWN`，没有负标签。

原始 JSONL、每个 private worker 的 response/launch 文件和 summary 保存在
[`experiments/logs/n03_producer_scorer_qualification_20260927/`](../../experiments/logs/n03_producer_scorer_qualification_20260927/)。
脚本与测试为 [`scripts/peerrolebench_producer_scorer.py`](../../scripts/peerrolebench_producer_scorer.py)、
[`scripts/peerrolebench_hidden_producer_scorer_worker.py`](../../scripts/peerrolebench_hidden_producer_scorer_worker.py)
和 [`tests/test_peerrolebench_producer_scorer.py`](../../tests/test_peerrolebench_producer_scorer.py)。

同时，对保存的 N02 v3 sealed recipient source 做了独立 consumer worker 回放：旧 parent
行为 scorer 是 `4/4 PASS`，独立 worker 返回 `FAIL`（`payload_and_ack`，0.75）。这是
诊断差异，不重写 N02 结果；它直接触发了 ADR 0032 的 producer/recipient outcome 分离。

## 3. 满足、部分满足与未开始

| 标准 | 状态 | 证据/边界 |
|---|---|---|
| producer-owned artifact digest 绑定 | `PARTIAL` | worker 回显并由 parent 校验 digest；尚未进入 live runner |
| source/near-miss 可区分 | `PARTIAL` | 五格矩阵通过；覆盖仍只有 seed 0 和七项手写 contract |
| scorer 失败不造负标签 | `PARTIAL` | malformed/worker/schema/digest 单测为 UNKNOWN；timeout/permission/IPC mutation 还需矩阵化 |
| recipient 自有集成与 producer 质量分离 | `PARTIAL` | 新 schema/worker 不读 consumer.py；旧 parent scorer 差异已记录 |
| TeamBench benchmark 资格 | `OPEN` | 任务文本泄露、单 structural root、native scorer 与 full coverage 仍未解决 |
| situated judgment 的信息价值 | `OPEN` | 未进行新的 LLM episode 或 baseline 比较 |
| online update/backbone/A800 | `OPEN` | 无训练准入信号，未启动作业 |

## 4. 根因与下一步

当前阻碍是**评分/因果设计缺陷与证据不足**，不是 API 或 GPU 阻塞。旧 scorer 把
recipient 行为当作完整标签，producer correctness 无独立测量；直接接入会把 recipient
返工归因给 producer。

下一步按顺序做：

1. 扩充零 LLM qualification：每个 P-check 的 targeted near miss，timeout/permission/
   transport/response digest mutation，candidate read-denial，并把结果纳入统一报告；
2. 设计独立 `producer_score` artifact/ledger event，补 replay constructor 和 causal
   order；在此之前 scorer 结果只作诊断，不更新 controller；
3. 仅当上述门通过后，才把 scorer 放到真实 runner 的 delivery→judgment 之间，并为同一
   judgment 保留 producer `Q_p`、recipient `Q_r` 和 cost 三条记录；
4. 重新评估第二个独立 structural root 和 strong same-information baseline。没有用户决定
   需要，Goal 仍保持 v1.0。

## 后续更正（同日）

本报告原先把一次独立 consumer worker 回放写成旧 parent scorer `4/4` 对 private worker
`FAIL, 0.75` 的真实差异。该表述已撤回：private worker 在同进程中把合法的 Python tuple
写死成 JSON list，导致 `payload_and_ack` 自身误判。修正 worker 后对同一保存的 N02 v3
sealed source 返回 `PASS, 1.0`；原始错误运行保留在
`experiments/logs/n03_independent_scorer_smoke_20260927/`，修正运行在
`experiments/logs/n03_independent_scorer_smoke_20260927_v2/`。ADR 0033 记录了这次更正。
这次错误不改变 producer/recipient 归因分离的协议决定，也不提供评分盲点或科学效果证据。
