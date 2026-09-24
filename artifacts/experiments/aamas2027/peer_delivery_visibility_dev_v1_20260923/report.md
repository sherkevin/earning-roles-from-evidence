# 交付可见性配对开发诊断：两臂均在审阅额度处删失

已按前瞻冻结顺序在同一 AppWorld train 任务 `3c13f5a_3` 的两个全新、初态内容指纹相等的世界运行 visible → hidden。两臂都在 8 次审阅模型尝试后未封存事前计划，均未进入行动；因此**不能判断交付可见性的任务质量或净成本效应**。这不是官方失败率、方法负结果或角色学习实验。

| 臂 | 模型尝试/响应 | 公开 GET / 任务数据 GET | 计划/行动/任务写入 | 状态 |
|---|---:|---:|---|---|
| visible | 8/8 | 19/1 | 无/无/0 | UNKNOWN/review cap |
| hidden | 8/8 | 28/8 | 无/无/0 | UNKNOWN/review cap |

两个臂均无 `complete_task` 调用，官方 evaluator 未运行，任务状态断言、完成答案断言和整体 success 均为**未测**。旧 v4 交付逐行采纳/修改/舍弃也无法审计，因为没有行动。visible 直到第 8 步才首次成功读到任务数据，且仅为文件目录；没有读账单金额或室友联系人。hidden 在第 4/5 步读取目录、日期及账单文件，第 8 步只查询联系人关系类型，仍未查到实际室友条目。两臂各有一次 phone 登录失败并在后续尝试修复；这些是公开 API 轨迹，不能把审阅 cap 归因于 API 故障或交付质量。目录 GET 本身也不足以支持金额/收件人主张，须逐项来源审计。

成本 token 顺序为 input/output/cache-read/cache-creation；均为提供商报告值：

| 口径 | 请求 | token 四类 | provider API 秒 | 未知用量 |
|---|---:|---:|---:|---:|
| visible 接收者 | 8 | 12385/2054/45696/0 | 66.594 | 0 |
| visible 全系统（含历史生产者） | 15 | 27054/9613/87168/0 | 276.442 | 0（历史报告口径） |
| hidden 接收者 | 8 | 13346/3486/40960/0 | 102.235 | 0 |

共 16 次真实任务请求、16 次返回、0 次传输错误；另有独立健康请求 1 次，不计入任务额度。两个臂都按冻结规则自然结束，父进程写有 `both_arms_terminal_barrier` 和 `run_final`。受审阅额度删失，预定的质量—全系统成本解释门为 **INDETERMINATE**；不能把 visible 更高的成本或 hidden 更多的读取解释为交付的因果效果。

**冻结协议字面偏差：** AppWorld 包在导入 `AppWorld` 时隐式导入 `appworld.evaluator`，所以“两个 actor 封存前评分模块不得 import”并未满足。用相同虚拟环境做的零模型 `sys.modules` 复核为真，而实际 actor 进程没有直接记录 `sys.modules`；源码顶层导入加上已记录的世界初始化构成这一判断。两臂 `load_ground_truth=False`，actor 期间没有`evaluate_task` 调用，也未观察到标签或评分进入模型；`scorer_barrier_completed` 只能表示**显式离线评分调用屏障**，不能表示模块未导入。偏差的[原始核查](protocol_import_deviation.json)单独保留，不改变两臂删失及不可判定结论。实际首请求的[字节隔离核查](postrun_initial_prompt_isolation_audit.json)则确认初始模板仅交付槽不同。

该任务由已观察到交付结果的 train 单例事后选出，AppWorld 原生是单用户任务；本配对只诊断交付可见性，既无自然多主体协作依赖，也无跨任务角色状态。下一步需要另行冻结多家族或自然依赖任务的探针，不能在本例按结果调提示或额度。

原始结果：[results.json](/Users/jingwu/work/earning-roles/artifacts/experiments/aamas2027/peer_delivery_visibility_dev_v1_20260923/results.json)；逐次日志：[run_raw.jsonl](/Users/jingwu/work/earning-roles/artifacts/experiments/aamas2027/peer_delivery_visibility_dev_v1_20260923/run_raw.jsonl) 与各臂 `raw.jsonl`；机器汇总：[processed_results.json](/Users/jingwu/work/earning-roles/artifacts/experiments/aamas2027/peer_delivery_visibility_dev_v1_20260923/processed_results.json)。

配置 SHA256 `b268aa7bfaaa39516e25a15dba4daf206607507bb131d3d78ba4cdcaefbb9a10`；runner `a8f513bc579f84c51d6ce4f7ff0961579837129a75341918cc3af3748539d1c7`；协议 `ee5c565606590945ae9ea354d06631979da730686aebfc3f39506daaef724c91`；results `36f4e567a11abaa182fc044a707bca44f0cb30c796b9395ea469789281edf656`。
