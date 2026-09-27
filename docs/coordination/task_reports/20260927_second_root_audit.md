# Task report：PIPE3 与 MULTI3 第二结构根静态审查 / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。本轮只读取固定的
`TeamBench@d185aef1916fd86a9ba554d581fd256319a973af` 生成器、任务文本、测试和
grader；没有运行生成器、pytest、LLM/API、Nebula 或 GPU，也没有修改历史实验结果。

## 审查标准

第二个结构根必须同时满足：

1. 上游 agent 交付可观察的中间产物；
2. 接收者有原任务固有的独立工作，不能把已经完成的代码重新分配来制造工作；
3. 接收者真实读取/使用交付物；评分能分别测上游交付、接收者自身完成度和最终采用结果；
4. seed 只是同一结构根的变体，不能冒充独立 root；任务文本不能把 gold 修法直接泄露给被评价的 agent；
5. 失败、基础设施 UNKNOWN、成本和修改归因必须能够保留在账本中。

## PIPE3_stream_processing

PIPE3 仍是当前最强的代码交付型候选，但**不能冻结为 benchmark**。

- 结构链清楚：`producer.py` 生成 JSONL，`processor.py` 有自己的变换工作，`sink.py`
  读取 processor 输出；三个缺陷分属 producer（时间戳）和 processor（envelope、编码）。
  因而可以定义 producer contract、recipient-self score 和 sink adoption 三个不相同的量。
- 已有严格时间戳边界的四格父进程 smoke（见
  [`n03_pipe3_qualification_20260926.md`](../../research/n03_pipe3_qualification_20260926.md)）
  能区分“只修 producer”“只修 processor”和“两者都修”。这证明评分切分方向可行，
  不是 peer 学习或效果证据。
- 三个 seed 只改变领域字段，仍由同一个生成器和相同三项错误机制产生；只能在同一
  `PIPE3` root 内作变体，不能作为三个独立确认样本。
- 原始 `spec.md`/`brief.md`/源码注释明确写出了 Bug、修复方向、Planner guidance。
  即使材料适配器移除了 oracle 文本，仍需真实 payload dispatch、接收者私有评分器、
  operator-only ledger 和完整 replay，才能证明信息边界；当前静态 canary 不足以证明这些。
- 原生 grader 还会安装 pytest、使用候选同工作区的测试；不能把 native 总分直接当作
  situated judgment label，也不能把同进程测试称为隐藏评分器。

**判定：CONDITIONAL / 不冻结。** PIPE3 的下游独立工作和 adoption 语义成立，下一步只
应补齐材料去 oracle、真实 IPC/评分器、producer/recipient 权限、multi-event/异常/成本
覆盖和 task-root split；在这些门通过前不启动新的 PIPE3 LLM 链或 A800。

## MULTI3_polyglot

MULTI3 有一个可利用的 backend→frontend 接口，但当前更适合作为备选，**不能直接作为
PIPE3 之后的第二个已准入 root**。

- `backend/processor.py` 的 serializer/batch 是明确上游交付；`frontend/handler.py` 的
  deserialize/process envelope 是明确下游工作。生成测试使用 hardcoded
  `correct_wire` 隔离 frontend 缺陷，这一点比只看总 round-trip 更适合构造 recipient
  self score；backend 测试使用实际 `self.wire`，可分别测 producer contract。
- 但第三个参与者 `shared/schema.json` 同时被 backend/frontend 依赖，且 schema bug 被
  生成器强制注入。必须在任务契约中明确 schema 是 operator-owned canonical contract，
  还是一个可分配的第三角色；如果不裁决，修 schema 的成本和责任会混入 backend/frontend
  judgment，无法归因。
- 当前 `spec` 标题为 “Planner Only”，直接列出 active bug inventory、字段、修复规则；
  `brief` 要求“修复 bugs”，而不是要求 recipient 对 producer 交付进行独立集成。若把
  backend 分给 producer、frontend 分给 recipient，需要新增明确的交付封存、接收者使用
  producer wire、schema 只读权限和 adoption 结果；这不是原生 MULTI3 评分的直接语义。
- frontend 的 canonical 输入可以测自身处理，但必须增加 parent-side producer artifact
  digest 与 schema contract probe；现有 round-trip/全套 unittest 不能证明 frontend
  实际采用了本次 producer 的 wire。反过来，backend 的测试会由 backend 自己构造 wire，
  不足以证明真实 frontend 已收到该交付。
- `BUG_COMBOS` 和四个 domain seed 改变字段与错误组合，但骨架始终是同一个
  backend/handler/schema serialization root；不能把 seed 计作独立 root。还需审计每个
  seed 的 expected JSON 是否真的进入 grader（不能只根据配置文件声明 seed-aware）。
- grader 的若干检查以候选模块/测试为执行边界，并从 expected 文件读取字段；应把
  canonical expected、异常/UNKNOWN 分类和 scorer 进程隔离后再谈真实信号。

**判定：CONDITIONAL-LOW / 暂不接入。** MULTI3 不是无效任务；它可复用字段级
backend/frontend scorer、canonical wire fixture、schema contract 和 round-trip 资产。
但在 schema ownership、真实 delivery binding、去 oracle 材料、独立 scorer/UNKNOWN、
多 seed root 划分及成本账本未解决前，不把它记为第二个合格 root，不启动 LLM/API。

## 选择与强 baseline 门槛

静态审查后的顺序是：

1. 先继续 PIPE3 的资格收口；若其 IPC、隐藏 scorer 或任务材料门失败，才转 MULTI3 的
   schema/ownership 改造，而不是同时扩展两个 runner。
2. 第二 root 通过后，固定同信息、同预算、同候选集合和同 task-root 的 baseline：
   no-update random/round-robin、terminal-only outcome、总体可靠性、以及使用完全相同
   delivery/judgment 信息的 contextual trust/bandit。任何 policy 都不得读取 producer
   private scorer、recipient 私有记录或 future outcome。
3. 在 baseline 与 root split 之前不把已有两条 DIST1 真实链当作角色学习结果；它们只证明
   受限 runner、ledger 和接口边界的工程事实。

## 结论

没有静态证据支持“PIPE3 已冻结”或“MULTI3 可立即替代它”。PIPE3 的因果切面更干净，
应先完成真实运行资格；MULTI3 保留为失败转向时可复用的第二候选。任何下一次真实调用
前都应重新写 config 和本报告对应的任务报告，保留 UNKNOWN/失败，不扩大 N02 已关闭的
episode 预算。
