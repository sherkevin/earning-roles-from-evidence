# Figure 1 v30 — refined embedded-font production

- 状态：候选，未晋升
- AI 底图：v29 textless base（完整 prompt 保存在 `ai_prompt_inherited_v29.md`）
- 生产层：LuaLaTeX + Arial Bold TrueType；只补可缩放文字，不重画 AI glyph
- v29 的第一次文字叠加保留在 `v29_textless_vector_base_20261007/`，本版本修正其文字坐标
- 目标：在不改变 AI 视觉构图的前提下，关闭可见文字的字体嵌入门
