# 两名同构 actor 的 source→target 筛查（候选诊断卡）

日期：2026-10-08。状态：`CANDIDATE / NOT_EXECUTED`。仅评估下一张有界真实诊断是否值得冻结；不修改六份 ACTIVE 文档、Goal 或既有停止结果。

## 要改变的决定

先问 PIPE3 是否产生**自然的、可迁移的候选差异**，以及他人的事前 J 是否有机会帮助未来负责人选人。若两名初始同构 actor 在新 source 和同一新 target 上没有可区分的交付/质量，继续给固定 C2 格增加判断调用没有价值；应重新审查任务依赖和 root，而非训练选择头。若有差异，再设计第三方 future assignment 与同信息基线。此筛查不能证明 J 有因果增量、角色学习或任务泛化。

## 最小真实设计与预算

**建议值得做一次，最多 8 次 LLM 请求，分段停止，不补跑。** 用已有 `live_producer_stage` 对两名无预设专家身份、同模型/配置/初始经验的 actor 各生成一次 source（2 次 producer）；对两份真实交付分别让同一冻结 recipient 在行动前给 J（2 次 judgment），随后分别完成该 source 的实际 recipient action（2 次 action）与独立 Qp/Y 检查。再让两名 actor 各处理**事前冻结的同一新 target**（2 次 producer），由 parent-only 独立 producer-contract 检查评价 target 交付。先做源生成与质量/来源核查；若源 UNKNOWN、公开合同/评分资格无效或两份交付没有可辨差异，即停，不花后续调用。合法的 Qp FAIL 是待测结果，不能作为停止或删样条件。目标 prompt/样本在看 source 之前冻结，不因源结果换 seed 或挑题。

source 两份 J 必须在各自 action 前封存；公开只读 probe 若使用，也必须在 J 前、同规则提供给两人并单列成本。A/Y 不进入同次 J。source 完成后可记录 typed noisy observation；只有通过独立责任门的部分才可能成为 producer evidence，J 本身绝不进入 producer credit。目标两份 producer 输出用于**parent-only counterfactual screening**：真实未来 selector 不可能同时选择并观察两名 actor 的 target 结果，故不能把两份 Qp 当 selected-only 反馈、离线训练样本或真实 route utility。target 若未执行 recipient use/adoption，Qp 也不能代替团队 Y。

## 执行前冻结与读数

冻结 actor/version、同构模型和初始个人经验空快照，source 与 target 的公开合同、root/seed、recipient 身份/策略、prompt 与工具可见性、调用/token/超时上限、随机调用顺序及响应失败规则；封存每次决策前的候选菜单、读切、公开历史和成本账。`live_producer_stage` 的个人历史仅存其既往公开 task input/actor response，不能把它说成 actor 自我训练或持久能力改变。两 actor 的 source/target 独立历史不得交叉污染；target 生成前不让 actor 读取对方 J、parent Qp/Y 或 target 对照结果。target 接收方和 CPU scorer 使用同一版本；每次尝试、UNKNOWN、返工和成本照实记录。原累计预算超额持续列账；本卡不是预算重置或执行授权。

主要屏幕读数为：两份 source 交付是否有真实差异、各自 Qp/J/A/Y 的对象与一致性，以及同一 target 上两名 actor 的独立 Qp/成本是否存在可区分次序。报告原始逐例而非胜率；两名 actor、单 root、单 target 无法估计总体增量、置信区间或选择收益。若源 J 与客观检查相反，先归因公开合同/代码行为事实错误（上一轮 `default=str` 即如此），不可将其当负的 producer reward。

**继续门：** 只有源链合法、target 差异可测且 J 可能提供超出固定公开事实的判别内容，才考虑另卡：第三方在 target 执行前基于合法 source snapshot 选择一名 actor，保留正概率探索，与取得相同公开字段的 contextual/trace-only 控制比较独立未来质量与完整成本；确认仍需不同 root、独立 streams 和实际后续执行。若只是同一 C2 时间戳好坏，可由公开 trace 确定，则不继续追加同根 J；若两 actor target 等价，先审查 benchmark 的真实依赖与任务变化。

## 信息论与时间边界

对固定公开 C2 条款和已观察的时间戳，标签是公开输入的确定函数，trace-only 已无该**窄标签**的 Bayes 风险空间；这不涵盖完整合同或未来效用。若固定无历史 judge 仅由同一完整公开输入 `Z` 产生 J，且随机性在给定 Z 后与未来 Y 独立，`I(Y;J|Z)=0`；有限样本/算力选择器仍可能受益于 J 的压缩。额外的 `W` 只能是 J **之前**实际合法可见的交付检查、公开 probe 或真实既往经验；不得虚构持久 peer 状态，也不得把同次 action/use/repair 的结果倒灌给事前 J。改成事后 J 属重大方法变更，不属于本诊断。

依据：[ACTIVE 方法 v1.3](../versions/method/method_v1.3_20261007.md) §2.1/§5.1、[故事线验收](../versions/evaluation/storyline/storyline_v1.3_20260928_eval.md)、[方法验收](../versions/evaluation/method/method_v1.4_20261007_eval.md)、[benchmark/baseline 验收](../versions/evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md)；既有失败见 `experiments/logs/n03_scoped_judgment_real_20261008_v1/` 与 `experiments/logs/n03_public_trace_feasibility_20261008_v1/`。
