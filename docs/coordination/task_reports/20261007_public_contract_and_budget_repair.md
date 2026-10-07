# 公开合同与实验预算纠偏 — 2026-10-07

状态：`PARTIAL / NO_NEW_API`；`goal_change_requested=false`。

## 目的与通过标准

先保证接收方看得到被考核的要求，再测它是否判断正确。本轮修复公开合同、核对
累计预算，并封存最多四次判断调用的候选卡，不训练选择器，不产生论文效果结果。
通过标准：v2 保留 v1 源码及职责；硬评分条件有可见行为条款；不泄露解法或私有
测试；四格实际载荷与标签可核对；旧预算超额时新卡不能执行。

## 发现的科学问题与解释更正

旧适配器删除源码注释和 docstring，并把原生说明替换成通用互通要求。原生说明
既有 `.isoformat()` 解法提示，也有“时间戳必须含 T”的行为要求；两者被一起删除。
私有 Qp 的 `P2_iso_serialization` 与 adoption 的 `A1_producer_boundary` 却仍把
T、无空格作为硬条件。

producer 可见的 sink 不检查时间格式；processor 接受空格分隔时间并规范化输出。
因此旧 Qp FAIL 不能证明 producer 违反了 **actor 当时可见** 的合同，更不能证明
recipient 接受是误判。旧分数仍表示“未通过该私有/原生格式检查”。这里不主张一般
ISO8601 必须只用一种分隔符。此外，终端检查精确比较规范化时间和大写 action，
旧公开文本也未明示保留这些转换。

两名独立 Codex 审查者对照公开源码、原生 spec 与 scorer 确认上述缺口。审查将
修复从“只恢复 T”扩展为恢复全部被测的可观察转换，未把审查意见当作效果证据。

- [旧适配器](../../../scripts/peerrolebench_pipe3_material_adapter.py)保持不变。
- [v2 合同](../../../scripts/peerrolebench_pipe3_public_contract_v2.py)复用旧源码及
  文件权限，仅修公开条款/条款引用、manifest 版本与载荷摘要。
- [固定原生材料](../../../references/aamas/task_signal_materials_20261007/README.md)
  来自 TeamBench commit `d185aef1916fd86a9ba554d581fd256319a973af`。
- [先前终端分析](20261007_independent_y_integration_audit_v2.md)的“局部合同违规”
  用语由本次限定；历史分数、API 响应与日志均不更改。

新材料不公开修改函数、bug 位置、隐藏输入或预期输出。私有评分逻辑未改；新材料
与已有 scorer 版本共同构成新测量条件，不能与旧提示条件直接合并。条款—检查
映射仅表示有限覆盖，不保证 scorer 查出所有违约。

## 预算管理问题

[独立清点](../../../experiments/logs/n03_attempt_budget_census_20261007_v1/summary.json)
核实 **31 次任务 episode 尝试、68 次任务 API request_start**，超过含 N02 的原定
24 次上限。23 次走完记录的执行路径、8 次 UNKNOWN；完成路径不等于任务正确或
学习有效。非任务健康探针未混入 episode 分母。

| 类别 | episode | 任务请求 |
|---|---:|---:|
| N02 v1–v3 | 4 | 8 |
| N03 neutral prepare | 2 | 6 |
| PIPE3 real smoke v1–v6 | 6 | 16 |
| C1 bounded live v2–v4 | 15 | 30 |
| parent source 与三条 target | 4 | 8 |
| 合计 | 31 | 68 |

共享源只计一次，重复副本不重计；超时与失败占尝试。无法给未留痕的外部调用确定
全局上界。即使采用无争议下界 25，也已经超限。
根因是局部卡有限额，却没有在新卡启动前统一核对累计上限。这是执行管理失误，
不是用户同意增额。本轮新增 API/GPU 均为零；新卡执行关闭，具体卡审查完成后才
请求新增四次预算。不能把改版本当预算重置，也不声称旧所有入口已增加全局拦截。

## 下一张最小卡及收益

四格交叉两种既有 producer 与两种 recipient：历史真实 API 修复产物和原生未改
控制。分别判断 producer 合规性、processor 自身是否需修改；后者以合规上游输入
为前提，不能让 recipient 替 producer 违约负责。

同一公开合同、源码清理、模型配置和无历史请求；顺序封存，结果/来源/正负标签仅
保留在 parent。预注册逐格双字段核对；全部正确仅说明固定四格可分，不估计总体
准确率，不证明泛化、采用或收益，也不能排除代码风格捷径。不会自动追加 action。
用途是先查“评价到底在评谁”，而非在已饱和的同根任务继续堆多臂结果。

[具体四次调用卡](../../research/candidates/scoped_judgment_four_call_card_20261007.md)
与四份请求已封存。两份 producer、两份 processor 的本地独立检查均符合预期：
历史产物各三项 PASS；原生 producer 仅时间格式 FAIL；原生 processor 发生自身
UnicodeEncodeError，其下游两项受阻。四次沙箱执行不是四次 API 或学习实验。
准备 v1 因检测到 dirty 外部 checkout 中止，未保存当时具体 porcelain 输出；随后
检查 clean，原因未确定。保留该 UNKNOWN 和事后记录，补齐错误明细记录后 v2
准备通过，未改 native 数据。新 prompt/API 尚未执行。

独立审查还发现 C6 漏写金融域 `txn_type`；v2 合同已补齐三个公开字段类型，
首轮测试快照保留。审查拒绝用代码来源直接充当 gold，故新增上述独立本地检查；
也要求将“零候选执行”限定在 prepare/judge 阶段，单列四次预检执行成本。

[最终有限检查](../../../experiments/logs/n03_public_contract_v2_20261007_v2/)
中两项材料测试覆盖三个域、语法检查、六类唯一 ACTIVE 与文档一致性通过。不是
科学验收：机器 gate 仍 `scientific_readiness=false`。正文目前由独立图稿任务编辑，
本轮没有覆盖共享 LaTeX 或把这些诊断填进正式效果表，也没有声称新编译 PDF。

## 与 Goal 和三份标准对照

| 标准 | 本轮推进 | 仍缺什么 |
|---|---|---|
| 故事线/创新 | 不把测量遗漏当 judge 错误，维持观察/收益分离 | 自然评价的增量，超过计数及客观质量控制 |
| 方法论 | 对齐可见义务、判断对象和独立标签 | 真正后续执行、合法更新、更新后的收益与泛化 |
| benchmark/baseline | 修任务公平性，收敛小卡并核对预算 | 第二 root、任务冻结、完整强对照与统计结果 |

三份标准仍 `NOT_READY`，scientific gate 关闭。Goal 和生效研究含义没有降低，
ADR0049 继续有效。复用 pinned 原生规范、真实交付及已有 scorer；不启动 A800。
