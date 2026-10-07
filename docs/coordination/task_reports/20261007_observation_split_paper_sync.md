# 观察／收益分离后的正文同步与 PDF — 2026-10-07

状态：`PARTIAL`；`goal_change_requested=false`。对应 ER-G1/ER-G5。
目的：让主稿准确反映用户确认的 ADR0049，同时保持恰好八页正文、完整实验框架与
空白结果单元。此任务不产生模型实验或科学效果。

## 内容变更

[英文主稿](../../../article/aamas2027/main.tex)与
[中文阅读稿](../../paper/aamas2027/FORMAL_PAPER_ZH.md)同步区分 typed noisy observation、
producer attribution 和独立 reward。观察使用 O 掩码，s 明确为带噪声类别统计而非
producer reward。三类 J 在各自合法动作配对中比较；加入 count-only/J-masked 控制。
发布不更新、未来任务真正执行、独立质量/责任/成本和原生 ID 桥接要求均保留；桥接
仍标明待验证，没有将拟议接口写成已经完成的闭环。所有实验矩阵与结果占位保留。

## 构建与目视结果

- [v1](../../../artifacts/aamas2027/observation_split_20261007_v1/)失败：10 页总计，
  9 页实际正文，且公式 overfull。日志与 PDF 保留，不晋升。v1 当时只保存了
  main.tex 哈希，没有精确源码备份，不能声称可完整复现；v2 有完整源码快照。
  后续构建必须在启动前复制实际输入，不能只记录哈希。
- v2 精炼重复动机、候选实现和接口解释，没有缩字体、改页边距、删实验矩阵或改图。
  [最新 PDF](../../../artifacts/aamas2027/observation_split_20261007_v2/main.pdf)通过：
  **9 页总计，正文恰好 8 页，References 从第 9 页开始**；引用全部解析、0 overfull，
  官方模板摘要未变。
- 主代理已查看全正文缩略图与第 8/9 页放大图：结论完整位于第 8 页，第 9 页仅引用；
  未发现正文裁切或覆盖。三张图仍在，结果表仍空。

[manifest 与完整 source 快照](../../../artifacts/aamas2027/observation_split_20261007_v2/manifest.json)
保存实际构建用图和源文件；[构建前配置与日志](../../../experiments/logs/n03_observation_paper_20261007_v2/)
可追溯版本。图形文件沿用当时工作树输入，本任务未覆盖另一路图形工作。
复现须使用该 snapshot，不能混用不同版本的主稿与图片。既有模板 ifx 警告继续记录。

PDF SHA-256：`cddc7e9b6d0c573fc0811f8ec5865de22ee3e5b9de44265a9a6dc36ee4cb192e`。

## 对 Goal 的回看

本轮完成的是语义同步和版式核验。实际 source 信号混入 recipient 集成计划的
[证据审计](20261007_judgment_support_and_observation_split.md)仍限制科学结论；
独立 reward、真实后续执行、两个合格 root、同信息强基线与实时/遗忘效果仍待完成。
论文没有新增效果数值，三份科学审核与科学投稿 gate 均未通过。
