# 有界判断执行器复用记录

2026-10-08。目的：执行已封存的四格诊断，不新建通用实验框架。

已有 `scripts/peerrolebench_real_closed_loop.py` 的 `call_api/log/save` 提供真实
“内部”配置读取、curl 直接连接、stdin 传认证、SSE 原始响应、逐请求成本及零重试。
本轮直接复用，保持历史 transport 不变。准备材料来自
`peerrolebench_scoped_judgment_diagnostic.py`，组件标签来自
`peerrolebench_scoped_judgment_gold_preflight.py`，两者均不重新生成。

所缺功能只有：冻结输入与 gold 校验、最多四次的一次性调用边界、精确双对象响应
结构核验，以及每次结果后的独立理由复核。以一个薄执行器实现，不引入依赖、不
触碰历史采样器或责任/在线 reward gate。软件 fixture 只用于拒绝边界检查；真实
结论只从实际 transport 原始响应获取。

真实case1因datetime语义判断错误停止后，复用 `peerrolebench_sandbox.SandboxedWorker` 与 `peerrolebench_pipe3_material_adapter.digest_files` 做单一公开 serialize_event 轨迹。现有 private producer scorer 包含私有检查，不能直接暴露给 actor；新 driver 仅返回执行文本、timestamp及版本绑定，单独卡最多2次本地RPC，不新增API。
