# 已知单例的交付可见性配对开发诊断：前瞻冻结协议

2026-09-23 09:53 UTC 初稿；同日零模型审计后前瞻冻结。**状态：FROZEN_PROSPECTIVE_PAIRED_DEV_V1；冻结时尚未调用本协议的模型。** 本协议只测试在同一初始任务状态下，一份已存在的生产者交付是否改变两个全新接收者的公开复核、任务写入与系统成本。任务 `3c13f5a_3` 是 AppWorld train 已知单例，因历史 v4+v5 已出现交付和使用而被事后选中；本次不产生未见确认样本、总体因果效应或角色学习证据。必须先通过与最终配置/runner SHA 完全匹配的无 LLM preflight 和独立 provider 健康检查，才能开始任何任务调用。

## 固定输入与唯一干预

- 只用 `3c13f5a_3`，AppWorld 数据 `0.2.0`、源码提交 `42b5bcf3cd334fee33f0c37c02070a9f5807add5`、`random_seed=100`。两个新的、名称不同的 recipient 实验世界均 `load_ground_truth=False`、`raise_on_extra_parameters=True`，使用相同公开工具列表、安全门禁、任务说明、`supervisor` 身份与公共基础提示。AppWorld 初始化会调用进程内 `close_all()`，因此两臂必须用隔离子进程；各进程先只做初始化与 controller-only 逐表排序 `(id, record_hash)` 内容指纹、`ModelCollection.model_hashes()` 写入计数、公开任务说明/日期指纹，均到达准备屏障后由父控制器比较，**一致才允许第一条 actor 请求**。AppWorld 的 `model_hashes()` 只是写入计数，不被当作内容哈希；只读阶段同时监测计数和实际记录指纹。不一致即停机。历史 v5 初态未存这些指纹，所以本次只能确认**新配对内部**初态相同，不能声称与历史世界的逐表内容已直接比对。
- 路由固定 cc-switch `内部` 的 `qwen3.8-max`，temperature `0`，每次请求 `max_tokens=1024`（请求参数，非提供商硬输出上限；实际 token 和返回模型逐次记录）。两臂均从空模型历史开始，不继承历史 v4 被拒的 `import apis` 回复或 v5 修复反馈，不加载 R0/A0 结果、生产者私有 REPL、过去的消费者轨迹或私有 evaluator。
- 唯一预定 treatment 是**是否可见历史 v4 封存提案的原始字节**，其 SHA256 为 `899b77381ab580733ae5b16430452e09256b43bb38ad27ce8a7e960fef4d8dad`。`hidden` 初始提示的统一 `delivery` 槽只显示 `NO_DELIVERY`；`visible` 的同一槽放原始 `<delivered_proposal>…</delivered_proposal>`。其余初始提示文字、API 权限、工具响应格式、计划 schema、阶段额度和控制器规则相同。`hidden` 的模型消息和在线反馈绝不含提案或它的哈希。原 v4 提案三行均遗漏引用读到账单/联系人细节的第 6 步，故该 artifact 仅为既有处理对象，不能在提示里宣称逐项来源已证实。
- 执行顺序用可复现的一次预提交抽签固定：Python `random.Random(100).shuffle(['hidden', 'visible'])` 得 **visible → hidden**；算法、种子和结果均在任务调用前写入机器配置。两个子进程先创建世界并在初态屏障等待；相等后只释放 visible，待其行动与日志封存或删失，再释放 hidden。前一臂的提示、动作、结果、成本和评分不进入后一臂消息或策略。一次抽签不能消除时间漂移或支撑总体随机化效应，只避免研究者按预期结果挑选先后。

## 共同 actor 流程和提示边界

