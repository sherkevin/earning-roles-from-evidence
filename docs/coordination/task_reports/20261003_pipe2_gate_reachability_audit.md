# PIPE2 gate reachability audit and strict-source fix

日期：2026-10-03
状态：`PARTIAL`（测量合同缺陷已定位并修复；没有产生科学标签）

## 任务与 Goal 对照

本任务回答一个比真实 API 更基础的问题：在 PIPE2 派生候选的 ownership、独立
producer score、recipient judgment、consumer action 和 terminal outcome 都完整时，
现有 gate 是否真的能区分“直接采用”和“recipient 修复”，并且是否能让唯一允许的
producer-defect 分支到达 `ELIGIBLE`。这对应 Goal 的“责任归因可识别、标签来源独立、
反馈只能在正确时序进入后续选择”硬标准；不改变故事线、active benchmark 或 Goal，
也没有申请降级。

## 运行前冻结与证据

冻结输入为 PIPE2 derived-root seed 0，root digest 来自
`pipe2_derived_root_candidate_v1.json`；材料由
`load_derived_pipe2`/`build_derived_materials` 重建。审计复用两个既有实现：

- `scripts/peerrolebench_two_stage_gate.py`；
- `scripts/peerrolebench_pipe2_responsibility_label.py`。

运行脚本为 `scripts/peerrolebench_pipe2_gate_reachability_audit.py`。它只构造父进程
控制 sidecar，不执行 candidate code，不调用 LLM/API、native grader 或 GPU，不写
policy state。运行前写入配置，运行中将每个 case 流式写入 JSONL：

```bash
python3 scripts/peerrolebench_pipe2_gate_reachability_audit.py \
  --output experiments/logs/n03_pipe2_gate_reachability_20261003_v3 --seed 0
```

最终可用回执是 `experiments/logs/n03_pipe2_gate_reachability_20261003_v3/`；v1 和
v2 的原始回执不删除。v1 首先暴露 canonical/PIPE2 gate 差异，随后 v2 将严格分支
收紧；v3 在修正脚本版本字段后重跑。测试：

```text
python3 -m pytest -q tests/test_peerrolebench_two_stage_gate.py \
  tests/test_peerrolebench_pipe2_responsibility_label.py
15 passed
```

The repository-wide `python3 -m pytest -q` command was also attempted, but it is not a
meaningful project-suite result in this checkout: nested TeamBench/fixture workspaces and
external snapshots are collected as tests and caused 1,591 collection errors (module-name
collisions and missing optional dependencies). The affected focused tests above pass; the
repository-wide collection failure is retained as an environment limitation rather than
silently reported as a code regression.

## 发现

初始 v1 的八个可达性 case 中，canonical gate 把两个不应发布的分支判为可归因：

1. 已注册 producer defect，但 recipient 修改自己的 `pipeline/transform.py` 后仍被
   判为 `ELIGIBLE`；
2. judgment 为 `accept_with_rework`、action 为 `repair` 且 recipient 修改文件时仍被
   判为 `ELIGIBLE`。

原因是 explicit-defect 分支只检查 `not producer_changed`，没有要求 direct
`accept/use`，也没有排除 recipient-owned change。PIPE2 专用 gate 已经较严格，两个
实现因此产生了不一致。这个差异若直接进入 live runner，会把 recipient 的整合成本
或修复结果误当成 producer role evidence。

## 修复

`two-stage-role-evidence-v2` 在 explicit registered-defect 分支增加了同一不变量：

```text
decision == accept
consumer_action == use
used_artifact == true
changed_paths == []
```

producer score 必须仍为独立的 `FAIL/0`，Qp/Y、artifact binding 和 target role 必须
完整。旧 v1 receipts 保持不可变；新版本的 strict 分支与 PIPE2 专用 gate 一致。新增
测试覆盖 registered-fail direct-use 的唯一正例以及 recipient repair 的拒绝。

## 结果与边界

| 项目 | v1 初始审计 | v3 修复后 |
|---|---:|---:|
| authored cases | 8 | 8 |
| canonical eligible | 3 | 1 |
| PIPE2 eligible | 1 | 1 |
| gate disagreement | 2 | 0 |
| API/LLM calls | 0 | 0 |
| GPU jobs | 0 | 0 |
| policy updates | 0 | 0 |

唯一的 `ELIGIBLE` 是“独立 producer FAIL/0 + recipient 直接 accept/use + 无任何改动”。
这只是可达性和测量正确性的证据，不是模型能产生该分支的证据，也不是 benchmark
label、peer suitability、future assignment 或 online-learning 效果。当前 PIPE2
真实 sandbox receipts 仍缺正式 situated judgment/action/outcome lineage，不能由本
审计补写。

## 验收状态与下一步

- 责任归因 gate 的一个内部不一致：`RESOLVED`，版本化为 v2；
- 独立 Qp/recipient judgment/action/Y 的真实闭环：`OPEN`；
- 第二 root authority、same-information baseline、independent histories、later
  assignment 和科学结果：`OPEN`；
- benchmark activation 和 A800：保持关闭。

下一步应先审查并收紧 `PeerHistoryV1` 的 source→target lineage 与 selector 接缝，
再决定是否值得为唯一可达正例支付新的真实 API 预算。`goal_change_requested=false`。
