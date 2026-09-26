# ArtifactRole-TB：协议与评分器的开发验证

初稿：2026-09-25；更新：2026-09-26。

范围：现有程序夹具与接口探针的证据核对；没有新增 LLM 或 GPU 实验。本文不宣布方法有效、benchmark 冻结或科学门通过；G0–G7 以 [AAMAS_TASKS](../coordination/AAMAS_TASKS.md) 为准。

## 本次验证回答的问题

修正后的 runner 检查：过去反馈记录的 assignment，能否决定下一次执行前的 peer 选择；消费者的使用、修复或重做，能否生成实际被终局评分的产物。两个参数化任务为 `CR2_style_enforce` 和 `DIST1_queue_race`，各用 seed 0、1；TeamBench 固定版本为 `d185aef`。

三个常驻对象都是手写程序夹具，不是真实 LLM agent：

- `peer_01_noop`：保留生成器的错误代码；
- `peer_02_repair`：运行预先写好的修复；
- `peer_03_partial`：DIST1 只修优先级比较器，CR2 保留初始代码。

四个条件 `random`、`static_best`、`terminal_only`、`recipient_judgment` 用于走通控制器分支，不能视为合格的论文 baseline。`static_best` 预设选择 repair 夹具，没有独立开发集资格结果；两个更新条件只是标量滑动更新，不是最终方法。

## 已修复的执行语义

依据 [ADR 0015](../user/decisions/0015-select-before-execution-and-bind-later-assignment.md)，程序按以下顺序执行：

> 选择一个 peer → 开始任务 → 仅选中 peer 交付 → 封存消费者判断 → 实际 use/repair/redo → 对消费产物独立评分 → 更新证据 → 写入并使用下一轮 assignment。

旧实现先生成所有 peer 的产物再挑选，并且下一轮忽略已记录 assignment。这测量的是事后产物筛选，无法支撑未来责任分配。当前 runner 只执行选中的 peer，下一轮直接读取 assignment 的对象与概率。随机条件使用带固定种子的真实 `rng.choice`，不是轮转序列。

消费者 `use` 直接使用交付，`repair` 从交付副本开始修复，`independent_redo` 从重新生成的初始 workspace 开始修复。终局 grader 读取消费后产物。修复与重做都调用同一套手写 repair，这是一项控制器测试安排，不代表真实消费者具备该能力。

strict ledger 要求选择在 task start 前、交付属于选中者、判断与动作一致、结果到达后才更新，以及后续选择保留 assignment 的概率。根据对 peer A 的负面评价改选 peer B 是合法行为，不能因 assignment 与被评价者不同就判错。2026-09-26 后续入口加固还拒绝同一 judgment/action 换 ID 重复更新、selection 后补写 assignment；当前协议测试为 15 项通过。causal_v2 运行早于这两项加固，不能反向视为新版本的运行记录。

## causal_v2 的逐样本核对

证据：[config](../../experiments/logs/peerrolebench_tb_vertical_20260926_causal_v2/config.json)、[raw.jsonl](../../experiments/logs/peerrolebench_tb_vertical_20260926_causal_v2/raw.jsonl)、[summary](../../experiments/logs/peerrolebench_tb_vertical_20260926_causal_v2/summary.json)。

| 检查 | 观察结果 |
|---|---|
| 完成数与耗时 | 16 episode；34.487 秒；0 次 LLM 调用 |
| 选中后执行 | 16/16 行只有选中 peer 标记执行 |
| 后续分配使用 | 8/8 第二轮 episode 消费先前 assignment |
| random 选择概率 | 4 条记录均为 1/3，包括第二轮 |
| 消费者动作 | use 5、repair 9、independent_redo 2 |
| 评分副本来源 | 16/16 candidate source digest 等于 evaluator 执行前 source digest |
| 评分前后完整性 | 16/16 消费产物、评分源文件、tests、expected 哈希不变 |
| 终局分数 | 均值 0.8958，最小 0.5833，最大 1.0 |
| 科学主张资格 | `scientific_claim_allowed=false` |

同任务/seed 下，四个条件的终局分数完全相同：CR2 seed 0、1 都是 1.0；DIST1 seed 0 是 1.0、seed 1 是 0.5833。因此本轮没有 selector 收益，不能把修复环境与消费产物之后的高均分解读成方法进步。

两个原因直接限制了结果解释。第一，`fixture_judgment` 根据 peer 身份固定返回 0.9 / 0.5 / 0.2 及对应动作，不读取真实交付质量。第二，repair/redo 均转入同一套修复，掩盖了选择较弱 peer 对终局质量的影响；`repair_cost` 只记 0/1，无法还原实际返工代价。真实接入时必须分别保留交付质量、实测返工成本与最终质量。