两臂均使用历史 v5 `render_native_prompt` 的公共部分：原生 task/supervisor/app descriptions、`apis.*` 文档发现、凭据仅经公开 supervisor API、REPL 只访问模拟环境，禁止 OS/私有 benchmark/evaluator。阶段专用补充文字应是同一模板，除了上述 `delivery` 槽，含义为：“你是独立接收者；先用公开只读 API 查证任务，在写入前输出一次 `<plan>{JSON}</plan>`；计划之后才可用公开写 API 完成任务。不要猜造实体、金额或凭据；不将 token/密码写入计划。”**不得加入**历史 v5 的评分、期望答案、三笔目标、金额或“调用 `complete_task` 时传 null”的提示。

共同计划最小 schema：`plan_status`（`ready/unknown`）、`planned_actions`（0–30 个 `{app, api, non_secret_arguments, public_source_steps}`）、`review_reason`、`uncertainties`、`delivery_assessment`、`intended_delivery_use`。`delivery_assessment` 对 hidden 必为 `not_available`，对 visible 为 `accept/repair/reject/unknown`；`intended_delivery_use` 对 hidden 为 `null`，对 visible 为布尔或 `null`。`ready` 计划须至少有一次本臂实际成功的公开任务数据 GET；每条计划动作引用的 step 必须是本臂实际成功的公开任务数据 GET。`ready` 的空动作仅可表示复核后有理由的无行动计划，离线仍检查理由，不能将其自动视为语义正确。在线门禁只验证来源存在与 schema，不用私有答案判断语义。若证据不足，两臂按**同一规则**可封存 `plan_status=unknown`、空动作、原因和不确定性（不需编造来源），并停在观察 `UNKNOWN`，或者在阶段额度耗尽时记 `UNKNOWN/cap`。visible 的 accept 意向、行动是否与交付行匹配、修改/舍弃/额外动作分开审计；hidden 没有可比较的 accept/use 指标，最多在**离线分析**中计算与原交付行的重合，不能把重合解释为使用。

零 LLM 的提示隔离测试须使用**合成哨兵交付物**，断言 hidden 的初始消息和控制器反馈没有从交付槽注入的原文字节、独有收件人/金额或私有评分字段；真实运行中 hidden 仍可通过自己的公开 API 自主发现与原提案重合的事实，不能把这种合法观察误判为泄漏。实现上 hidden 进程不能读取历史 proposal/scorer 文件；父进程只在启动前预检原 proposal 哈希，并于两臂进程终止后为离线匹配读取；visible 子进程仅在构造 delivery 槽时读取已钉哈希的 proposal。评分模块在两臂 seal 前不得 import。

每臂先只读 review，成功计划封存后才开启 action 写权限；两个世界不共享变量、数据库写入、模型历史或观测。各臂审阅 **8** 次、行动 **18** 次真实 LLM 尝试，上限 **26**；整个配对新任务调用最多 **52**，两臂和两阶段均不能借用额度。这个额度与原 v4 接收者的 review8/action18 **权益**一致；历史 v5 review7 是 v4 已收费的首次被拒审阅之后的余额，不应错误套给全新接收者。历史生产者 7 次模型调用不会重做，但要计入 visible 系统净成本，因此 visible 净尝试数=`7+visible recipient attempts`，hidden=`hidden recipient attempts`。历史 v4+v5 合链实际 15 次只作事前固定的描述性成本参照，不拿来截断新两臂预算。预定资源敏感性口径是**系统总 26 次调用**：visible 只有在 recipient 第 19 次或更早完成时满足 `7+19≤26`，hidden 在第 26 次或更早完成；若质量结果须越过界线才得到，就如实记“等总调用预算下未观察到可比质量”，不利用后续结果回填。此口径只是轨迹可行性标记，不是另一组随机实验，也不改变两臂的实际调用上限。

## 原始证据、停机与离线比较

