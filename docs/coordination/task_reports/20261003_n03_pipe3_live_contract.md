# N03 PIPE3 live runner precondition contract

日期：2026-10-03
状态：`QUALIFIED_OFFLINE`；仅零调用工程资格，不能支持科学结论。

## 完成内容

新增独立的 `peerrolebench_pipe3_live_contract.py`，没有修改历史 runner 或历史
receipt。contract 验证四类前置条件：

1. source episode 到 target episode 的顺序：assignment 必须先于 target selection
   和 target task start；source/target index 必须递增。
2. 同一 ledger 中 selection、delivery、producer score、judgment、action 和
   outcome 的候选 ID、artifact digest 绑定；完整事件通过既有
   `replay_ledger_events` 后才可通过。
3. ownership classification table：producer-owned defect + 独立 Qp FAIL/0 才能
   `ELIGIBLE`；recipient-only 为 `PENDING_ATTRIBUTION`；mixed、outside-contract、
   digest mismatch 或不完整 Qp 为 `UNKNOWN`；Qp PASS 且无登记 defect 不产生标签。
4. 候选 registry、versioned menu、chosen index 和 propensity 一致性；propensity
   必须等于所选菜单项的概率。

`unknown_no_update` 明确规定 UNKNOWN 不写 label、不创建 assignment/target
selection、不更新 policy，且 state digest 不变。

## Receipt 与验证

- 初始 qualification receipt：[n03_pipe3_live_contract_qualification_20261003_v2](../../../experiments/logs/n03_pipe3_live_contract_qualification_20261003_v2/)；
  共享工作区修复后保留不可变 v2，并重新执行得到最新
  [v3 receipt](../../../experiments/logs/n03_pipe3_live_contract_qualification_20261003_v3/)。
  两个目录都包含配置、append-only raw、ledger、candidate registry 和 summary。
- 5 个离线 case 全部通过：source→target/ledger binding、逆序拒绝、registry/menu/
  propensity、ownership table、UNKNOWN/no-update。
- `real_api_calls=0`、`gpu_jobs=0`、`candidate_execution=0`、
  `scientific_claim_allowed=false`。
- 定向测试：`python3 -m pytest -q tests/test_peerrolebench_pipe3_live_contract.py`，
  5 passed；`py_compile` 和 `git diff --check` 通过。

## 未解决阻断

这项工作没有证明 PIPE3 的真实 API 闭环，也没有证明 benchmark、baseline、角色学习
或训练收益。下一 runner 仍需把真实 API 的 producer/judgment/action 响应绑定到该
sealed contract，运行独立 Qp、recipient/adoption scorer 和 later-use outcome；同时
必须先定义每个 peer 的持久历史，否则同模型 fresh-call peers 只能验证选择接缝，不能
解释 suitability 或角色形成。A800 继续等待这些前置条件。

还有一个需要在下一次方法审查中明确的语义点：当前卡片的 ownership 表把
“recipient-only diff”写成 `PENDING_ATTRIBUTION`，而严格预注册 producer defect 的
实现可以把 producer 保持只读并依赖独立 Qp FAIL/0 归因。此处 contract 暂按卡片表的
显式 diff 优先级执行，没有擅自改写 active method；真实 runner 接入前必须固定这一
优先级并让 scorer、gate、论文描述一致。
