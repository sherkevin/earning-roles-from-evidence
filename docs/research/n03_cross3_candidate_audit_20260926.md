# CROSS3 第二任务基底审查：原切面不通过

本次要判断 TeamBench 的 CROSS3 能否接在 DIST1 之后，提供另一个“上游交付、下游继续自己的工作、再评价上游”的任务基底。结论是：**不能把它直接接成代码交付型的第二个结构 root；原有 consumer 和 publisher 已经实现，剩余缺陷都在两个并列的上游模块。** 原生“分析计划 → 修复代码”链条值得保留，但它属于另一种交付切面，尚未取得独立评分和实际采纳的资格。

日期：2026-09-26。源码固定为 `TeamBench@d185aef1916fd86a9ba554d581fd256319a973af`，读取时 `git status --short` 无输出。本文只做源码阅读、AST 静态检查和文件哈希计算；没有运行生成器、候选代码、pytest、grader、LLM API 或 GPU 作业，没有新增实验结果。

## 第一原则：必须有未完成的下游工作

研究需要的因果链是：一个 agent 交付了某样东西，另一个 agent 在完成自己独立负责的工作时实际使用它，使用中取得的证据再影响未来分工。仅存在函数调用，或请另一个 agent 重写已经正确的 consumer，都不能满足这个要求。

本次按三个问题判断，不以任务名称或文件名判断：

- 原任务是否同时留下上游交付和下游独立工作？
- 评分能否分别观察上游交付质量、下游自身完成度、最终组合结果？
- 改造是否保留原始任务，而不是删去完成代码、增加原本不存在的义务来制造协作？

结构 root 指共享同一依赖和缺陷结构的一族任务，不是一个 seed 或领域名称。CROSS3 与 DIST1 的业务接口不同，具有成为另一结构 root 的内容基础；但结构不同本身不等于符合我们的交付/消费者语义。

## 原始职责：只有桥接模块待修

原 spec 的目标是修复 `bridge/translator.py` 的四类转换错误，以及 `bridge/error_mapper.py` 的两类 HTTP 状态映射错误。`analysis_guidance.md` 更明确要求只修这两个文件，不改 `service_a/` 或 `service_b/`。依据：S:3–20、A:41–43。

生成器已经提供 `BridgePublisher.publish_record()`，它调用 translator 并把消息交给 `MessageConsumer.consume()`；也已提供 `publish_error()`，调用 error mapper 后交给 `consume_error()`。`MessageConsumer` 已完成校验和收集逻辑；这些方法没有待实现标记，也不属于 spec 列出的六个缺陷。依据：G:355–393、472–506。

**判断：把 producer 定为 translator/error mapper 的修复者、把 recipient 定为 consumer 的“实现者”，会给 recipient 分配原任务已经完成的工作。** 把 translator 和 error mapper 分给两个 owner 也不能解决：两者分别处理正常消息和错误状态，都由现成 publisher 调用，后一个 owner 的修复并不消费前一个 owner 的修复产物。

具体例子：修好 `translate_event_streaming()` 后，现有 `publish_record()` 会调用现有 `consume()`。这是真实代码依赖，但没有尚待 recipient 完成的集成任务；recipient 新写同功能 `consume()` 所花成本不能算 producer 导致的返工。

## 公开职责：检查与依赖逐项对应

下表完整列出 spec 的七项验收义务，并补充原 API 和连接过程的检查范围。`C1`–`C10` 是原 `grade.sh` 中的检查，不是本文运行结果；“覆盖”仅表示读取到对应调用或断言。

