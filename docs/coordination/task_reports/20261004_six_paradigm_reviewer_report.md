# 六范式叙事审查报告

- **日期**：2026-10-04
- **审查者**：独立 Codex 只读审查员
- **范围**：六范式参考文档、当前 ACTIVE 故事线/方法/benchmark-baseline、`article/aamas2027/main.tex`
- **结论性质**：叙事审查，不修改 ACTIVE 研究正文，不改变 Goal，不运行 API/GPU

## 1. 审查范围与边界

审查对象：

- `research/2026_AI顶会最佳杰出论文叙事范式_六大范式_阅读整理.md`
- `docs/research/versions/storyline/storyline_v1.1_20260928.md`
- `docs/research/versions/method/method_v1.1_20260930.md`
- `docs/research/versions/benchmark-baseline/benchmark_baseline_v1.1_20260930.md`
- `article/aamas2027/main.tex`

六范式参考文档本身标注为“参考级”，其论文、奖项和数字尚未独立核验。因此，本报告把它作为叙事方法论，而不是正式会议录用规则。

当前论文仍是 internal pre-results manuscript：没有正向效能结果，benchmark 尚未冻结，strong same-information baseline 尚未完成 live parity，closest published adapter 尚未资格化，没有证明 role learning、self-evolution、specialization 或 quality-cost improvement。

## 2. 主范式与辅助范式

### 主范式：①根因手术刀

核心叙事应是：多智能体协作中的问题不只是“谁表现更好”，而是现有反馈把 producer defect、recipient integration work 和 downstream failure 混成一个标签，因此无法可靠地学习未来责任。

当前文档已有这条线索，但还没有把它压成一个全文唯一的根因句。

### 辅助范式：④新基准暴露失效

真实 trace 已暴露一个有价值的系统性漏洞：consumer 行为四项检查通过，但 producer 的 priority artifact 在独立 import/constructor audit 中失败；judge 认为 priority 已修复，consumer scorer 却没有覆盖 producer contract；recipient 自己修改 `consumer.py` 的行为被误解为 producer repair。

这可以形成一把更锋利的尺子，但当前只能称为 benchmark/scorer diagnostic。benchmark 尚未冻结、独立 root 未完成，不能把它写成已经建立了成熟 benchmark。

### 辅助范式：②反直觉重构

论文可以挑战默认设定：acceptance/rejection 或 terminal reward 并不天然是 producer 的质量标签。在真实依赖中，recipient 可能完成自己的正常 integration、因自身错误导致失败，或修复 producer defect；这些因素必须与 producer correctness 分离。

这个反直觉点目前散落在 Intro、Responsibility gate 和 Current Evidence 中，还没有被组织成明确 hook。

### 辅助范式：③理论照亮经验

当前 event-time contract、responsibility gate、delayed update 和 replay 语义具有形式化潜力，但目前主要是对象定义、接口合同和事件时序，并非定理或证明。可作为理论支撑的候选不变量是：pre-selection noninterference、recipient-only no producer evidence、idempotent replay。

⑤社会价值可以作为应用价值补充，但不是当前主线。⑥极简统一美学尚未成立：核心接口较简洁，实际协议含有多个责任、时间和审计层次，需进一步抽象。

## 3. 总体评分

| 维度 | 分数 | 判断 |
|---|---:|---|
| 问题切口清晰度 | 6.5 | 问题已收紧，但根因尚未一句话定型 |
| Hook 与反直觉性 | 5.0 | 有潜力，但开头仍是抽象陈述 |
| 根因定位 | 5.5 | 已有责任混淆线索，缺少单一主因 |
| 因果链完整性 | 7.0 | delivery→judgment→attribution→assignment→outcome 清楚 |
| 方法与根因的对应 | 7.0 | gate、evidence、delay 与问题有对应关系 |
| 理论支撑 | 3.5 | 目前是合同和定义，不是定理或证明 |
| Benchmark 暴露失效能力 | 4.0 | 已发现 scorer blind spot，但 benchmark 未冻结 |
| Baseline 说服力 | 5.5 | 同信息 baseline 设计较完整，实证 parity 尚未完成 |
| 极简统一性 | 4.5 | 两阶段接口清楚，整体实现仍显复杂 |
| 实验叙事成熟度 | 3.5 | 矩阵完整，但没有主结果和确认 root |
| 证据边界诚实性 | 8.0 | 对无结果、失败和 UNKNOWN 交代较诚实 |
| **故事设计潜力** | **6.2** | 有一条可发展的强主线 |
| **当前正式投稿就绪度** | **3.8** | 尚未达到投稿叙事门槛 |

