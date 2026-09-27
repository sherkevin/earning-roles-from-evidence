# 0029：真实 runner 在 role update 前必须通过 parent replay gate

日期：2026-09-27。
状态：Accepted as an integration contract; 不改变 Goal v1.0。

## 背景

独立 replay validator 已经能验证封存的 ledger，但如果真实 runner 仍直接根据 append
成功的内存对象更新 controller，验证器就可能被绕过。生成阶段允许临时不完整链，
而学习更新和 episode summary 需要不同的完整性门。

## 决定

`scripts/peerrolebench_real_closed_loop.py` 采用两层调用：

- `load_ledger()` 对已有序列化 ledger 使用 `allow_incomplete=True` 的 parent replay，
  因此恢复中的 episode 只能得到可审计的 `UNKNOWN`，非法 hash、字段、顺序或引用立即
  停止；
- `replay_gate()` 在写入 role evidence 后、controller update 前使用严格 replay，且在
  episode summary 前再次 replay。失败先写 `ledger_replay_gate` raw 事件，再抛错，不把
  缺失链当作负标签或成功。

## 理由与边界

这把训练信号的消费点与账本完整性绑定，同时保留 live episode 的中间态。它只保证
parent-side 事件链没有被 runner 绕过，不能证明 candidate 隔离、hidden scorer 正确、
producer contract quality 或 online update 有效；历史 N02 输出不重跑、不改写。

## 后果

任何未来 runner 若改变事件类型、retry/exception 语义或更新时机，都必须更新协议、
validator、测试和 task report；未经 gate 的数据不能进入学习器。下一步仍是实际
producer/recipient/scorer/IPC 资格，不是立即提交 A800 作业。
