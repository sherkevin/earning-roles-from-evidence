# experiment.md

## 0. 文档定位

这是本项目当前阶段的**权威实验执行规范**。

它的目标不是介绍方法，而是统一 5 件事：

1. 当前主线实验到底用哪个模型。
2. 旧结果和新结果分别在论文里扮演什么角色。
3. 实验被打断之后必须如何断点续跑。
4. 中间日志和 checkpoint 应该如何保全。
5. 工程师向 coordinator 汇报时必须写哪些关键信息。

若后续工程实现、工程师任务文件、口头讨论与本文件冲突：

- 先把冲突记入 `implementation_log.md`
- 再由 coordinator 明确覆盖
- 未被明确覆盖前，以本文件为准

---

## 1. 当前绑定决策

### 1.1 主线 backbone

当前主线实验统一采用：

## `gpt-4.1-mini`

这是当前阶段的主论文 backbone。

原因：

- 国际会议审稿人辨识度高；
- 比当前 GLM-only 路线更适合作为主论文证据；
- 成本和能力在递归多 agent 实验里更平衡；
- 更能避免 reviewer 将组织失败误判为“底层模型太弱”。

### 1.2 主表实验的模型政策

主表实验必须遵守：

- 单一 backbone；
- 同一实验包内所有 agent 使用同一 backbone；
- 同一对比表内所有方法使用同一 backbone；
- 主表禁止使用 mixed-model society。

多模型异质社会目前只能作为：

- appendix；
- stress test；
- future work；

不能作为当前主论文主表的主实验设置。

### 1.3 旧 GLM 结果的定位

已有 `GLM-5.1` / `glm-4-flash` 相关结果**不删除、不否定**，但统一降级为：

## `Stage-1 guidance-only artifacts`

也就是说，这些结果仍然有价值，但其用途变成：

- 历史对照；
- 受限原型证据；
- sanity comparison；
- 方法演化记录；

不再作为新的主线 headline evidence。

---

## 2. 实验类型与口径

当前实验分为 3 类：

### 2.1 Mainline experiment

指未来要进入主论文主结果表、主分析或核心结论的实验。

要求：

- backbone = `gpt-4.1-mini`
- 单一模型社会
- 必须 resume-safe
- 中间日志必须完整保留
- 必须清楚区分 config label 与 actual resolved runtime model

### 2.2 Stage-1 archived experiment

指已完成或已部分完成的 GLM 路线结果。

要求：

- 保留原 run dir；
- 不覆盖、不删除；
- 在 summary 或 note 中明确标记为 `Stage-1 guidance-only`；
- 可以引用其经验，但不能混淆成当前主线。

### 2.3 Reviewer-loop / diagnosis experiment

指 reviewer 批次、敏感性分析、小规模 smoke test 等支持性实验。

要求：

- 也必须写清楚模型口径；
- 也必须保留中间日志和归档；
- 若脚本本身不支持严格 resume，则至少保留已完成归档并增量继续，不得抹掉旧结果。

---

## 3. 模型与 provider 记录规范

### 3.1 必须记录的四个模型字段

每次实验都必须区分并记录：

1. `intended_backbone`
2. `config_label`
3. `actual_resolved_model`
4. `provider_endpoint`

含义：

- `intended_backbone`：本次实验想用的 backbone，例如 `gpt-4.1-mini`
- `config_label`：config 文件中写的模型名
- `actual_resolved_model`：运行时真正发给 API 的模型名
- `provider_endpoint`：请求实际走的 endpoint / provider path

### 3.2 禁止的坏口径

以下写法都不合格：

- “配置里写了 `gpt-4.1-mini`，所以这次就是 `gpt-4.1-mini`”
- “llm.json 里列了很多模型，所以应该用了其中某个”
- “默认应该就是新模型”

只有在 summary 或 artifact 中明确记录了 `actual_resolved_model` 后，才可以对外宣称某次实验使用了某个 backbone。

### 3.3 当前已知风险

当前仓库曾存在这样的问题：

