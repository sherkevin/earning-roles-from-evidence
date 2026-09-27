# 0032：producer quality 必须独立于 recipient outcome

日期：2026-09-27。  
状态：Accepted as a causal and scoring boundary; 不改变 Goal v1.0。

## 背景

当前 runner 的 `TerminalOutcome` 建立在 recipient 的 `ConsumerAction` 之后，测量的是
recipient 是否把交付接入成功。它不能同时充当 producer 交付质量标签：recipient 自己负责的
`consumer.py`、返工、重做和返工成本会污染 producer 的归因。原生 TeamBench `grade.sh`
也会检查整个 workspace，不能直接作为 producer role evidence。

最近的独立 consumer scorer 回放还发现，旧的 parent-side 行为检查给一个保存的 episode
判为 `4/4 PASS`，独立 worker 在相同 sealed source 上发现 `payload_and_ack` 失败，得到
`FAIL, 0.75`。这说明 scorer 隔离不仅是工程问题，检查语义也必须分开记录。

## 决定

1. 定义两个不同的观测：
   - `Q_p(D_i)`：只对不可变的 producer delivery `D_i` 和 producer-owned paths 评分；
   - `Q_r(F_i, C_i, D_i)`：对 recipient 的最终集成产物、consumer 行为和 action 成本评分。
2. `Q_p` 使用独立 operator-only scorer，输入只含 task/seed、producer artifact digest 和
   公开 schema；hidden checks 留在私有 worker。其 `PASS/FAIL/UNKNOWN`、check inventory、
   response digest、退出/超时/权限信息单独落盘。
3. `Q_p` 暂不写入现有 `TerminalOutcome`，也不直接改 role controller。先增加独立的
   producer-score artifact/事件设计，并在 replay causal order 明确后再允许它作为学习信号。
4. situated recipient judgment 仍是论文的核心证据；`Q_p` 用于评估判断校准、归因和可选的
   oracle-label 对照，不能静默替代 situated judgment。
5. 在 buggy/correct/near-miss/transport mutation qualification matrix 通过前，不把该
   scorer 接入真实 role update，不启动 A800。

## 后果

producer 缺陷、recipient 自有工作、最终质量和返工成本可以分别报告；旧 episode 的
`consumer_score` 不会被改写。代价是需要一个新的 producer-score schema、回放构造器和一轮
零 LLM scorer qualification。Goal 没有降级，`goal_change_requested=false`。
