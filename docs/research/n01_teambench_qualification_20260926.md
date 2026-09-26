# N01：TeamBench 接入资格与修复结果

当前可复用 TeamBench 的任务生成器和原生评分，但不能直接把它当作已经合格的角色学习 benchmark。
这轮修复让我们能够区分“队列修好了”和“接收者真的正确使用了队列”，并明确什么材料可见、什么代码可改、什么测试未覆盖。
两条限定真实模型链已完成；完整任务评分、严格隔离资格和独立任务结构仍待验证。

## 来源与用途

本地 `references/benchmark_sources/TeamBench` 固定于
`d185aef1916fd86a9ba554d581fd256319a973af`；本轮检查 HEAD 一致、工作树干净。
上游代码为 MIT，本项目不修改上游源码。任何后续引入的其他任务数据需要单独核对其条款。

- DIST1 的原生需求明确要求队列实现 ack/nack，consumer 随之集成。生产者交付
  `queue.py` 与 `priority.py`，接收者完成 `consumer.py`，可以形成实际依赖。
- CR2 当前没有独立下游任务，只用于材料/评分接入诊断，不计作协作证据。
- DIST1 的 seed 主要改变命名、术语与默认容量，`seed % 8` 会重复。所有变体
  属于一个结构 root，不能把不同 seed 当独立结构的训练/测试划分。
- 使用完整 generated spec/brief 是本项目显式的信息协议，区别于上游预设
  Planner/Executor/Verifier 的分工；所有拟比较条件必须使用相同协议。

## 已解决的测量错误

1. **任务材料可能缺失。** 上游 `setup_run` 调用 `write_to_disk` 未传 task_dir，
   不能依赖静态模板目录取得当前 spec/brief。新材料适配器直接读取 GeneratedTask。
2. **分数可能把跳过当通过。** 原生 C7 按 pytest exit 0 记成功，即使 ack 缺失时
   测试被 skip。新分类保留原生 score，另列实际 passed/failed/skipped/error/timeout；
   必需测试清单缺失、漏跑或身份重复不能算完整覆盖。环境错误/超时不当能力负标签。
3. **consumer 的工作不影响原生行为分数。** 原生 grader 对 consumer 只检查语法；
   生成测试自己调用 queue，没有运行实际 consumer。新增独立父进程断言、公共子进程
   JSON driver，实际执行 consumer；不向子进程传断言、期望值或评分。
4. **repair/redo 权限不自洽。** use 只允许集成 consumer；repair 允许修改消费副本的
   queue/priority/consumer；redo 从冻结的初始公开模板重建。原始交付不变，修改路径与
   输入/输出 digest 可核查。redo 之前已经读过交付，因此绝不能称为盲测对照。

材料分发、动作约束、固定 source pin、结构 root、评分分类见
[peerrolebench_task_contract.py](../../scripts/peerrolebench_task_contract.py)。
声明的修改权仍需要运行时执行；校验返回快照并不能阻止运行过程中的越权读取。

## 已执行检查及其边界

[动作契约回归](../../experiments/logs/n01_action_contract_20260926/summary.json)
保存先失败后修复的记录：新增检查使旧实现 22 失败/22 通过，修复后 44 通过。
之前材料契约与协议的 37 项合并检查也保留，不能把两个次数相加当成不同科学样本。

[consumer 行为检查 v2](../../experiments/logs/n01_consumer_behavior_20260926_v2/summary.json)
只运行项目中经过阅读的手写产物，没有 LLM 调用，没有 GPU 作业：

| 输入产物 | 观察 | 说明 |
|---|---|---|
| 手写完整修复 | 四项通过 | 空队列、原始 payload/ack、失败重试、drain 均被实际执行 |
| 修复后的 queue + 原始 consumer | 前三项失败，drain 超时 | 原生 consumer 将 `(message, receipt)` 当消息，空队列也继续处理；整体为 UNKNOWN，已观察失败仍保留 |
| 去掉成功 ack | ack 检查失败 | 不再仅看 handler 有没有收到消息 |
| 去掉失败 nack | 重试检查失败 | 能识别消费者造成的消息丢失 |
| 将 `is None` 改成 `not message` | drain 检查失败 | 能识别 0、False、空串等合法 payload 被丢弃 |

v1 因后续超时覆盖此前断言记录，保存为失败接入记录；v2 保留逐项结果，且 UNKNOWN
不会被当作整体 FAIL。这证明新评分能检出这些指定缺陷，不能证明覆盖所有错误或
方法效果。此次没有重跑原生 grader；日志的 `native_score_changed=false` 意指未改动
原生 scorer 实现，**不是测得原生分数不变**。