- `configs/*.yaml` 里的 `main_model` 主要是日志标签；
- 主实验运行时可能仍通过 `workspace/idea04_core/llm_client.py` 的默认值发起请求；
- reviewer 脚本又可能走另一条单独的模型配置路径。

因此，模型口径必须显式记录，不能凭想当然。

---

## 4. 运行前检查清单

每次发起实验前，工程师必须先确认以下事项：

### 4.1 基本设置

- 实验类型：`mainline` / `stage-1 archive` / `reviewer-loop`
- backbone：本次 intended backbone 是什么
- provider：本次请求要走哪个 endpoint
- samples：本次样本文件是什么
- methods：本次跑哪些方法
- topology：`chain` / `star` / 其他

### 4.2 运行目录策略

- 是否新建 `run_*` 目录
- 是否应该复用已有 `run_*` 目录并 resume
- 是否存在旧 partial run 可继续

### 4.3 环境检查

- API key 是否已注入当前 shell
- endpoint 所需环境变量是否齐全
- 运行命令是否已写入 summary 草稿或 run note

### 4.4 日志策略

- 本次运行是否会产生 checkpoint
- 若中断，恢复命令是什么
- 谁负责在 summary 中登记中断点

---

## 5. 断点续跑规范

这是本文件最重要的部分之一。

## `长实验默认必须断点续跑，不得轻易从头跑。`

### 5.1 总规则

- 如果 run dir 存在且日志完整，优先 resume。
- shell 断开、IDE 关闭、网络闪断，不构成重头跑的理由。
- 只有在 run dir 明确损坏、checkpoint 不可读、或输出彼此冲突无法修复时，才允许放弃该 run dir。
- 放弃旧 run dir 时，必须写明：
  - 为什么不能 resume
  - 哪些日志仍可保留
  - 新 run 与旧 run 的关系

### 5.2 当前脚本支持

当前主实验脚本：

## `scripts/run_round1_v3.py`

已支持：

- `--resume-run-dir <RUN_DIR>`

因此只要已有 run dir 还在，就应优先走 resume，而不是新建目录重跑。

### 5.3 标准恢复流程

1. 定位原 run dir。
2. 检查是否存在关键中间文件：
   - `_ckpt_preds.jsonl`
   - `routing_traces.jsonl`
   - `handoff_packets.jsonl`
   - `raw_model_outputs.jsonl`
3. 记录当前已完成样本数。
4. 用同一个 run dir 重新发起命令，并加上：
   - `--resume-run-dir <RUN_DIR>`
5. 在 summary 中写明这是一次 resume，而不是 fresh run。

### 5.4 不允许的做法

- partial run 还在，却重新建新目录从 0 开始跑
- 已有 checkpoint，但因为“懒得查”就直接重头跑
- 覆盖旧 run dir 却不说明
- 删除旧 run dir 中间文件以“节省空间”

---

## 6. Run 目录与命名规则

### 6.1 run dir 原则

每个实验包应有唯一 run dir，例如：

- `artifacts/round1/run_YYYYMMDD_HHMMSS`

原则：

- 新 backbone 的主线实验应使用新的 run dir；
- 同一个实验包的 resume 必须继续写回同一个 run dir；
- 不同 backbone 不能混写到同一个 run dir；
- archive run 与 active mainline run 必须清晰区分。

### 6.2 archive 标注

旧结果一旦被降级为 archived Stage-1 guidance-only，至少要在以下之一中留痕：

- `agent-i-summary.md`
- `run_notes.md`
- 独立 archive note

需要写明：

- run dir
- backbone
- 当前状态
- 为什么归档
- 是否仍可作为 sanity comparison

---

## 7. 日志与中间资产保护规范

中间日志不是临时调试垃圾，而是论文资产。

## `中间日志必须被视为核心研究证据。`

### 7.1 必须保留的主实验资产

以下文件默认必须保留：

