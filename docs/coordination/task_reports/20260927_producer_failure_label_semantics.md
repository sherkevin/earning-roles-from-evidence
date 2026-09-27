# Task report：producer import failure 的标签语义 / 2026-09-27

状态：`RECOMMENDATION_READY`；`goal_change_requested=false`。本报告只审查
producer quality 的测量语义，没有修改历史日志，没有启动 LLM API、Nebula 或 GPU。

## 问题与直接结论

问题是：候选 producer 已经交付了 `priority.py`，在一套先资格化、版本固定的 Python
运行环境中，`dataclass` 装饰器因字段顺序抛出 `TypeError`，模块因此不能导入。该情况
应判为 **producer quality `FAIL`，binary label 为 0**，但前提是能够证明异常来自候选
producer 源码，而不是 scorer/worker/环境本身。

理由是 producer 的可交付物是“可被声明的公共接口导入并使用的代码”。在环境已通过
资格检查时，候选代码在定义类时失败意味着交付物不能完成最基本的 producer contract；
这不是测量缺失，也不是 recipient 的集成成本。把它判为 `UNKNOWN` 会把一个可复现的
候选缺陷从学习信号中抹掉。

这个结论**不改变历史 v1 日志**。历史运行没有预注册该规则，也没有记录 candidate-origin
的 import-failure 字段，因此只能保持当时的诊断结果和 `UNKNOWN` 语义；不得事后重算
label。

## 证据与当前实现的缺口

保存的 N02 post-hoc 证据已经展示了这个问题：

- `n02_posthoc_priority_sandbox_20260926/episode_0/stdout.bin` 在固定 sandbox 的
  worker 中两次返回 `TypeError: non-default argument 'message' follows default argument`；
  其 `launch.json` 记录了 CPython 3.12.13、sandbox runtime 和完整运行时指纹。
- 同一任务的 `n02_posthoc_priority_import_20260926/summary.json` 在另一个受控解释器
  中也复现了同一 dataclass 定义错误。
- `episode_1` 的 `PriorityEvent.__init__() missing 1 required positional argument:
  '_seq'` 不属于同一类结论：模块能导入，异常发生在 scorer 按自己猜测的构造函数调用
  中；当公共任务契约没有声明这个构造签名时，它是 scorer-contract mismatch，应为
  `UNKNOWN`，不能借此给 producer 负标签。

当前 `dist1-producer-objective-v1` 的 `Scorer.run()` 将 worker 未捕获的 `TypeError`
交给 `main()` 的通用异常处理，返回 `ok:false`；parent 的
`classify()` 因而只能得到 `UNKNOWN`。现有 qualification matrix 也只把
`malformed_source` 预期为 `UNKNOWN`，没有一个预注册的“候选 import TypeError”对照。
所以 v1 的实现无法回答本问题；这不是证据支持 `UNKNOWN` 的科学理由，而是一个未定义
的 scorer 分支。

## 从测量对象出发的判别规则

将 producer 质量拆成环境可观测性与候选能力：

\[
E=\mathbf{1}[\text{同一运行时、scorer 和资源预算已通过 qualification}],
\]
\[
A=\mathbf{1}[\text{delivery digest、必需文件和编码完整}],\qquad
I=\mathbf{1}[\text{producer-owned 模块可导入且公共接口可解析}],
\]
\[
Q_p = E\cdot A\cdot I\cdot
      \frac{\sum_j w_j c_j}{\sum_j w_j},\qquad
y_p=\mathbf{1}[Q_p=1].
\]

这里 `E=0`（worker 无法启动、版本漂移、权限/资源失败、响应损坏）只能是
`UNKNOWN`；不能把环境的不可观测性当作 `Q_p=0`。反之，在 `E=1` 且 `A=1` 时，候选
模块的 dataclass `TypeError` 使 `I=0`，因此 `Q_p=0`、`y_p=0`。这条规则不依赖本次
模型输出的好坏，也不使用 recipient 的最终修复来倒推 producer 质量。

### v2 中必须记录的异常来源

新 scorer 版本（建议 `dist1-producer-objective-v2`，新 response schema）应为每个
异常记录以下已公开、可审计字段：

```json
{
  "status": "FAIL",
  "label": 0,
  "failure_origin": "candidate",
  "failure_stage": "import",
  "exception_class": "TypeError",
  "failure_code": "DATACLASS_FIELD_ORDER",
  "source_path": "mqueue/priority.py",
  "decision_complete": true,
  "coverage_complete": false,
  "quality_score": 0.0
}
```

`source_path`、`exception_class` 和预定义 `failure_code` 只用于审计，不应把隐藏 traceback
或测试断言传给 agent。`coverage_complete=false` 表示后续行为检查因不可导入而没有测量，
不是把未知覆盖伪装成全覆盖；`decision_complete=true` 表示 hard import gate 已经完成，
因而 binary label 合法。parent 不能沿用 v1 的“只有 coverage_complete 才有 label”规则，
必须显式区分这两个字段。

如果希望不扩展 schema，等价但较不清晰的实现是让 P1--P7 全部返回
`FAIL(origin=candidate, blocked_by_import)`，并把 `quality_score=0`；我不建议这个做法，
因为它会让 reviewer 误以为每个行为测试都实际执行过。

## candidate-origin 与 infrastructure-origin 的预注册判定

只有下面条件全部满足，异常才可以成为 `FAIL`：

1. 运行前 manifest 已冻结 Python 可执行文件、版本、依赖 lock、sandbox 版本、环境变量、
   locale、CPU/RPC/session 预算和 scorer worker hash；同一 fingerprint 的 authored-correct
   control 在本轮已成功导入。