| 公开职责 / 原 API | 原 native 检查与假设 | 实际 consumer 依赖 / 未完成工作 | 资格判断 |
|---|---|---|---|
| R1：int64 不截断；`translate_<domain>(dict)` 返回对应 dataclass | translation 的 `test_int64_not_truncated`，C2/C4；C4 接受任一 dataclass 字段等于大 ID。E2E 明确检查 ID。G:571–589、743–765；R:61–104 | `consume()` 不检查 ID 范围或保真；现有 E2E 检查最终收集消息。没有新的 consumer 工作 | 有上游确定性属性；C4 的“任一字段”弱于指定 ID 字段 |
| R2：payload 字符串 base64 解码为 bytes | translation 的 bytes 测试检查类型和相等；C5 在所有字段中找原始 bytes。G:592–610；R:106–145 | `consume()` 检查 payload 是 bytes，但不比较内容；E2E 比较内容。G:374–381、763–765 | 属性可复用；应按已知字段断言，避免任意字段代偿 |
| R3：oneof 只能选择一个内容变体 | translation 测 text-only 和 neither；C6 同样只测 text-only、neither，并调用 schema 的 `validate_oneof()`。G:613–647；R:147–206 | `consume()` 确实调用 `validate_oneof()`，但校验只拒绝多于一个 truthy 字段。G:334–345、374–376 | spec 的“exactly one”和实际“at most one”冲突；没有两个输入同时非空的断言，也没有 binary-only 行为断言 |
| R4：所有 status 名称映为整数代码 | translation 遍历四个固定正确映射；C7 从候选 `STATUS_MAP` 自取 expected，并按字段名含 `status` 寻找输出。G:650–673；R:208–259 | `consume()` 只检查 `isinstance(status, int)`，E2E 也只检查类型。G:379–380、765 | translation 断言可复用；C7 不能独立充当可信真值来源 |
| R5：404 → NOT_FOUND=5 | `test_404_maps_to_not_found`、C3/C8；E2E 检查最终 errors 包含对应代码。G:699–705、768–780；R:261–279 | `consume_error()` 直接收集，不自行验证 code。G:383–384 | 上游 mapping 可独立评分；下游路由已经实现 |
| R6：429 → RESOURCE_EXHAUSTED=8 | `test_429_maps_to_resource_exhausted`、C3/C9；同一 E2E。G:708–714、768–780；R:281–300 | 同上 | 同上 |
| R7：`pytest tests/` 全过 | C1 跑所有 tests；C2/C3 重跑两个子集，末尾又跑一遍整体以采集数量。R:33–58、320–341 | 整体测试包括真正 publisher→consumer 调用，不是 DIST1 的仅语法检查 | 测试成功不等于 recipient 有独立工作；子集和整体重复，不可当独立证据 |
| 保留 translator 公共符号 | 生成器保留 `translate_<domain>` 和别名 `translate_event`；publisher 用前者，tests/直接 grader 用后者，grader 还读取 `STATUS_MAP`。G:408–440、479；R:68–85 | 只保留 alias 或只保留原函数名都会破坏一侧调用 | 不应凭接口名改造简化；二者和常量需在契约中明确 |
| 保留 `map_http_error(status_code, message="") -> StatusMessage` 的其他分支 | tests 覆盖 200、400、500；spec 另写 401/403、5xx。G:452–469、685–722；S:38–49 | publisher 传 detail；consumer 保存状态。现有 tests/E2E 不断言 message 保留，也没逐项测试 401/403 和非 500 的 5xx | 不能把两项 bug 修好直接等同完整原 API 保持 |
| 保持 record 的 type/timestamp 和 schema 属性 | translator 赋 type/timestamp；数据模型暴露对应字段。G:191–229、321–345、423–424 | consumer 不验证 type/timestamp，native 主要检查不覆盖其正确值 | 作为原接口回归属性保留；不能将隐藏扩充义务偷加到 producer 标签 |
| 正常消息经 publisher 到 consumer | `test_e2e_translate_and_consume` 调 `publish_record`，断言收到一个消息并查 ID/payload/status 类型。G:743–765 | 真正调用实际 `consume()`；当前实现已具备所需功能 | 可以复用为组合检查，但不是新 recipient 实现验收 |
| 错误消息经 publisher 到 consumer | `test_e2e_error_routing` 调 404/429，检查两条消息和代码集合。G:768–780 | 真正调用 `consume_error()`；当前实现已具备所需功能 | 可复用；未断言顺序、detail 与状态的逐条对应 |
| 两个修改文件语法有效 | C10 用 AST parse 两个文件。R:302–318 | 不运行 API | 是静态资格检查，不能替代功能检查 |
| 分析者交付诊断，Executor 修复原有缺陷 | 原框架支持 planner 报告与消息，Executor 随后完成代码修复；native grader 最终只评代码。I:342–418、492–526；O:442–515 | Executor 确实还有未完成工作，可消费诊断；其最终正确与否不能单独给诊断定责 | 可保留为另一种交付切面；尚缺报告质量和逐项采纳评测 |