执行前须另行冻结确切 prompt 模板、runner/config SHA、导入的 API/提示/控制器源码依赖 SHA、源提案 SHA、Python 虚拟环境与 AppWorld 安装/源码版本、两个 experiment names、阶段预算、provider 健康结果和零 LLM 原生 fixture。运行父进程和子进程均核对依赖 SHA，保存源码快照；每次请求、响应、使用量（input/output/cache 各类）、timeout/HTTP 错误、世界步骤、公开 API 读写及参数脱敏、计划/行动/完成回报、状态哈希、执行时间逐次写 JSONL；raw、processed、人工报告分文件。密钥/密码/token 不落盘。真实 provider 健康调用独立预算，不混入 52 次。金额/用户等公开任务值可进脱敏研究原始轨迹，不能借私有 evaluator 影响 actor。

同请求 `429/503` 至多重试两次，1、2 秒退避，每次计入当前阶段；`TimeoutError` 只在无返回响应、未解析/执行该次代码、请求消息/参数逐字节不变且本阶段有余额时每臂最多重试一次，计费并保留未知用量。其他传输异常或响应状态不明不重试，标记 `UNKNOWN/transport`。计划验证失败在原阶段给无私有答案的错误反馈并计费；额度耗尽是 `UNKNOWN/cap`，不是任务语义失败。初态不等、只读阶段**被门禁挡下的写企图或任何实际任务模型变更**、密钥日志或私有评估泄漏立即全局停止，不能继续下一次 actor 请求；不可为了配对完整性绕过安全门。一般 cap/传输删失仍按固定顺序尝试另一臂，以免按早期结果挑选，但配对质量比较记为不可判定；所有未启动状态保留。

两个 actor 行动与原始日志都**封存或明确删失**之后，才离线调用两臂官方 evaluator；评分不得影响第二臂提示、重试、行动或控制器修订。如果一臂没有可评估行动，离线评分可标缺失，不能补造结果。预定并列报告：公开任务数据复核次数和覆盖、事前计划与实际动作、正确/遗漏/额外写入、官方任务状态断言、`complete_task` 答案断言和整体 success；把最终答案错误与任务写入错误分开。成本同时列 recipient 自身及 visible 加生产者的净请求数、所有已报告 token 类、unknown usage、API 时间与墙钟时间；历史生产者已知为 7 次、14,669 input/7,559 output/41,472 cache-read tokens，历史合链 15 次、30,233/13,630/85,120 tokens，美元价格未经核实。不同时间的 provider 性能和缓存状态会影响耗时，不能把单例差额当稳定效应。

这两个 fresh recipient 世界可以更干净地比较“给定同一旧 artifact 的可见性”，但仍只有一个事后挑选的 train 任务、一份已观察到问题的交付、固定顺序、无重复种子和模型服务波动。最多报告**此条件下的机制开发诊断**；不作置信区间、显著性、总体因果或提高中稿率的主张。无论结果如何，都不直接升级为“learning roles from others’ judgment”：这里没有跨任务角色状态更新或后续职责分配。若交付对质量/总成本没有清楚边际价值，应如实记负结果；若有，也需要另行预注册未选任务、多种交付和真正角色学习对照。

**预定解释门**：主质量只看官方任务状态断言和公开写入的正确/遗漏/额外项；官方整体 `success` 与 `complete_task` 答案错误另列，不让单个答案字段替代任务状态质量。full system 成本对 visible **加上原生产者 7 次和全部已报告 token/API 时间**，hidden 只计本臂；因为没有核实 USD 价格，成本按“尝试次数、input/output/cache-read/cache-creation 各 token 类、API 时间”分别比较，未知用量使对应成本判断不可判定。仅当 visible 的任务状态质量更好且上述成本各项均不高，或状态质量相同而成本各项均不高且至少一项严格更低，才给出“此已选单例的正向局部可行性信号”。其他可评价结果记为本例**不支持交付边际价值**；任何一臂删失或成本关键项未知则记不可判定。无论出现哪种结果，都不能据此确认或否定 AppWorld 一般情形；不在同一已选案例上调 prompt/额度寻找好结果。下一步若仍有研究价值，另行冻结多任务家族的观察样本或有自然相互依赖的任务环境。