2. delivery 的必需 producer 文件存在、UTF-8 解码成功，且 parent 计算的 digest 与
   worker 回显完全一致。
3. worker 已启动并完成请求；candidate traceback 的首个相关 frame 位于只读 public
   source tree 的 producer-owned 文件，或 AST/import 结果明确指向该文件。不能只根据
   `TypeError` 字符串判断来源。
4. 异常可在一个全新的 worker 进程中按预注册的 repeat count（建议两次）复现；复现只
   是稳定性证据，不得在看到结果后增加次数来寻找想要的标签。
5. 该异常属于冻结的 candidate-failure codebook（例如
   `DATACLASS_FIELD_ORDER`、`SYNTAX_ERROR_IN_DELIVERY`、`MISSING_REQUIRED_CLASS`）。

下列任一情况必须是 `UNKNOWN`：worker 自己/driver 的 traceback、缺失 scorer 依赖、
运行时版本漂移、sandbox/permission/resource/timeout、candidate digest 不一致、hidden
driver 无法读取 source，或 scorer 调用了未写入 public contract 的构造函数/方法。这样
`PriorityEvent` 缺 `_seq` 的 episode-1 构造异常不会被误判为 producer defect。

## v2 预注册 qualification matrix

以下矩阵必须在任何新的真实 API episode 之前写入不可变 config；旧 v1 结果不回填：

| 对照 | 预期 | 目的 |
|---|---|---|
| authored-correct producer，固定 runtime | `PASS`, label 1 | 证明环境与 scorer 可工作 |
| dataclass 字段顺序错误，异常来自 producer 文件 | `FAIL`, label 0 | 本报告的目标 case；两次 fresh worker 一致 |
| producer `SyntaxError`（文件内容完整且 digest 一致） | `FAIL`, label 0 | 候选不可导入的确定性边界 |
| 缺必需 producer 文件/非法编码 | `FAIL`, label 0 | delivery 本身不可用；parent 可确定归因 |
| scorer worker Timeout/Permission/exit/资源上限 | `UNKNOWN`, label null | 环境/测量不可观测 |
| scorer response malformed、schema/check/digest mismatch | `UNKNOWN`, label null | 回执不可信 |
| runtime fingerprint drift 或 correct control 也无法导入 | `UNKNOWN`, label null | 不能证明候选缺陷 |
| scorer 调用未公开的 constructor（如 `_seq`） | `UNKNOWN`, label null | scorer-contract defect |
| 每个行为义务的 targeted near-miss | 仅相应行为 `FAIL` | 检查 inventory 与归因粒度 |
| source 中尝试读取 private driver/operator ledger | 拒绝并记录；不产生 quality label | isolation 边界 |

`P2` forced-race 和 `P7` 大压力检查若撞到 worker CPU/RSS/session 预算，仍按
`UNKNOWN`，即使同一 source 另一个 check 已经失败；不能用已观察的负面行为覆盖未知的
其余检查。候选 import gate 是唯一例外，因为它本身已经完成了可归因的 hard decision。

必要的 negative control 是“同样的 TypeError 放在 trusted scorer driver 中”，预期必须
为 `UNKNOWN`；它能检出将所有 TypeError 一律判 FAIL 的危险实现。另一个 control 是把
候选文件保持不变但改动 artifact digest，预期 `UNKNOWN`，防止 source/result 错配。

## 防止 post-hoc 标签塑形

1. 在生成任何 API episode 前，提交新 v2 card、failure codebook、上述矩阵、label/score
   公式、重复次数、预算和 stop rule；运行前写 `config.json` 与所有源码/manifest hash。
2. 为 v2 使用新 `scorer_version`、新 response schema、新 experiment id；不修改 v1
   `response.json`、summary、ledger 或历史 `UNKNOWN`。
3. scorer 结果在 recipient judgment/action 完成前对两个 agent 及 controller 隐藏；
   只在 sealed delivery 上运行。`Q_p` 仅作为 objective oracle/evaluation 对照，不能
   代替 situated judgment，也不能让本轮结果影响本轮选择。
4. 标签规则先在 controls 上逐项运行并把预期/实际回执写入 raw JSONL；若矩阵失败，
   停止该 scorer，不通过修改 label、放宽 timeout、减少 check 或删除失败 case 来恢复。
5. 真实链只允许消费 `label_eligible=true` 的 `PASS/FAIL`；`UNKNOWN` 永不更新 role
   model。每条 producer score 绑定 `delivery_id`、artifact digest、scorer version、
   response digest 和 runtime fingerprint，并由 replay gate 校验。
6. 报告时分开三列：候选质量 label、recipient situated judgment、recipient integration/
   final cost；不得用 recipient 修复成功反推 producer 通过，也不得用 producer FAIL
   替代对 situated judgment 信息价值的测量。

## 对 AAMAS 主线的影响

若采用该 v2 规则，dataclass import failure 可以作为一个干净的 objective producer
negative label，用来检验 recipient judgment 的校准和后续责任分配；它还不能单独证明
RARE、peer specialization 或 online update 有效。当前 candidate manifest、baseline
matrix 和 N03 实验准入仍然保持 `OPEN`：必须先通过 v2 scorer qualification、第二结构
root、同信息 baseline 和持久 agent state，才能把该信号送入 controller 或 A800。

本任务推进了 Goal v1.0 的 ER-G3 测量边界，但没有完成 ER-G1/ER-G2；Goal 不降级。