> **评分口径警告：**源码中共定义十二个 pytest 测试函数，其中五个 translation、五个 errors、两个 E2E；这是静态计数，没有执行。原 partial score 是十项 C 检查的通过数除以十，其中 C1/C2/C3 与 C4–C9 大量重叠，不能解释为十个独立能力或独立样本。

## 任务变体：三个 seed 仍是一个 root

`task.yaml` 列出 seeds 0、1、2。生成器按 `seed % 3` 选择 event streaming、IoT telemetry、media catalog，替换类名、字段名、枚举名称和示例文本；所有变体保留相同六个缺陷与相同调用结构。依据：T:7–8、G:15–80、89–113。

`spec.md` 与 `brief.md` 每次直接从同一固定文件读取，没有 seed 插值。它们主要用通用名描述转换要求，因此没有把 IoT/media 明确绑定为 event 任务；但 analysis guidance 的若干字段例子是通用或 seed-0 风格，不能把例子名称当作每个 seed 的真实 API。依据：G:95–99、A:11–29。

seed 在工作区内的另一作用只是 `tests/fixtures.py` 中 `LARGE_RECORD_ID = 9007199254740993 + seed`。本文件中的 `SAMPLE_JSON_BINARY` 没有被生成的十二个测试函数导入；大 ID 的主测试/E2E 仍使用固定值 `9007199254740993`。静态 AST 还显示构造的 `rng` 没有被读取。依据：G:90、115–166、522–559、562–781。

**判断：不能把三个领域名称视为三种独立任务结构，也不能用增加 seed 来扩大独立样本量。** 同模三的 seed 仅改变未被这些测试引用的 fixture ID 和 expected 元数据，不能形成新的未知能力评价。若以后使用 CROSS3，所有变体必须在同一 root 组中划分训练/保留集。

## 原评分：有真实消费也有盲点

与 DIST1 的原评分不同，CROSS3 的 E2E 的确把生成的消息送入实际 consumer。这个资产值得保留；但它检验的是“修好桥接模块后，既有管道能否工作”，不提供 recipient 独立实现、采纳判断或返工归因。

下面是必须先解决的源码级问题，而非已观察到的运行失败：

- **oneof 契约冲突。** spec 和 schema 注释写 exactly one，实际 schema 和 tests 允许零个；缺少 both-present 与 binary-only 测试。未经版本化裁决，不应把某一解释写成官方正确标签。
- **真值来自可改对象。** C7 使用候选 translator 的 `STATUS_MAP` 作为 expected；固定 translation 测试能约束四个正确值，但 C7 本身不独立。C4/C5 在任意字段寻找所需值，弱于字段级契约。
- **测试与执行共址。** C1–C3 执行工作区内 tests，候选 Python 模块与测试断言处于同一进程。单独加外层 sandbox 并不能把这些断言变成候选不可读的秘密；完整原 harness 的容器权限未在本次重新审计。
- **执行错误直接算 fail。** shell 分支将 pytest/导入非零结果记为 fail；CROSS3 不区分基础设施 UNKNOWN。`grade.sh` 运行时还尝试 `pip install pytest`，且同时使用 `python`/`python3`，不适合直接移入无网、固定解释器的资格环境。
- **expected 文件没有参与这个 grader。** 通用 harness 会把 `expected.json` 作为第五参数传入，但 CROSS3 脚本只读取前四参数。因此 expected 的 seed/domain 字段不同，不证明评分真的覆盖新实例。依据：H:59–64、R:5–8。

最小的评分整理可复用现有公开测试，将固定 schema/字段/枚举值放在父进程，按单个职责检查受限 worker 的输出，同时保留原 native 分数及其身份。即使完成这些整理，它也只改善交付质量测量，仍不能补出原任务没有的下游工作；本轮不实现该 scorer。

## 可复用切面：诊断交付需另判

不能因为代码交付切面不合格，就否认原有 Planner→Executor 的合作。框架明确允许 Planner 交付分析报告或计划，Executor 读报告后实际修改有缺陷的代码，具有“交付物不是最终答案，下游仍有工作”的基本形态。依据：I:309–330、342–418、492–526，O:442–515。