3.8 不是对研究潜力的否定，而是对当前证据状态的评价。没有 benchmark 冻结和主实验结果时，不应把论文包装成已经验证的 role formation 方法。

## 4. 逐节审查

### 4.1 标题

当前标题 `Know Who You Are: Earning Roles from Situated Peer Judgments` 有想象空间，也包含动态形成意味，但没有直接暗示责任归因这一锋利切口，且可能被理解为普通 reputation/role assignment。标题可保留，但 Introduction 第一段必须迅速说明角色为什么不能直接由终局分数获得。

### 4.2 Abstract

当前摘要完成了“协作缺口→situated judgment→责任感知协议→benchmark/baseline/falsification”的链条，且没有伪造实验结果。但它更像研究计划或 protocol paper：

- `We specify a TeamBench-derived artifact track...` 把重点转向实验设计；
- `candidate mechanism` 暴露未完成状态；
- `The resulting protocol makes its claims testable` 是可测试性陈述，不是发现；
- 没有给出已观察到的 benchmark failure 或 diagnostic evidence。

正式摘要应优先写“责任混淆根因→协议如何阻止错误归因→benchmark 如何暴露旧标签失效→实际结果”。在没有结果时要保持证据边界，但不要充满 internal/empty-cell/candidate 语气。

### 4.3 Introduction 第一段

开头 `A collaborator can be valuable in one dependency and unhelpful in another.` 正确但常识化；`Multi-agent systems nevertheless often allocate work with fixed roles, a global reputation, or a central selector.` 是领域概括，不是锋利反例。

建议开头直接使用真实反例：recipient 为了让任务继续而修改自己的 integration 文件，但系统把终局失败归因于 producer。随后给出根因名：`responsibility confounding`。

### 4.4 Introduction 第二段

`when can the agent that actually receives and uses a delivery provide reliable evidence about the producer's future responsibility?` 是全文最强的问题句，明确了参与者、evidence 和 future responsibility。应补充反直觉转折：最接近 artifact 的 recipient 既可能是最有信息的观察者，也是最危险的错误归因来源，除非其自身 integration work 被分离。

### 4.5 Introduction 第三、四段

`make the recipient's local observation a public, version-bound evidence object with a responsibility boundary` 把方法与问题连接得很好，但后续同时列出 public evidence、responsibility boundary、assignment、delayed update、future responsibility、cost，容易被看成多个工程组件。

应明确最小核心：`convert a recipient’s situated observation into a responsibility-scoped evidence object that can affect only a later assignment`；其余是保证该操作合法的约束。

### 4.6 Contribution list

目前四条贡献主要是“定义了什么”“预声明了什么”：event contract、two-stage protocol、benchmark/baseline matrix、falsification boundary。对于内部设计稿，这种表述诚实；正式论文应压缩成三条可验证贡献：责任混淆问题定义、责任/时间安全协议及不变量、能区分 producer/recipient/downstream 的 benchmark contract。第三条只有 benchmark 冻结后才能升级为已建立贡献。

### 4.7 Figure 1

当前顺序 `producer delivery→recipient judgment→public evidence→future assignment→target outcome→delayed credit` 正确，但没有展示旧方法怎样错误归因。建议加一个对照路径 `terminal score→producer penalty`，并标注 recipient-owned work 与 producer defect 被混淆。当前 caption 中 `not a reported result` 适合内部审计，不适合最终论文图注。

### 4.8 Related Work

