# Selected-only RLS 校正实验记录（2026-09-24）

该实验只用于检验事件协议和在线参数更新方向，不是论文最终 benchmark。环境随机生成 regime、菜单排列和 1–8 步反馈延迟；learner 只收到已选候选的反馈。隐藏 truth/未选 label 只存在于评估日志，未进入更新。

| 方法 | mean expected reward | 95% normal CI | 相对 static 的 paired delta |
|---|---:|---:|---:|
| static | 0.51405 | [0.47743, 0.55067] | — |
| online_rls | 0.52115 | [0.48384, 0.55846] | 0.00711 [0.00392, 0.01029] |
| label_shuffle | 0.51350 | [0.47686, 0.55013] | -0.00055 [-0.00241, 0.00131] |
| no_feedback | 0.51405 | [0.47743, 0.55067] | 0.00000 [0.00000, 0.00000] |

OnlineRLS 相对 uniform static 的 paired 提升为 +0.00711，12 个 seed 的近似 95% 区间为 [0.00392, 0.01029]；label-shuffle 为 -0.00055，区间 [-0.00241, 0.00131]。这说明 selected-only 反馈在这个构造环境中有可见但很小的信号，且打乱标签后信号消失。

## 不能从这次实验推出的结论

- static 是 uniform policy，不是已经训练好的 Laya/AnyJev 静态 scorer，因此不能声称击败现有 JEV。
- 未包含 Beta、周期性 full-refit、contextual bandit 等全部强基线，也没有真实 peer/tool 数据。
- 评估使用了模拟环境的隐藏 truth 计算 counterfactual reward；它没有泄漏给 learner，但仍不能替代真实终端标签。
- 还没有测 A800 上 RLS 的 p50/p95；已有 A800 记录只测 gated scorer/update 的运行时吞吐。

下一步是用资格明确的真实 selected-only replay 重放，并加入静态 scorer、Beta、周期性 refit 和相同探索率的 RLS 对照；若真实数据上优势消失，主张收缩为工程范式。
