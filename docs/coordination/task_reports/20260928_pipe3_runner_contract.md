# 2026-09-28 PIPE3 real runner contract

- 状态：`DONE`（实现契约，非方法冻结）
- 对应 Goal：ER-G1、ER-G2、ER-G4
- `goal_change_requested=false`
- 真实 LLM API：0；GPU：0；scientific cell：0

## 完成内容

新增 [PIPE3 real runner v1 contract](../../research/20260928_pipe3_real_runner_contract.md)，
把下一阶段实现所需的边界写成可检查的顺序：

- pre-call card、candidate registry、material/root、policy/scorer/provider 和 global
  arrival schedule 必须先冻结；
- 每个 decision cut 先按 `arrival_index` flush，再构造不含 chosen/propensity 的 offer，
  policy choose 后写 native selection，随后才封存 consumption attestation；
- native `PeerRoleLedger`、native sidecar manifest、assignment auxiliary manifest 三套
  链严格分开；
- producer Qp、recipient Qr、adoption 的可见文件边界和 UNKNOWN no-update 规则固定；
- responsibility v3 feedback 必须在 action/artifact lineage 具备后才可成为 eligible；
- online arrival order 与 offline sidecar replay 分离，不能用 wall-clock sort 代替；
- runner 输出、双回放和 real API/A800 准入门槛明确。

## 价值和限制

这份契约消除了实现时最容易发生的三种漂移：把 offer 混进 native ledger、把 judgment
误当成责任标签、把离线排序误当成实时更新。它没有实现 runner、没有调用 API，也没有
选择最终 updater；因此不增加 scientific evidence，不改变当前 Goal 或 active method。

下一步是依照契约新增 versioned `peerrolebench_pipe3_real_runner_v1.py`，先用 fixture
输入和零 LLM fault-injection 通过双回放及 schedule gate，再进行一条真实 API 小链。