当前写法谨慎，没有把邻近系统硬说成 baseline。问题是 closest published adapter 仍在资格化，尚无完成的、可复现的强对照。Related Work 应围绕 evidence semantics 写：已有工作学习“谁有用”，本文研究“什么证据在什么责任边界下可以合法地表示谁有用”。

### 4.9 Problem Formulation

优点是 decision 与 feedback arrival 分开，read cut、future outcome、UNKNOWN、assignment-before-start 和 delayed credit 都清楚。这是全文最有理论潜力的部分。

缺口是没有至少三条可审查命题：

1. target outcome 不影响 target selection 的 decision digest；
2. recipient-only change 不产生 producer role evidence；
3. 同一 assignment/outcome lineage 重放不会产生第二次 credit 或改变状态。

### 4.10 Candidate Mechanism

方法含有 publish、choose、validate_later、update、event-time contract、representation 和 score。优点是语义清楚，风险是协议和具体学习模型边界不够清晰。应分成：semantic protocol、policy realization、scientific comparison。RLS、online logistic、periodic refit 等应明确是 updater comparators，不是创新本身。

### 4.11 Benchmark and Baselines

文档明确写出 `candidate protocol, not a frozen benchmark`，这很诚实，但也意味着正式实证叙事还未成立。ArtifactRole 是主轨，PeerSelect 只能证明 local selection、drift 和 service cost；不能让读者以为两个轨道共同证明同一个 role-learning claim。

### 4.12 Baseline Matrix

uniform、no-update、raw acceptance、terminal-only、contextual trust/bandit、pooled controller、RARE 的分层合理。当前缺一个唯一主比较：`RARE vs strongest same-information contextual trust`。closest published adapter 仍是条件项，PeerSelect baseline 不能替代 ArtifactRole baseline。

### 4.13 Experimental Questions and Matrix

RQ1–RQ4 覆盖完整，但可能让论文同时像在研究 role learning、online training、drift adaptation、causal attribution、cost accounting 和 replay safety。主线必须是 RQ2：situated evidence 是否在未见 root 上改善 future assignment utility。RQ3/RQ4 作为机制和边界分析。

### 4.14 Current Evidence

这一节真实记录了两条 API 链、consumer PASS、producer priority audit FAIL、probability 未变化、无 specialization、无 persistent individual experience 和 benchmark 未冻结。对内部版本很有价值，但正式稿中的 `The current draft does not report a positive efficacy result`、`The current scientific release gate is closed`、`No result cell...` 都像研究日志。

应改写为 diagnostic finding：consumer scorer 可以通过而 producer contract 仍失败，这促成了 responsibility gate 和 ownership split。保留失败事实，删除内部 release-gate 语言。

### 4.15 Discussion and Conclusion

Discussion 的边界控制较好。Conclusion 中 `self-evolving multi-agent roles` 可能超出当前证据，建议暂时改为 `a testable protocol for role adaptation`，待证明 role change、assignment effect 和 future utility 后再使用更强措辞。

## 5. 最严重的缺口

### P0：根因没有成为全文唯一主轴

建议统一为：

> Existing multi-agent feedback confounds producer responsibility with recipient integration and downstream outcome, so a terminal score cannot be safely used to form future roles.

所有组件都要说明它如何解决 responsibility confounding、避免未来泄漏、让 evidence 改变 future assignment。

### P0：真实失败没有转成叙事证据

priority audit 应被写成最小反例：consumer scorer 4/4 PASS、独立 producer contract FAIL、recipient 修改 `consumer.py`、producer 被要求承担 repair。只能称 diagnostic evidence，不能扩大成 efficacy result。

### P0：理论支撑尚未形成结果

把 selection noninterference、producer attribution safety、update idempotency/replay equality 组织成定义、前提、证明或机器可检验 invariant。

### P1：benchmark 叙事尚未成立

冻结前统一使用 candidate/qualification track。正文不应把 ArtifactRole 写成已建立的权威 benchmark。

### P1：主轨与副轨并列过强

