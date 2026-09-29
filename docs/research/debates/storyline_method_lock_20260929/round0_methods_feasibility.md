# Round 0 — independent methods feasibility auditor

- **Role**：methods and experiment feasibility
- **Source**：local independent agent; read-only; no repository edits
- **Confidence**：接口缺口与识别风险高；具体最优 updater/benchmark 低

## POSITION

现有方法可以支撑最小协议实验，但不足以识别“责任感知 situated judgment + 在线更新导致更好 future assignment/quality”的主张。它是良好的事件/信息/验收合同，尚不是可复现实验算法。

## TARGET

`method_v1.0/v1.1`、`benchmark_baseline_v1.0` 和 `GOAL.md` 的 ER-G2/G3/G4；重点审查唯一目标、更新器、标签、选择偏差、peer 状态和在线性质。

## EVIDENCE AND REASONING

1. **Identification**：若 RARE 与 contextual trust/bandit 使用相同 judgment、context、propensity、arrival 和 delay，所有收益都可能由普通 trust/bandit 解释。责任门、公共 evidence 和 late correction 必须有可反事实的增量。
2. **Algorithm**：`φ`、状态 `S`、更新 `U`、初始化、探索、容量/淘汰、漂移与 late correction 未定；“小状态充分统计量”只是假设。
3. **Label**：recipient judgment 受 recipient 能力、任务难度、共享模型错误和 prompt 影响；责任过滤不保证 label correctness。需要 independent contract/later-use、reliability/calibration、UNKNOWN 敏感性。
4. **Causal chain**：当前结果未证明 producer correctness、later assignment change、unseen root quality 或 complete cost。
5. **Selection bias**：selected-only 让未选 peer 没有 label，policy 又改变 exposure；需 fixed opportunity 或 propensity/off-policy 估计。
6. **Peer state**：所有 peer 若同构且无持久经验，不能产生可学习 specialization；必须定义 `H_u` 的来源并保持 control 不复制 proposed memory。
7. **Delay/stability**：late label 是否修正状态、撤销 assignment、合并冲突和恢复 checkpoint 尚未定义。
8. **Power/root**：改 seed 不是独立 root；需 root-level split、预注册效应、CI、功效和停止规则。

## DECISION TESTS

- **D1 algorithm lock**：冻结 `φ,S,U`、复杂度、late/idempotence；逐条事件重放相同 digest。
- **D2 mechanism increment**：RARE、contextual trust、raw acceptance、no-update 同信息/预算/propensity；去掉责任门或 late protection 后按预测改变。
- **D3 label validity**：分离 producer contract、recipient integration、later outcome；报告 reliability 和 UNKNOWN。
- **D4 closed loop**：assignment 在执行前改变，并在独立 confirmation root 改善 quality/repair/full cost。
- **D5 online**：update/selection p50/p95、backlog、state bytes、drift response、old-root forgetting、restore/replay。
- **D6 selection bias**：固定机会或 propensity-weighted/off-policy，分析未选择 peer 和 missing labels。

## RECOMMENDATION

先做 method-lock card 和 causal-measurement card，之后才开始零调用 replay 和单 root diagnostic；若 D2/D3 不通过，不能用实验失败为借口降 Goal，而应保留失败证据并讨论是否收窄 claim。
