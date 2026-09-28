# 2026-09-28 pre-decision evidence offer and consumption attestation

- 状态：`PARTIAL`
- 对应 Goal：ER-G1（future assignment 箭头可识别）、ER-G2（方法边界可验证）、ER-G4（主张与证据一致）
- `goal_change_requested=false`
- 真实 API：0；GPU：0；科学效果主张：不允许

## 为什么不能继续沿用 LaterAssignment

旧的 `LaterAssignment` 同时包含 chosen agent/propensity，随后 selection 又被强制与它
一致。这样 assignment 在决策前已经编码了 policy 输出，无法识别 evidence 是否真正
影响选择。此次新增的 `AssignmentEvidenceOffer` 只包含 task/index/role、context、候选
菜单、公开 evidence rows 和全局 event watermark；它没有 chosen agent 或 propensity。
chosen peer 只能在 policy 读取 offer 后由 `DecisionSidecar` 产生，LaterAssignment
今后只作为 selection 后的 lineage/adoption 记录。

## 合同

`AssignmentEvidenceOffer` 的 `bundle_digest` 只由公开字段计算，不包含 operator ledger
record hash，避免 matched cells 通过内部记录哈希泄漏条件。rows 只允许公开字段，要求
source/candidate/version、source index、arrival index、label/disposition/provenance
完整且一致；private scorer 字段、重复 ID、未知 candidate、未来 arrival 和非有限数值
都会拒绝。`source_index` 表示 evidence 的语义顺序，`arrival_index` 表示其何时可读，
两者不混用；`global-event-index-v1` 明确 watermark 的同一时间域。空 offer 是合法
cold-start/F=1 情形。

`DecisionConsumptionAttestation` 绑定 offer id/record hash、公开 bundle digest、
selection protocol/event/sidecar digest、policy state digest、state version、read
cut、decision index 和 policy input digest。构造与验证都要求候选菜单、task/role/context
和 state digest 完全一致，且 `available_index <= read_cut <= decision_index`。F=0
attestation 的 policy input 使用空 offer digest；operator 仍可保留真实 offer，但不把
bundle 传给 policy。operator ledger hash 不参与 public bundle digest。

## 验证与失败保留

测试 `tests/test_peerrolebench_assignment_attestation.py` 的 11 项覆盖：F=1/F=0
敏感性、空 cold-start、private/unknown row、双时间轴未来泄漏、菜单/上下文/state
不匹配、decision mismatch、operator-hash 非干扰和 canonical digest。qualification
还用固定菜单/温度的 toy adapter 检查：F=1 改公开 label 会改变 input digest 与输出
概率，F=0 改 evidence 不改变二者。它是接口行为资格，不是方法效果。

- v1 `experiments/logs/n03_assignment_attestation_qualification_20260928_v1/`：10 个
  case 单例通过，但 summary 计数写成 11，失败日志保留。
- v2 `..._v2/`：加入 toy sensitivity 和 late case 后通过；随后又补充 scalar row、
  双 watermark 和 public/operator digest 约束。
- v4 `..._v4/`：在补充 scalar row 与双 watermark 后重跑 11 case；其目录内配置仍沿用
  v2 experiment id，故不把它当成独立版本号，只保留作源码哈希审计记录。
- v5 `experiments/logs/n03_assignment_attestation_qualification_20260928_v5/summary.json`：
  最终源码上 12 个 case 全部通过，状态 `QUALIFIED_OFFLINE`，
  `scientific_claim_allowed=false`。

## 边界与下一步

attestation 的 digest/read trace 是 non-adversarial runner 的审计声明，不是恶意 policy
进程下的密码学行为证明；offer_record_hash 也还需要独立 assignment-offer manifest 或
版本化 protocol event 做 canonical ledger binding。当前没有真实 runner 在每个 decision
cut 前调用 policy，也没有 feedback/selection 的 event-time interleaved replay，因此 F
scientific cell 仍为 0。后续零调用 event-time qualification 已将 offer/consumption
写入独立 auxiliary manifest；native sidecar manifest 保持三类 native event 的
exact-coverage，不能混入这两类 auxiliary event。下一步是实现同一
`PublicEvidenceOffer` 输入下的真实 policy 与强 baseline 的交错执行：每次 decision 前
flush `arrival_index <= read_cut`，记录 state digest/attestation，再产生 selection；
迟到 feedback 只能影响尚未执行的后续 decision。