这条备选切面也有决定性限制：analysis guidance 直接给出了六项修法，bug 注释和公开 tests 也暴露了大部分修复内容。因此不能仅靠让 Planner 复述答案、Executor 实现答案，就推定存在有价值的 situated judgment 学习信号；原 grader 也不直接检验报告忠实性、完整性或是否真正被采纳。

**可以制定不读取私有评分答案的新前瞻协议，但不能原封照搬 analysis 模式。** 这里的“不泄漏 gold”指不读取 evaluator 的期望值、评分脚本、其他运行报告或人工解答；原 spec 自带的六项需求和工作区注释/公开测试是合法任务信息，不能为了产生差异把它们偷偷删掉。

最小可讨论协议如下；它是源码层面可构造的候选，尚未实现：

| 环节 | 保留与限制 | 必須测量，不能偷换的目标 |
|---|---|---|
| Planner 交付 | 只读原 spec 与原工作区代码/公开测试；交付带具体文件/行及公开需求依据的诊断与修复计划，不直接给 Executor 一个已经修好的代码仓库 | 逐项诊断是否有可见依据、是否指出真实缺陷、遗漏哪些职责；引用存在不能代替诊断正确 |
| 可见信息 | 不向双方提供 `analysis_guidance.md`、grader、expected 或历史答案；完整保留任务代码与原公开 tests。spec 给 Planner、brief 给 Executor，严格记录原设定的信息差 | 将“不提供现成解答 guidance”列为新协议与上游 analysis 模式的差异，不能称 native 零改动；若坚持完整保留该模式的 guidance，就关闭“独立诊断能力”解释 |
| Executor 实际使用 | 原任务仍只修 translator/error mapper；先记录对计划各项的接受、拒绝或需澄清判断，再保留对应代码差异和执行证据 | 计划采纳与最终代码结果分开；自己的实现错误、计划带来的误导、独立发现的遗漏分别编码；只有可观测额外修复才记返工，不能用一个 `repair` 文本标签替代 |
| 独立评分 | 在看到结果前解决 oneof 契约冲突；诊断按公开职责离线核查，最终代码按独立执行属性与原 native 范围分别记分 | 不把最终成功反推为计划正确；不用 grader 输出提前帮助 Planner；不能由计划自己的 `STATUS_MAP` 定义自己的真值 |
| 最小对照 | 同样代码/公开测试下的无计划 Executor，以及固定转发公开 spec 中六项要求的基线；完整计入读计划、生成计划、执行与修复成本 | 检查真实诊断是否比需求转发多提供可用信息，或是否在总成本上帮助实现；若同等成本下只会复述公开修法，没有支持 peer 信息学习的证据 |

信息限制必须由明确文件清单实现，不能只相信角色名或 prompt：源码里的读取工具以 task 目录为 allowed root，范围宽于单个 spec/brief 文件。依据：I:329、402–408、520–524。本次没有证明原容器 mount 是否已收窄这个范围，因此新协议须单独审计可见文件，不能沿用“Executor 看不到 spec”的未验证假设。

**仍只是候选的原因：**现有公开代码和测试已暴露大部分修法，排除人工 guidance 也不保证有诊断难度或增量价值；六种同结构错误也不保证不同 peer 具有稳定、情境相关的差异。即使一份计划帮助 Executor 修好代码，也只支持一次诊断协作，不能证明从第三方判断学习了角色或选人收益。

将这条切面作为第二 root 会改变交付类型，应在跨任务契约中显式说明；不能把计划采纳直接混称为代码消费者返工。本审查也没有证明原生 harness 在 CROSS3 上默认走 analysis 模式。

## 来源与许可证：材料已在本地

固定源码、测试模板和 grader 已在本地参考仓库，本文保留了职责表、原 API、缺口和逐文件哈希，不需要再次下载或另造任务模板。可立即复用的是 schema/API 边界、六类公开故障义务、真实 publisher→consumer E2E 连接，以及原生报告→实现流程；其中评分覆盖不足的部分已标明。

仓库 LICENSE 为 MIT；README 说明来自外部 GitHub/UCI 的任务仍保留上游许可证。CROSS3 的工作区与示例字节均由本生成器直接构造，没有引用外部数据文件或标明独立数据许可证，因此本次只能确认其在仓库 MIT 声明范围内，复用时保留版权及许可文本。

