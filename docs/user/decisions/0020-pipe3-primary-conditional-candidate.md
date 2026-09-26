# 0020：将 PIPE3 作为第二任务 root 的主候选（条件性）

状态：Accepted for the next qualification gate；不是最终 benchmark 冻结。

日期：2026-09-26。

## 背景

DIST1 已完成有限真实链，但只覆盖 queue/priority→consumer 集成。CROSS3 的代码交付切面被审查为不合格，因为原 consumer/publisher 已经完成；还需要第二个结构不同、且确实存在下游独立工作的任务 root。

TeamBench 静态扫描保留了 PIPE3、MULTI3、CROSS5 三个候选。随后对 PIPE3 seed 0 做父进程控制样例。v1 发现 Python 的宽松 `fromisoformat()` 会让 processor 接受 producer 的错误空格时间戳；v2 把 spec 已要求的严格 `T` 分隔边界放入父进程 contract probe 后，producer 质量、recipient 自有工作和完整 adoption 的四格控制矩阵完全可分。

## 决定

将 `PIPE3_stream_processing` 作为第二 root 的主候选，进入下一层任务契约、隔离和真实运行资格；保留 MULTI3 作为失败时的备选。CROSS5 暂不采用，因为 native grader 不执行 Java consumer 行为。DIST3 与 NEG3 关闭，INFRA2 只保留 diagnostic-only。

## 责任切分

- producer：只负责 `producer.py` 的 JSONL 输出；父进程直接检查 ISO timestamp 和字段格式。
- recipient：只负责 `processor.py` 的变换与写出；用独立 canonical 输入测自有工作。
- read-only support：`models.py`、`sink.py` 和测试契约；不得把 recipient 的 processor 修复归责给 producer。
- adoption：仅当符合 producer contract 的输出经过 processor 后被 sink 读取，才记完整 adoption。

## 后果与边界

这个决定提供一个可审查的 benchmark 候选和评分边界，但不锁定最终 benchmark、baseline、backbone 或 updater。下一步不调用 LLM、不创建 GPU 队列，只做路径/账本/成本资格。若真实任务契约或隔离无法通过，应将本 ADR 标记为 superseded 并转向 MULTI3，而不是继续修补 PIPE3。