公共 driver 复用原生 queue/consumer 接口；父进程保存断言是防止测试内容被直接挂到
候选进程的必要条件。子进程仍须在合格 sandbox 内运行，不能因为 JSON 协议而宣称安全。

## 尚未过的门

- 执行隔离：本机没有 Docker/Colima/Podman。初始 sandbox-exec profile 在 Python
  启动时失败，失败日志全部保留。固定版本的 Anthropic sandbox-runtime 源码解释了
  dyld 所需的根 vnode 读取许可；补充精确 `(literal "/")` 后，
  [canary](../../experiments/logs/n01_isolation_canary_20260926_uv312_rootvnode/results.json)
  的公共读写通过，私有读写、符号链接逃逸、loopback 连接、子进程私有读取均被拒绝。
  这是列举访问的有效检查，不是完整 runtime 资格。下一步复用成熟 runtime，
  在实际 worker 边界验证相同约束和资源上限；[上游依据](../../references/aamas/sandbox_runtime_20260926/README.md)。
- 评分隔离：原生 pytest 与候选代码在同进程，不能声称隐藏断言对候选不可见。
  独立 consumer driver 分开了评分对象，但还需验证 source/进程/输出边界并处理资源超限。
- 原生 scorer 有静态实现风格约束；保留其原始分数，不能把新增行为分与原生 leaderboard
  混为一谈。任务更名、跳过和环境错误都需独立列报。
- 单个 DIST1 结构 root 可做 N02 接入，不足以证明跨任务角色学习。正式 benchmark
  替换、root 划分及同信息强 baseline 仍须 N03/N04 的证据后收口。

## 实际运行边界的后续复核

已安装固定 npm `sandbox-runtime@0.0.77`，依赖 lockfile 与
[复现说明](../../tools/peerrole-runtime/README.md) 保存于仓库。未复制改写上游 sandbox。
[runtime-v3](../../experiments/logs/n01_runtime_qualification_20260926_v3/summary.json)
通过十二个列举检查：公开读取、scratch 写入，以及源码改写、私有读写、符号链接、
父评分脚本、loopback、fork 的拒绝，还有不完整响应超时、输出上限、RSS watchdog。
五个固定产物仍能区分。原始 consumer 在前三项失败后触发 RSS 上限，整体 UNKNOWN，
不能将已观察失败直接用作总体负标签。Data-volume 别名补查亦被拒绝。

v1 的 `RLIMIT_DATA` 在此 macOS 上无法设置；v2 在已退出进程组的冗余 kill 上出错。
两次失败原样保留。v3 使用父进程 RSS 轮询，不声称硬内存限额或无瞬时超量。
独立审查又发现子进程返回资源异常会被父断言误判为 FAIL，现改为 UNKNOWN，
原已观察行为失败仍保留；版本升为 `dist1-consumer-behavior-v2`。
[最终定向/契约检查](../../experiments/logs/n01_final_contract_checks_20260926/junit.xml)
为 66 项通过，其中原有 59 项与新增 7 项标签边界检查，不是 66 个科学样本。

**严格 N01 仍未通过。** 非对抗 Python 的内部事件记录仍不是防篡改证据，原生
pytest 同进程 gold 的问题仍存在。[ADR 0017](../user/decisions/0017-n02-development-scoring-scope.md)
记录了两条 N02 开发接入的限定：完全不运行 native grader，只使用父进程 consumer
行为检查；不测独立 producer 正确率、不写角色收益。该限定不能静默覆盖正式资格门。

## 小任务回看（补充）

本轮推进的是故事线的可测性：过去高分掩盖了接收者是否正确使用交付，现在有独立
行为证据，并且不会把环境问题或改名 seed 包装成学习效果。复用资产是上游生成器、
原生 score、项目 strict ledger、材料契约和标准 JSON 通信；新增代码集中于上游
缺失的消费者行为测量。尚未开始实时训练，backbone/update 选择继续开放。

## 真实接入后的资格修正

[N02报告](n02_real_closed_loop_review_20260926.md)记录四次尝试中的两条完整限定链。
两次consumer行为分均4/4，却未覆盖producer的priority模块；事后在同运行边界检查，
一例导入失败、一例原公共构造接口失败。原分不回改，下一版必须按全部公开交付
契约分别检查producer与consumer，不能把consumer分当完整任务分。

两条声明repair实际仅改变消费者本应负责的consumer.py，因此也没有测得额外
返工成本。材料v3显式保留原始职责，repair扩写权限不等于职责转移；旧冻结payload
不改。priority虽然属于公开交付义务，却未进入当前consumer路径，必须另列为
交付合同覆盖，不能据其分数声称真实下游使用收益。

当前同构producer调用无个人持久经验，是N03信号设计的另一个必要缺口。完成
限定链只支持可观测流程；严格N01及正式benchmark资格仍开放，不因API成功关闭。
