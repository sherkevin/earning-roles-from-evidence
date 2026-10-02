# N03 前置设计：让第一次在线角色学习实验可识别

日期：2026-10-02
状态：`DESIGN_ONLY`，不替代 active benchmark/method 文档，也不解冻 API/GPU 实验。

## 目的

N02 的两条完整真实链证明了 API、delivery、judgment、consumer 和 delayed
assignment 可以在有限条件下连通，但没有产生学习效应：两次反馈映射都等于先验，
选择概率没有改变；两次 consumer 都只修改了自己的 `consumer.py`，而原评分没有覆盖
producer 的 priority 缺陷。两个 peer 也是同模型、无持久状态的 fresh call，因此不能把
结果解释成“某个 peer 更适合某种角色”。

本设计不修改 Goal，也不把这些失败改写成正结果。它规定下一次真实学习实验必须先
满足什么，才有资格回答：situated recipient judgment 是否能形成 producer role evidence，
并改变后续责任分派。

## 四个不可跳过的识别条件

### 1. Root 与材料资格

实验必须绑定两个结构不同的 root，并在执行前封存 source、generator、scorer、ledger、
hidden-test、候选 workspace、可见性和写权限的 digest。改 seed、改名或从同一结构复制
字段都不算第二个 root。

当前状态如下：

| 路径 | 当前结论 | 下一步 |
|---|---|---|
| `PIPE3_stream_processing` | 主候选；已有责任/ledger/runner 工程资格，但尚未完成独立 live history 与 baseline parity | 先完成 producer correctness 覆盖与 live material receipt |
| `DIST1_queue_race` | 诊断材料；原始任务文本存在泄露/修复痕迹，不进入 confirmation root | 只保留作工程反例，不把它当独立科学 root |
| `PIPE2_data_pipeline` | 条件候选；seed 1/4/6/9 的 generator CSV 形状无效 | 只有 authority 修复、全 root replay 和独立 history 均通过后才能申请新版本 |
| `MULTI3_polyglot` | `CONDITIONAL-LOW` fallback；native tests 没有真实 producer→recipient adoption | 不投入主线 runner，除非补齐 artifact binding 与 scorer contract |

任何 root 缺少真实 recipient action、producer-owned contract score 或 later-use outcome，
都只能输出 `UNKNOWN`，不能用人工修复或删除病例提升通过率。

### 2. 责任标签资格

每个 source episode 必须独立记录：

```text
delivery/version/digest
→ recipient action + changed paths
→ producer contract score Q_p
→ recipient judgment J
→ later/terminal outcome Y
→ ownership gate G ∈ {producer, recipient, mixed, unknown}
```

只有 `G=producer` 且 `Q_p, J, A, Y` 完整、可回放、版本一致时，才可发布
`RoleEvidence`。recipient 自有 integration、mixed ownership、缺字段、scorer/resource
失败和仅有 terminal outcome 都是 `UNKNOWN` 或 `PENDING_ATTRIBUTION`；它们不能惩罚
producer，也不能作为负例喂给 updater。

评分必须覆盖 producer contract 的公开模块，而不只是 consumer 的 ack/queue 行为。
consumer 行为分数与 producer correctness、sink adoption、完整 cost 分开列账；原 N02
的 `4/4 consumer` 不回写为 producer 正确。

### 3. Agent 状态资格

为检验“从他人的判断中学习角色”，每个 peer 必须从同一初始状态开始，并在 episode
之间保留可审计的本地状态。至少记录：

- `agent_id`、state/version digest 和允许读取的事件范围；
- 过去由该 peer 交付的 artifact、recipient judgment、责任 gate 和 later-use 结果；
- 下一次 generation/choice 实际读取的 state digest；
- state 更新前后 hash、容量、延迟、token/tool/GPU 成本和遗忘探针。

同一个模型的 fresh API call、prompt 中临时写入的 peer 名称或预置“专家身份”都不能
证明角色形成。若实验只研究 artifact judgment，必须在论文中明确它不是 peer-role
learning；不得把这两个问题静默合并。