`datasets/README.md` 对另一套数据下载工具的 synthetic placeholder 声明 CC0，不应泛化成 CROSS3 全部生成代码和测试都是 CC0。spec 的 real-world context 中包含若干历史事故/CVE 类表述，本次没有逐条核其一手来源，不将其转写成我们的论文事实。

以下短号供上文行号定位；所有位置属于同一个固定 commit：

| 短号 | 本地源码 | SHA-256 |
|---|---|---|
| G | [生成器](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/generators/gen_cross3_protocol_bridge.py:1) | `41c614cadd1ba3f4afb9d189677761843727a09e32ae98bc2ad06cac0b414836` |
| S | [spec](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/tasks/CROSS3_protocol_bridge/spec.md:1) | `8366b7c16e13b2802add1d5460d6a3d0dd81f6c7f61554d8369188c7c717c17d` |
| B | [brief](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/tasks/CROSS3_protocol_bridge/brief.md:1) | `8038d14f36fe7a6c6401e1592b0018852381c432960faa84722b99e4938b3186` |
| R | [native grader](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/tasks/CROSS3_protocol_bridge/grade.sh:1) | `b86c5667b0fa0710de4da574c87d82a7336b8a3ebe7d4c8e7cd3605f00686116` |
| T | [任务配置](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/tasks/CROSS3_protocol_bridge/task.yaml:1) | `e94929cf6f6244e83d7f8691db60c5d667b8a1038fb6baa14642d780707225a8` |
| A | [分析提示](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/tasks/CROSS3_protocol_bridge/analysis_guidance.md:1) | `d89c7e8a0fcf1b955f797a7511d7b1647601e36c20f7f08351b4d1d94bb9c4cb` |
| H | [通用评分入口](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/harness/grade_task.py:1) | `fac2e10b561924d5a3d9a0eb2ce8da987a90b4d7a04a6fc1dcfd28fd31a23501` |
| I | [原生角色接口](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/harness/agent_interface.py:309) | `110a67d21380529150f2ffdde12555653b02069981e45ed91876a456020a4a44` |
| O | [原生编排](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/harness/orchestrator.py:442) | `cfc45da3e78fa0b67fd6ee46f965978a332142007715842cb60426ca7fb2402f` |
| — | [生成基类](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/generators/base.py:105) | `5f72d5e9abecbc7c738211020f8ed00f60977f4b383a1b8a72f2c9104c3f30ba` |
| — | [README 许可说明](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/README.md:157) | `bc740f246515dcbc3207b7de4f4fe173b0415b681ab89291e9798c30a6476277` |
| — | [MIT LICENSE](/Users/jingwu/work/earning-roles/references/benchmark_sources/TeamBench/LICENSE:1) | `0c0d65e201383b8ff6f4265fc09d03278e5308ec1bb9541d5cc96647505aaadc` |

## 判决与下一步：本轮停止接入

**原定代码交付型第二 root：NO-GO。** 决定性原因是原下游工作已经完成，而非 runtime 尚未搭好；继续给它加隔离、补测试或跑 LLM 不能解决这一点。本轮不做 CROSS3 adapter、native 执行、LLM 采样或 A800 实验，也不把它记为已获得第二个合格 root。

**可复用资产：保留原计划→实现流程和公开接口/测试义务。** 它们已经固定在本地，本文的职责与依赖表可直接用于下一次任务资格审查，不需要扩大搜索或重复实现。

**最少下一步是完成一张新协议资格卡的纸面审查，不是开实验。** 资格卡只需固定上表的信息清单、诊断与实现分离的评分、六项需求直接转发的对照，以及“没有增量信息/成本价值就停止”的规则；特别标明排除人工解答 guidance 是前瞻协议改动。只有这些项与论文的交付定义一致，才有理由讨论一次有界资格验证。

若主线需要两个同为“代码交付 → 下游独立集成”的 root，或不接受改变交付类型，CROSS3 当前候选直接关闭。若允许诊断报告作为真实交付，也维持 **CONDITIONAL / 未准入**：公开提示可能导致无可学信号，不能为凑第二个 root 而先写 runner、削弱对照或扩大采样。
