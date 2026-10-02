# N03 candidate card: PIPE3 real closed loop with responsibility-safe judgment

状态：`DESIGN_ONLY / NOT AUTHORIZED FOR SCIENTIFIC CLAIMS`  
日期：2026-10-03  
对应 Goal：ER-G1–ER-G4；不修改 active benchmark、method 或 Goal。

## 目的

用一个极小的真实 API 流验证当前真正缺失的识别链：

```text
producer delivery → independent Qp/defect registration
→ recipient judgment → recipient-owned action classification
→ independent later-use outcome
→ source gate → public role-evidence offer
→ preview/read-cut/assignment before target selection
```

这张卡只解决“能否得到合法、可归因的反馈行”，不估计方法 superiority，也不选择
backbone/updater，不启动 A800。

## Root 与材料

- root：`PIPE3_stream_processing`，使用现有 `pipe3-neutral-v1` material adapter；
- seed：先用一个已通过 CPU material/scorer qualification 的 development seed 做
  transport/ledger 小流，第二个 seed 只有在第一条完整且非 UNKNOWN 后才允许执行；
- producer 只能返回 `producer.py`；recipient 只能写 `processor.py`/约定 consumer
  文件，模型和 sink 保持只读；具体 writable paths、source/model/config digest 在
  `prepare` 阶段封存；
- source、prompt、scorer、sandbox、worker-limit 和 candidate registry 均在首次 API
  请求前写入 config/hash manifest。

## API 与执行预算

- provider/model 沿用已验证的内部 API 配置；temperature=0；streaming；不重试；
- 每个 episode 最多 3 次模型调用：producer、recipient judgment、recipient action；
- 每个 seed 最多 2 个 episode；第一条未完成/UNKNOWN/资源失败则停止，不补量；
- scorer/action/terminal outcome 均由固定 CPU scorer 与 sandbox 产生，不调用 hidden
  oracle；
- 这不是 N02 重跑，使用新的 PIPE3 card/version 和独立输出目录；旧 N02 预算不回收。

## 必须记录的真实字段

### Producer

`ProducerScore(status,label,quality_score,coverage_complete,decision_complete,
artifact_sha256,response_digest,scorer_version)`；`status=UNKNOWN` 时禁止 label。
独立 scorer 必须能注册 `producer_defect_registered` 或 producer-owned contract
change；recipient 的 repair 不能替代该字段。

### Recipient judgment

API JSON 必须含 `decision`、`target_role`、`observed_artifact_sha256`、confidence、
rationale 和 repair plan。父进程把 decision/action 映射成 typed ledger，并把完整
原始响应和 parsed digest 保存到 episode 目录。

### Action/ownership

动作前后分别保存 source snapshot；父进程以 writable-path diff 计算
`producer_owned_paths_changed`、`recipient_owned_paths_changed` 和 outside-contract。
producer-owned、recipient-only、mixed、out-of-contract 分别进入
`ELIGIBLE`、`PENDING_ATTRIBUTION` 或 `UNKNOWN`，不得由模型自报 ownership。

### Independent outcome

recipient/adoption scorer 在 action 后独立运行，结果绑定原始 delivery digest 和
output digest，形成 `TerminalOutcome`；不得把 recipient outcome 当 producer Qp。

## 通过与停止

只有以下条件全部满足，才继续第二个 episode：

1. API 请求完整、响应可解析、原始 SSE 和 usage 可复现；
2. producer score 与 delivery digest 绑定，judgment 在 action 前封存；
3. action ownership diff、recipient/adoption outcome 和 ledger replay 全部通过；
4. `evaluate_source_gate` 得出确定状态，并且 source evidence 可由
   `build_role_evidence_from_ledger` 派生；
5. 若要进入后续选择，必须用 `RoleEvidenceOffer` + preview→assignment→commit，
   记录 read-cut、candidate menu、propensity、state/decision digest；不能手写
   `LaterAssignment`。

任一字段缺失、摘要不一致、resource failure 或责任无法归因：保存 `UNKNOWN`，不写
producer label、不更新 policy、不执行下一次选择，不增加 timeout/token/样本。

## 结果字段与论文边界

输出 `config.json`、append-only `raw.jsonl`、逐 episode 原始响应、ledger、source
snapshots、scorer receipts、`summary.json`。summary 必须含 API/token/latency/cost、
UNKNOWN 原因、ownership、root/seed、source/model/sandbox hashes 和
`scientific_claim_allowed`。

这张卡若通过，只能说明真实反馈链可识别、可重放；不能填写 AAMAS 主结果表，也不能
声称动态训练、角色专业化、跨 root 泛化或 quality/cost improvement。baseline parity、
independent history 和 confirmation root 仍需单独冻结后才能做科学比较。