### 4. 同信息 baseline parity

所有 arm 必须共享 candidate menu、task/root split、model/API/tool budget、exploration、
feedback arrival order、UNKNOWN 分母和完整成本；每个 arm 只能读取自己的合法历史。
最小主轨矩阵为：

| arm | 可读反馈 | 更新 | 替代解释 |
|---|---|---|---|
| `uniform` | candidate menu | fixed uniform | 随机/探索下界 |
| `no_update` | 初始状态与当前任务 | 无 | 执行本身已足够 |
| `raw_acceptance` | 合法 accept/reject | 只更新 raw channel | 责任过滤没有增量 |
| `terminal_only` | 独立 later/terminal outcome | delayed | situated judgment 没有额外信息 |
| `contextual_trust` | 与主方法完全相同的 public context、propensity、延迟和 UNKNOWN | 自己的 contextual update | 普通同信息 bandit 已解释收益 |
| `pooled_controller` | 允许的公共历史 | pooled update | 集中控制上界 |
| `RARE` | responsibility-safe judgment/action/contract | public evidence + selected-only delayed update | 候选机制 |

`RLS`、online logistic/SGD、periodic refit 是 updater/训练比较，不重复算作 policy；
closest published adapter 必须有可复现代码或明确独立重实现合同，否则标为 `NO-GO`，
不以手写 trust score 代替。

## 预注册的小步实验顺序

1. **零调用 replay**：两 root 的 visibility、ownership、scorer coverage、UNKNOWN、
   delayed ordering、snapshot/restore 和 duplicate/late correction。
2. **单 root real material**：只测 producer→recipient→scorer 的责任标签和成本；不报告
   role-learning 效果。
3. **信息价值四格**：`no evidence/no update`、`public evidence only`、`delayed update
   only`、`public evidence + delayed update`。先验证 judgment 能否在独立 producer
   contract/later-use 上有增量信息。
4. **同信息 policy parity**：uniform/no-update/raw/terminal/contextual/pooled/RARE，
   相同 menu、seed、budget、arrival 和 live history；主指标写入冻结 card 后才运行。
5. **独立 confirmation root**：开发结果不能改 split、label、指标或停止规则。
6. 只有真实信号暴露出表示或 updater 瓶颈，才冻结一个 A800 challenger；GPU 不能替代
   benchmark 或责任证据。

## 必须报告的结果

- **信息价值**：judgment 对 independent `Q_p`/later-use 的预测、Brier/AUC（适用时）、
  calibration、UNKNOWN 率与 raw/terminal 对照；
- **闭环后果**：执行前 assignment 的变化、未见 root 的 quality/adoption/rework、
  complete cost 和 quality--cost utility；
- **实时性**：publish/read/update p50/p95、state bytes、token/tool/GPU/人工成本；
- **时效性**：预注册 drift 后在窗口 `W` 内的 propensity/quality 恢复；
- **稳定性**：旧 root holdout 峰值/平均遗忘、恢复窗口、乱序/延迟/correction replay；
- **审计性**：每条事件的 raw JSONL、source/model/data/hardware/seed/hash、错误和
  `UNKNOWN` 原因。

若四格或 parity 显示 judgment 没有增量，论文应报告 null/trade-off，并撤回相应角色
学习主张；这属于科学结论，不是降低 Goal 标准。

## 放行门

在上述四个识别条件都满足前：

- 不启动 N03 正式采样，不填写论文 headline result，不选择最终 backbone/updater；
- 不把 N02 的 consumer score、离线 fixture 或单次成功链写成方法收益；
- 不提交 A800 作业；
- 保留所有失败、超时、UNKNOWN 和未启动 episode。

本设计与 active 文档的关系是“执行前解释和检查清单”；如需改变 root、label、主指标
或创新边界，必须先由用户确认并新建 ADR/active version，不能在实验失败后静默放宽。
