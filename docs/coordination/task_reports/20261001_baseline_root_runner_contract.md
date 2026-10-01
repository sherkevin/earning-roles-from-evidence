# Task report — baseline root-runner contract (2026-10-01)

## 状态

`PARTIAL`。本任务完成了一个可执行的零调用契约层，并没有把它冒充成正式
benchmark runner 或科学结果。`goal_change_requested=false`。

## 目标与冻结内容

本任务对应 `GOAL.md` 的 ER-G3/ER-G4：baseline 必须在同一信息、时间、成本和
责任口径下可比较，且每个结果的分母与回放都可审计。运行前冻结了：

- 七个 ArtifactRole arm 的名称、合法 feedback source、history scope、update rule、
  correction policy 和 visibility profile；
- `artifactrole-baselines-v1` 与 `artifactrole-root-runner-v1` 两个 schema 版本；
- 16 个成本字段及单位：actor/recipient/judge/scorer、selection、policy update、
  retry、communication、repair、replay、state、API、tokens、GPU seconds 和 wall seconds；
- UNKNOWN 规则 `unknown_no_update_with_reason`；
- global schedule prefix、feedback denominators 和 assignment-before-task-start 的校验规则。

代码为 [`peerrolebench_baseline_contract.py`](../../../scripts/peerrolebench_baseline_contract.py)
和 [`peerrolebench_baseline_root_contract.py`](../../../scripts/peerrolebench_baseline_root_contract.py)，
单测为 [`test_peerrolebench_baseline_contract.py`](../../../tests/test_peerrolebench_baseline_contract.py)
与 [`test_peerrolebench_baseline_root_contract.py`](../../../tests/test_peerrolebench_baseline_root_contract.py)。

## 实际验证

证据目录为 [`n03_baseline_root_contract_20261001_v1`](../../../experiments/logs/n03_baseline_root_contract_20261001_v1/)。
测试没有调用 LLM/API，也没有提交 GPU：

- 定向 contract/policy runner：16 passed；
- `tests/test_peerrolebench_*.py`：358 passed；
- policy matrix v12：`QUALIFIED_OFFLINE`，七个 arm 的 snapshot/replay、既有七 case
  语义检查通过；每个 arm 的成本字段现在明确为 `measured=false`，不是伪造零成本。

日志中还保留了一次重复输出目录导致的 runner 退出（`FileExistsError`）；随后使用
新目录 v11 成功，历史失败没有被覆盖。一次无范围的仓库级 pytest 也曾因归档嵌套
workspace 的同名测试、外部 clone 依赖和旧脚本导入冲突而在 collection 阶段失败；它
没有被当作本项目回归结果，项目范围命令的 358 个测试才是本次有效回归。

## 已满足、部分满足与未满足

已满足的是静态 contract：缺少 arrived feedback、提前暴露 future feedback、重复
feedback、非法 denominator class、assignment 晚于 task start、缺成本字段/单位都会
被拒绝；每种 UNKNOWN 必须保留 reason，且不更新 policy。

仍为 `PARTIAL/OPEN` 的是正式 root runner。离线 policy matrix 现在会拒绝不完整的
schedule prefix，但它的 schedule 和 rows 仍来自 hand-authored fixture；尚未由 live
runner 从 canonical ledger 重建每个 decision 的可见前缀，也没有把
`LaterAssignment → task_start → later outcome` 接入同一个 root-level live runner。
`contextual_trust` 与 RARE 的 visibility/correction/update
contract 也仍不同，所以只能把 RARE 标成 candidate method、把 contextual 标成
`open_live_parity`，不能声称 strongest same-information comparison。

成本字段虽已完整，但离线回执全部是 `measured=false`。真实 per-arm/per-episode
成本、独立 live histories、later-use outcome、closest published adapter 和
confirmation split 仍未取得证据。

## 下一步

在第二 root authority A–D 选择前，不启动真实 API/A800。下一项实现应把
`validate_public_prefix` 接入 versioned root runner：runner 只从 canonical ledger
按 `read_cut` 生成 visible feedback ids，并记录 ITT/per-protocol denominator、later
assignment 和完整 measured cost。随后才能重新审查 contextual-vs-RARE 的同信息公平性。

本任务没有改变 benchmark active manifest，也没有修改 Goal。
