# Research 文档分层

- `canonical/`：六类研究文档的唯一生效版本登记。
- `versions/`：按类别存放 active、superseded、archived 版本正文；当前 active 由 `canonical/active_versions.json` 唯一指向。
- 顶层 dated `.md`：研究报告、候选设计、审查和证据记录；它们不能替代 active 文档。
- 旧的未带日期方法 spec 也只是历史候选；当前方法只认 canonical 登记。
- `docs/archive/`：字节保真的历史来源。

遇到故事、方法、benchmark 或评价标准的冲突，先看 `canonical/README.md` 和 Goal，再看 task report 与实验日志。不要从旧的主线稿、方法 spec 或候选 freeze 文件推断当前结论。
