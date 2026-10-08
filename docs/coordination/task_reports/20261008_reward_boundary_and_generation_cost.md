# 将错误标签更新与正式训练隔离

日期：2026-10-08。状态：`BOUNDED_SOFTWARE_CHECKS_PASSED / NO_NEW_LIVE_EXECUTION`。

本轮落实已确认的 ADR0049：**证明任务链存在，不等于证明评价可以当训练标签。**
目标是防止新方法误用旧 target-J 更新，并使新 producer 生成的费用有计量入口。
不修改 Goal、六份生效文档、benchmark 划分或训练目标；没有新增 API/GPU。

## 问题与修复

独立 Codex 审查发现，`validate_later` 只核验 ledger 和 assignment 关联，随后
仍允许 target J 或 terminal 分数更新 policy；公开 `apply_later_credit` 还能直接调用。
C1 真实执行器另有直接调用 `DelayedCreditLedger` 的旧路径，修适配器不能覆盖它。

- `peerrolebench_delayed_policy_adapter.py` 升为 v2。默认保留发布与关联验证，拒绝
  旧标签更新；只有明确 `diagnostic_only=True` 才保留历史诊断机制。
- 快照记录模式，恢复诊断状态也须显式选择；v1 快照不自动升级成正式训练状态。
- C1 公共入口须显式声明诊断用途，执行配置与更新回执记录范围。它不是预算授权，
  也不是新的合法 reward 接口。底层 baseline/terminal-only 对照保持原语义。
- 复用 `episode_cost` 的缺测处理和去重计时，增加独立 `producer_api` 费用。缺少
  token 或时间仍是 UNKNOWN；失败已消耗时间保留，不补成零。没有 producer receipt
  的旧固定产物记录仍只表示原来的阶段小计，不重算历史结果。

`cost_status=COMPLETE` 只针对回执所列阶段，不能代表完整路由成本。新回执显式给出
计量范围、producer 是否实测以及 `full_route_cost_complete=false`。生成 API 与其他
阶段确实独立的绑定、selector/update/存储/共享源等总账仍须在完整 runner 中接通。

## 验证与失败留痕

执行前封存配置与八个相关源码快照，见
[v1 日志](../../../experiments/logs/n03_reward_boundary_repair_20261008_v1/config.json)。
首轮 33 项通过、1 项失败：新回滚测试发现快照中存在内部字典引用，更新时其“之前”
对照随内部赋值变化。失败输出和源快照保留；不能把它省略后只报告通过数量。
随后改为独立复制完整嵌套快照，补充返回快照被修改也不影响 live state 的检查。
[v2 日志](../../../experiments/logs/n03_reward_boundary_repair_20261008_v2/summary.json)
记录四个定向测试文件共 **35 项通过**，期间源码摘要未变化。包含默认两个更新入口
拒绝、显式诊断幂等/恢复/回滚、C1 启动限制、成本完整/缺失/失败和原有离线链条回归。
当前 target payload 不含完整 ownership，故不能声称测过 recipient-only/mixed 的合法
奖励识别；默认拒绝仅防止未经验证的旧标签更新，不等于新训练路径已经跑通。

独立审查的剩余问题见
[回执](../../../experiments/logs/n03_reward_boundary_repair_20261008_v1/independent_review.json)。
这些是软件/接口检查，未验证模型行为、创新、收益或实时训练效果。

## 对目标的推进与下一项实际工作

| 标准 | 本轮推进 | 尚未证明 |
|---|---|---|
| 故事线与创新 | 避免把旧诊断更新写成新方法成功 | 创新优势及真实角色形成 |
| 方法论 | 落实观察与奖惩分离；显式诊断与恢复边界 | 完整合法奖励、signed 更新、速度和遗忘 |
| Benchmark / baseline | 保留对照；明确费用小计与全成本区别 | 两 root、公平独立流、实测比较 |

可复用的部分已定位：原生 Qp、独立 Y 绑定、API/scorer 成本回执以及共享源去重账。
下一步将它们与真实 producer stage 对接；冻结成本单位/权重后才能生成 route utility，
且必须执行更新后的真实未来任务。现有 `[0,1]` 标签接口无法接负效用，不能简单改名
或裁剪。当前修复没有实现这个新入口，科学投稿 gate 继续关闭。

新增调用预算与第二 root 方向等待已发出的两项答复；不重复申请，不据此降低目标。
论文科学含义本轮未改动，唯一主版 PDF 沿用已同步的 `artifacts/aamas2027/main.pdf`。