摘要、主图和主结果只突出 ArtifactRole；PeerSelect 仅用于 updater、drift 和 service diagnostics。

### P2：极简性不足

把所有复杂字段解释为支持一个核心语义操作的审计结构：`publish responsibility-scoped evidence, then consume it before a later assignment`。

## 6. 过度主张或易误读句子

### `main.tex` Abstract

- `We formulate this gap as role formation from situated peer judgments.` 可保留，但要明确是问题定义。
- `We call the resulting candidate mechanism...` 适合内部稿，正式稿应在证据充分后改为 `we introduce` 或 `we study`。
- `The resulting protocol makes its claims testable` 是可测试性，不是研究发现。

### `main.tex` Introduction

- `The scientific claim to test is that...` 明显是研究计划措辞，正式稿需替换为结果或 qualified finding。

### `main.tex` Candidate Mechanism

- `The full mechanism is intended to have three properties.` 是目标，不是结果，除非有定理或实验支撑。

### `main.tex` Conclusion

- `This paper defines a precise object for self-evolving multi-agent roles` 当前可能超证据，建议暂改为 `a testable protocol for role adaptation`。

### ACTIVE 文档

- `并允许后来的可观测结果安全地修正它` 是机制目标，不能被理解为已验证效果。
- `ArtifactRole 承载...质量—完整成本闭环` 在 benchmark 未冻结前应带 candidate/qualification 限定。

## 7. P0–P2 修改建议

### P0

1. 冻结 `responsibility confounding` 根因句。
2. 在 Introduction 开头加入真实 priority audit 最小反例。
3. 明确反转 acceptance/terminal reward 的默认 producer-label 语义。
4. 补充 pre-selection noninterference、recipient-only no producer evidence、idempotent replay 三个不变量。
5. 将 `RARE vs strongest same-information contextual trust` 设为唯一主比较。
6. Benchmark 冻结前统一使用 candidate/qualification track。

### P1

7. 将 Figure 1 改成旧标签路径 vs responsibility-safe 路径。
8. 将 PeerSelect 降为机制副轨。
9. 重写贡献列表，少写“预声明”，多写根因、协议对象和可验证 benchmark contract。
10. 将 Current Evidence 改成 diagnostic finding，删除 internal release gate/empty result cells 等正式论文不需要的流程语言。

### P2

11. 统一使用 responsibility-scoped evidence、future assignment、producer/recipient ownership，减少未证实的 self-evolution/dynamic training。
12. 压缩正文符号，把 ledger digest、arrival metadata、lineage 放入补充材料。
13. 提前定义 complete cost，使其成为主问题约束。
14. 对每段使用 `Observed failure → identified root cause → mechanism response → measurable test` 模板。

## 8. 推荐最终叙事骨架

```text
具体失败场景
→ responsibility confounding 根因
→ acceptance/terminal reward 的反直觉失效
→ situated judgment 转为 responsibility-scoped evidence
→ pre-execution future assignment
→ delayed selected-only credit
→ noninterference/attribution/idempotency 不变量
→ benchmark 暴露旧指标失效
→ strongest same-information baseline
→ future assignment utility、成本、稳定性与边界实验
```

## 9. 最终判断

当前版本有一条可发展的高质量主线：在有真实依赖的多智能体协作中，终局结果和 acceptance feedback 会把 recipient integration 与 producer responsibility 混在一起；研究目标是把 recipient 的 situated judgment 转换为责任边界明确、时间顺序合法、能够影响未来 assignment 的 evidence。

最适合的范式组合是：主范式①根因手术刀，辅助④新基准暴露失效和②反直觉重构，理论支撑③事件时序与责任归因不变量。

当前最关键的不是增加更多方法组件，而是压实根因、转化真实诊断反例、补齐可验证不变量、冻结 benchmark/strong baseline，再由真实结果决定是否使用 role learning、self-evolution 和 quality improvement 等强表述。

在完成 P0 工作前，当前稿件适合作研究设计与内部 pre-results manuscript，尚不适合作为正式 AAMAS 投稿稿件。
