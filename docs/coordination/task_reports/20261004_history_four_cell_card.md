# History 四格 matched replay 卡片（零调用）

日期：2026-10-04
状态：`DESIGN_ONLY`
目标：为 active method 的 history/no-history/shuffled/reset 先建立可反驳的 selector-consumption 工程门；不产生 benchmark、baseline 或科学效果结论。

## 为什么现在做这一步

上一项只证明 `delayed credit → HistoryBindingReceipt → PeerHistoryV2.append`。如果下一次选择没有读取 projection，history 写入对故事线没有因果作用；如果乱序或重置仍然能更新，实时/稳定性主张也不可审计。因此先做同一 E0/E1 轨迹下的四格 matched replay，避免把 API 失败误判为方法失败。

## 固定对象

- structural root：`PIPE3_stream_processing` 的已资格化 seed-0 source/target fixture；同一 candidate registry、candidate version、role/context、base score、RNG seed 和 selection menu；
- E0：source delivery、独立 Qp、recipient judgment/action、terminal outcome；
- E1：相同 `RoleEvidenceOffer`、assignment-before-selection、target outcome 和已提交 delayed credit；
- E2：只在 E1 arrival 之后读 public projection，再对相同候选菜单做一次选择；E2 不执行模型、不改 scorer、不读取 hidden fields；
- 每个 cell 独立 policy/history namespace，禁止跨 cell 共享可变对象。

## 四个 cell

| cell | E1 到达 E2 前的 history | 预期 E2 行为 |
|---|---|---|
| `history` | append 合法 E1 receipt；selector 读 projection | `projection_consumed=true`；输入 digest 与 empty cell 不同；选择/propensity 可因公开 history 改变 |
| `no-history` | 丢弃 projection，其他输入完全相同 | `entry_count=0`；使用同一 base/RNG；不读取任何 history 字段 |
| `shuffled-history` | 将合法 history 的 arrival/read-cut 顺序打乱后重放 | `UNKNOWN`、0 update、不得把乱序记录当成新证据；不输出科学选择结果 |
| `reset-history` | 合法 E1 后恢复到预注册空 snapshot | 必须与 `no-history` 的输入 digest/choice/propensity 相同；reset 不能保留隐式状态 |

## 预注册指标与通过条件

每个 cell 必须记录：`cell_id`、commit/component hashes、candidate registry digest、E2 read-cut、history input digest、projection digest、candidate scores/probabilities、chosen peer、propensity、selection event digest、update count、UNKNOWN reason、append/update latency 和完整 cost schema。任何缺字段的 cell 为 `UNKNOWN`。

零调用工程门只有同时满足以下条件才通过：

1. `history` 的 projection digest 被 selector input digest 引用，且 E2 selection digest 可重放；
2. `no-history` 与 `reset-history` 的全部 E2 selection fields 相等；
3. `shuffled-history` 不产生可用 label、credit 或 policy update；
4. candidate menu、RNG、base scores、模型/API/tool budget 在四格完全相同；
5. hidden artifact、terminal outcome、private scorer、其他 cell 的 state 不出现在 E2 projection；
6. 任一失败保留 raw receipt，不能把 UNKNOWN 改写成负例。

这组条件只验证信息消费和保护边界，不验证 peer suitability、质量/成本收益、实时训练速度、遗忘或 AAMAS 接收概率。若通过，下一步才是把同一四格接口挂到独立 live histories；若失败，先修复 runner/信息边界，不启动真实 API/A800。

`goal_change_requested=false`。