## 失败记录与修复依据

旧记录全部保留，不用修复后的结果覆盖它们：

| 记录 | 观察及解释 |
|---|---|
| [secure_v4](../../experiments/logs/peerrolebench_tb_vertical_20260925_secure_v4/summary.json) | 历史 16 条夹具均分 0.3196，25.14 秒；含旧执行/消费语义及评分适配问题，不能与 causal_v2 当作方法前后比较 |
| [CR2 首次资格检查](../../experiments/logs/peerrolebench_cr2_fixture_qualification_20260926/summary.json) | seed 0 为 12/13，seed 1 为 3/13；尾逗号未修，以及 allowlist 写死 `test_helpers.py`、未复制 seed 1 的 `api_client.py`。旧报告把低分仅归为模型泛化是不完整的 |
| [CR2 修复复核](../../experiments/logs/peerrolebench_cr2_fixture_qualification_20260926_v2/summary.json) | 从 seed 对应生成器代码修复；grader 按 evaluator 元数据选择应复制的模块；两个 seed 均为 13/13 |
| [DIST1 资格检查](../../experiments/logs/peerrolebench_dist1_fixture_qualification_20260926/summary.json) | 缺少 `pytest-timeout` 会使原生 `--timeout` 检查变成环境失败。安装 2.4.0 后，seed 0 初始产物 6/12，repair 12/12；仅证明该 seed 的运行环境与评分能区分产物 |
| [causal_v1](../../experiments/logs/peerrolebench_tb_vertical_20260926_causal_v1/raw.jsonl) | assignment 被使用，但 random 的第二轮 propensity 错写为 1.0；v2 保留原采样概率修复了此项 |

当前 config 保存运行时命令、HEAD、工作区状态摘要、runner/protocol 哈希、Python/系统信息与依赖可用性。执行时 runner SHA256 为 `c79a29aeedcce99427cc62575f3c4bf636e0f7e54e4ab16d28bb9a4ad49381f1`，protocol SHA256 为 `f34d2a0277c893a199bc42fdb48e01504bc5a08aa335307be21f7caa5bf63a71`。当前代码可继续修改，不得冒充这些历史字节。

raw 按 episode 流式落盘，保存逐项 score、产物路径和 ledger snapshot，但没有逐事件导出全部 `ledger.events`。哈希与 snapshot 不等于已经有可独立重放的完整事件证据；下一轮应冻结实际源文件并导出选择、开始、assignment 和反馈到达事件。

## 真实模型接口探针的准确边界

[2026-09-25 原始探针日志](../../experiments/logs/peerrolebench_real_judgment_20260925/raw.jsonl) 包含三次真实尝试：一次 TLS 错误，一次真实响应后被本地 `api` 变量错误误标失败，一次成功重跑。两份真实响应都被保留，后处理纠正单独记录。

成功重跑的 `qwen3.8-max` 返回 `accept`、预测 0.90、置信度 0.62，报告 256 输入与 700 输出 token。早先那份响应是 `accept_with_rework`、预测 0.78、置信度 0.55，其用量不完整。config 的 `real_api_call_count=1` 仅对应最后的成功记录，不能拿来代表整个探针预算；TLS 失败行中的零用量也不能证明实际未计费。

探针只提供人工撰写的任务/diff 摘要，artifact digest 是 `a` 重复 64 次的占位值，没有让消费者检查实际源文件或执行动作。prompt 确实没有包含 grader、expected 或终局分数；它只能支持传输、JSON schema 和该条 prompt 的信息内容已检查，不能支持实际产物绑定或完整隔离已成立。模型返回的判断没有进入 selector 更新。

## 未关闭的资格问题与下一步

TeamBench 原生 grader 不是完整 sandbox。新 evaluator、source allowlist、只读 tests/expected 与哈希检查降低了“通过改测试得分”的风险，但相同用户下的只读权限不能构成不可绕过的安全边界；被执行的源代码仍可能读取 sibling reports。所有 16 条记录的 `candidate_grader_sandboxed_from_sibling_reports` 都是 false。

下一步按主台账 N01 完成实际文件/网络隔离、正常与错误产物评分、越权读取负例，并核实每个任务是否存在真实上下游依赖。开发与留出应按任务 root 划分，不能把同生成器不同 seed 自动视作独立任务泛化。只有这些资格满足后，才运行已批准的最多 4 条真实接入尝试；不得把当前两个任务族、四个夹具条件或高终局分数宣布为最终 benchmark/baseline。

本轮可复用的是原生任务生成器/scorer、选择与反馈账本、消费产物的 lineage 和逐样本审计接口。它们推进了原始故事的可测性；判断是否包含有用角色信息、能否帮助他人后续分派、怎样低成本实时更新，仍需后续真实证据。