- `_ckpt_preds.jsonl`
- `routing_traces.jsonl`
- `handoff_packets.jsonl`
- `competence_snapshots.jsonl`
- `raw_model_outputs.jsonl`
- `parsed_predictions.jsonl`
- `metrics.json`
- `run_notes.md`
- `case_studies.md`
- `failure_cases.md`

### 7.2 论文级派生资产

以下派生文件也要保留：

- 合并 CSV 表
- Markdown summary
- paired statistics 输出
- mechanism ablation note
- robustness note
- reviewer archives
- scoreboard / fix themes

### 7.3 对日志的禁止操作

- 不得随意覆盖旧日志
- 不得因为 rerun 就删除 partial logs
- 不得把无效 run 混进有效结果而不标注
- 不得只保留最终 `metrics.json` 而丢掉中间轨迹

### 7.4 远端镜像建议

重要实验与日志最好同时具备：

- 本地副本
- 远端备份副本

若当前 session 无法完成远端镜像，也必须至少在 summary 中注明是否已做 remote mirror，以及由谁补做。

---

## 8. 工程师 summary 最低记录标准

每个工程师在 `agent-i-summary.md` 中的每个 session 至少要记录：

- 日期
- 目标
- 精确命令
- run dir
- 样本文件
- 方法列表
- intended backbone
- actual resolved runtime model
- provider endpoint
- fresh / resumed
- 关键指标
- validation 结果
- blocker / anomaly
- next recommendation

如果中断过，还必须补充：

- 中断前完成到第几条样本
- 中断原因原文
- resume 是否成功
- 若未 resume，为什么没有 resume

---

## 9. Mainline relaunch 规范

当前主线已经决定迁移到 `gpt-4.1-mini`。

因此新的 mainline relaunch 必须按以下顺序进行：

1. 先修 backbone control，确认 runtime 真正可控。
2. 做小规模 smoke test，确认：
   - actual resolved model 正确
   - endpoint 正常
   - logs 正常落盘
   - resume 机制正常
3. 再启动新的 `200`-sample baseline / sensitivity package。
4. 最后再启动新的 `7405 fullval`。

禁止顺序：

- 在 runtime backbone 还没确认前就直接开新 fullval
- 跳过 smoke test 直接发起长跑
- 用不明模型口径的结果更新主表

---

## 10. Reviewer-loop 特别规定

reviewer-loop 虽然不是主实验，但也属于研究证据链的一部分。

### 10.1 reviewer 批次原则

- 已完成的 reviewer archive 不删除
- 新 reviewer 批次只增量追加
- scoreboard 和 fix themes 允许刷新，但要能追溯到具体 reviewer 目录

### 10.2 reviewer 模型记录

每次 reviewer 批次必须单独记录：

- reviewer model
- reviewer endpoint
- prompt 版本
- parseable / scored 情况

### 10.3 不允许的做法

- 静默切 reviewer model 却继续横向比较分数
- 只保留 scoreboard，不保留单个 reviewer 归档

---

## 11. 何时必须升级给 coordinator / 用户

出现以下情况必须立即上报，而不是私自继续跑：

1. `gpt-4.1-mini` 无法真正被 runtime 解析或调用
2. provider endpoint / key contract 不清楚
3. run dir 明显损坏，resume 失败
4. checkpoint 文件不可读或与输出互相冲突
5. 多次 provider/network 失败导致 run 长时间无法推进
6. config label 与 actual runtime model 不一致
7. 新 backbone 下结果与旧口径差异极大，需要 coordinator 决定如何叙事

---

## 12. 当前阶段的最小执行准则

把所有复杂规则压缩成一句话，就是：

## `先确认模型真在跑，再保住日志，再从断点继续，最后才谈主表更新。`

当前阶段每位工程师都必须遵守：

- 不用混模型社会写主表；
- 不把旧 GLM 结果冒充新主线；
- 不把长实验当成一次性命令；
- 不把中间日志当成可丢弃副产品；
- 不在模型口径不清时更新论文主结论。

这份文档从现在开始就是本项目实验执行的统一规范。
