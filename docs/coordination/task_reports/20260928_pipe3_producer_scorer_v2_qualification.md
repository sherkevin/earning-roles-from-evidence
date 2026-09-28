# 2026-09-28 PIPE3 producer scorer v2 qualification

- 状态：`PARTIAL`（producer-only 离线工程资格通过；完整 scorer、真实 runner、benchmark 和科学效果仍开放）
- 对应 Goal：ER-G1、ER-G3、ER-G4；当前阶段门 G1
- `goal_change_requested=false`
- 真实 LLM/API：0；GPU：0；`scientific_claim_allowed=false`

## 本次任务

PIPE3 real smoke v1 在一次真实 API 请求后暴露了 scorer fixture 缺陷：v1 worker 为通用
字段构造 `action="probe"`，但 TeamBench PIPE3 的公开 `models.py` 只接受
`page_view/click/scroll/purchase`。该错误使 P2/P3 变成 `UNKNOWN`，不能生成 producer
label，也不能继续 judgment/action/update。v1 输出不重写，保留在
`experiments/logs/n03_pipe3_real_smoke_20260928_v1/`。

本任务复制并版本化 producer-only scorer 为 v2，在测试事件中从公开的
`models.VALID_ACTIONS` 确定性选择合法 action；同时保留 v1 的 response schema、digest、
coverage 和 `UNKNOWN` 语义，不放宽任何 scorer 结果。新增文件为：

- `scripts/peerrolebench_pipe3_producer_scorer_v2.py`
- `scripts/peerrolebench_pipe3_producer_scorer_worker_v2.py`
- `scripts/peerrolebench_pipe3_producer_scorer_v2_qualification.py`

## 冻结与证据

运行前固定 scorer version、response/request schema、TeamBench commit、seed 0/1、测试
cases、负向控制和 `scientific_claim_allowed=false`。资格运行命令及完整回执保存在：

`experiments/logs/n03_pipe3_producer_scorer_v2_qualification_20260928_v1/`

关键结果：

- `passed=true`，6 个正向矩阵格均按预期返回；
- authored-correct：`PASS`, label `1`, quality `1.0`, decision/coverage complete；
- original-delivery：`FAIL`, label `0`, quality `2/3`，decision/coverage complete；
- syntax-failure：`FAIL`, label `0`, quality `0.0`，candidate-origin syntax code 被保留；
- trusted-driver type error、timeout、digest mutation、decision incomplete：全部
  `UNKNOWN`，没有 label；
- `llm_calls=0`、`gpu_jobs=0`、native grader 未调用、candidate 未收到 hidden assertion。

## 与 Goal 的对照

| Goal 标准 | 本次状态 | 说明 |
|---|---|---|
| producer 责任可形成可审计的质量信号 | 部分满足 | seed 0/1 的离线控制矩阵能区分正确、交付失败和 scorer/环境 UNKNOWN。 |
| FAIL/UNKNOWN 责任边界稳定 | 满足工程子门 | candidate-origin syntax/交付错误才产生 0；trusted worker、digest、coverage 错误不产生 label。 |
| recipient judgment、实际 action、adoption 与 cost | 未满足 | 本任务只资格化 Qp，未执行 recipient 或 sink。 |
| 真实 API runner 的隐藏隔离和完整 lineage | 未满足 | 没有 API；仍需在真实 runner 中验证 IPC、delivery、ledger 和 sidecar 绑定。 |
| 独立 root、强同信息 baseline、benchmark freeze | 未满足 | seed 0/1 仍是同一 structural root；`scorer_is_qualified=false`。 |
| 在线角色学习或 AAMAS 科学效果 | 未满足 | 没有 policy update、跨 episode 结果、质量/成本比较或 GPU 训练。 |

## 发现的问题与下一步

v2 修复的是一个确定的测试事件与公开任务模型不一致的问题，不能被叙述为模型能力提升，
也不能回写 v1 的 UNKNOWN。剩余门槛由回执明确列出：recipient-self/adoption scorer
仍未合并到同一 qualification，PIPE3 versioned runner 与真实 ledger replay 尚未接通，
candidate/scorer 仍是非对抗性 Python instrumentation，且 seed 0/1 不是独立 root。

下一步先把 v2 scorer 接入新的 versioned real-smoke card，在最多一条小链中观察 Qp 是否
完整；任何 scorer UNKNOWN 都停止后续 judgment/action/update。只有完整责任链和同信息
baseline parity 都通过后，才讨论第二 root、benchmark freeze 或 A800。无需用户改变 Goal
或批准降级。
