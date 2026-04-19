# EMNLP 2024 / 2025 高质量 Long Paper 参考库

> 维护者：科学家（reading lead）。本目录是 EMNLP long paper 投稿的**外部参考资料库**。
> 创建日期：2026-04-19。新增/重命名 PDF 必须同步更新本文件 + `PROJECT_STRUCTURE.md §2`。

---

## 0. 目的

为本仓库 (`Emergent Delegation Organization` / `TCPB Prototype`) 的 EMNLP 投稿提供：

- 写作风格与论证结构参考（Best / Outstanding 是当年风格基线）
- Method 章节的可执行性 / 形式化深度参考（尤其 Tier 1 + 算法类 Tier 2）
- Limitations / Responsible NLP 段落写法参考（EMNLP 2024+ 强制项）
- Related Work 引用候选（多 agent / routing / reasoning / evaluation 方向）

---

## 1. 概览

| Tier | 数量 | 来源 |
|---|---:|---|
| Tier 1 — Best Paper | 6 | EMNLP 2024 (5) + EMNLP 2025 (1) |
| Tier 2 — Outstanding | 27 | EMNLP 2024 (20) + EMNLP 2025 (7) |
| Tier 3 — 其他奖项 | 9 | EMNLP 2024 (2) + EMNLP 2025 (7) |
| **合计** | **42** | 全部已通过 `%PDF-` magic bytes 校验 |

下载源：所有 PDF 来自 `https://aclanthology.org/{year}.emnlp-main.{ID}.pdf`。校验方式：本地文件存在 + magic bytes = `%PDF-`。
官方 awards 页面：[EMNLP 2024](https://2024.emnlp.org/program/best_papers/) · [EMNLP 2025](https://2025.emnlp.org/program/awards/)。

---

## 2. Tier 1 — Best Paper（6 篇）

| # | Anthology ID | 标题 | 路径 |
|---:|---|---|---|
| 01 | `2025.emnlp-main.1268` | Infini-gram mini: Exact n-gram Search at the Internet Scale with FM-Index | `2025/best/01_infinigram_mini_fm_index.pdf` |
| 02 | `2024.emnlp-main.573` | An image speaks a thousand words, but can everyone listen? On image transcreation for cultural relevance | `2024/best/02_image_speaks_thousand_words_transcreation.pdf` |
| 03 | `2024.emnlp-main.570` | Towards Robust Speech Representation Learning for Thousands of Languages | `2024/best/03_robust_speech_thousand_languages.pdf` |
| 04 | `2024.emnlp-main.142` | Backward Lens: Projecting Language Model Gradients into the Vocabulary Space | `2024/best/04_backward_lens_lm_gradients.pdf` |
| 05 | `2024.emnlp-main.300` | Pretraining Data Detection for Large Language Models: A Divergence-based Calibration Method | `2024/best/05_pretraining_data_detection_divergence.pdf` |
| 06 | `2024.emnlp-main.721` | CoGen: Learning from Feedback with Coupled Comprehension and Generation | `2024/best/06_cogen_coupled_comprehension_generation.pdf` |

---

## 3. Tier 2 — Outstanding Paper（27 篇）

### 3.1 EMNLP 2025 Outstanding（7 篇）

| # | Anthology ID | 标题 | 路径 |
|---:|---|---|---|
| 07 | `2025.emnlp-main.69`   | LingGym: How Far Are LLMs from Thinking Like Field Linguists? | `2025/outstanding/07_linggym_field_linguists.pdf` |
| 08 | `2025.emnlp-main.154`  | Mind the Value-Action Gap: Do LLMs Act in Alignment with Their Values? | `2025/outstanding/08_value_action_gap_llms.pdf` |
| 09 | `2025.emnlp-main.398`  | DiscoSG: Towards Discourse-Level Text Scene Graph Parsing through Iterative Graph Refinement | `2025/outstanding/09_discosg_scene_graph_parsing.pdf` |
| 10 | `2025.emnlp-main.486`  | Generative or Discriminative? Revisiting Text Classification in the Era of Transformers | `2025/outstanding/10_generative_or_discriminative.pdf` |
| 11 | `2025.emnlp-main.504`  | Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps | `2025/outstanding/11_cot_faithfulness_unlearning.pdf` |
| 12 | `2025.emnlp-main.882`  | MiCRo: Mixture Modeling and Context-aware Routing for Personalized Preference Learning | `2025/outstanding/12_micro_personalized_preference.pdf` |
| 13 | `2025.emnlp-main.1271` | Causal Interventions Reveal Shared Structure Across English Filler-Gap Constructions | `2025/outstanding/13_causal_filler_gap_constructions.pdf` |

### 3.2 EMNLP 2024 Outstanding（20 篇）

| # | Anthology ID | 标题 | 路径 |
|---:|---|---|---|
| 14 | `2024.emnlp-main.649`  | Fishing for Magikarp: Automatically Detecting Under-trained Tokens in Large Language Models | `2024/outstanding/14_fishing_for_magikarp_undertrained_tokens.pdf` |
| 15 | `2024.emnlp-main.406`  | Learning to Retrieve Iteratively for In-Context Learning | `2024/outstanding/15_iterative_retrieval_in_context_learning.pdf` |
| 16 | `2024.emnlp-main.953`  | Measuring Psychological Depth in Language Models | `2024/outstanding/16_psychological_depth_lms.pdf` |
| 17 | `2024.emnlp-main.1216` | Do LLMs Plan Like Human Writers? Comparing Journalist Coverage of Press Releases with LLMs | `2024/outstanding/17_llms_plan_like_human_writers.pdf` |
| 18 | `2024.emnlp-main.311`  | Words Worth a Thousand Pictures: Measuring and Understanding Perceptual Variability in Text-to-Image Generation | `2024/outstanding/18_words_thousand_pictures_perceptual.pdf` |
| 19 | `2024.emnlp-main.911`  | Finding Blind Spots in Evaluator LLMs with Interpretable Checklists | `2024/outstanding/19_blind_spots_evaluator_llms_checklists.pdf` |
| 20 | `2024.emnlp-main.195`  | GoldCoin: Grounding Large Language Models in Privacy Laws via Contextual Integrity Theory | `2024/outstanding/20_goldcoin_privacy_laws_contextual_integrity.pdf` |
| 21 | `2024.emnlp-main.172`  | Verification and Refinement of Natural Language Explanations through LLM-Symbolic Theorem Proving | `2024/outstanding/21_verification_refinement_explanations_theorem_proving.pdf` |
| 22 | `2024.emnlp-main.983`  | The Zeno's Paradox of 'Low-Resource' Languages | `2024/outstanding/22_zenos_paradox_low_resource.pdf` |
| 23 | `2024.emnlp-main.236`  | When Is Multilinguality a Curse? Language Modeling for 250 High- and Low-Resource Languages | `2024/outstanding/23_when_multilinguality_curse_250_languages.pdf` |
| 24 | `2024.emnlp-main.53`   | Language Models Learn Rare Phenomena from Less Rare Phenomena: The Case of the Missing AANNs | `2024/outstanding/24_rare_phenomena_missing_aanns.pdf` |
| 25 | `2024.emnlp-main.1051` | Fool Me Once? Contrasting Textual and Visual Explanations in a Clinical Decision-Support Setting | `2024/outstanding/25_fool_me_once_clinical_explanations.pdf` |
| 26 | `2024.emnlp-main.1101` | Threshold-driven Pruning with Segmented Maximum Term Weights for Approximate Cluster-based Sparse Retrieval | `2024/outstanding/26_threshold_pruning_sparse_retrieval.pdf` |
| 27 | `2024.emnlp-main.20`   | Learning Planning-based Reasoning by Trajectories Collection and Process Reward Synthesizing | `2024/outstanding/27_planning_based_reasoning_trajectories.pdf` |
| 28 | `2024.emnlp-main.978`  | Are Large Language Models Capable of Generating Human-Level Narratives? | `2024/outstanding/28_human_level_narratives_llms.pdf` |
| 29 | `2024.emnlp-main.304`  | Formality is Favored: Unraveling the Learning Preferences of Large Language Models on Data with Conflicting Knowledge | `2024/outstanding/29_formality_favored_conflicting_knowledge.pdf` |
| 30 | `2024.emnlp-main.724`  | OATH-Frames: Characterizing Online Attitudes Towards Homelessness with LLM Assistants | `2024/outstanding/30_oath_frames_homelessness_attitudes.pdf` |
| 31 | `2024.emnlp-main.702`  | SUPER: Evaluating Agents on Setting Up and Executing Tasks from Research Repositories | `2024/outstanding/31_super_evaluating_research_repos_agents.pdf` |
| 32 | `2024.emnlp-main.914`  | Towards Cross-Cultural Machine Translation with Retrieval-Augmented Generation from Multilingual Knowledge Graphs | `2024/outstanding/32_cross_cultural_mt_rag_kg.pdf` |
| 33 | `2024.emnlp-main.1114` | Which questions should I answer? Salience Prediction of Inquisitive Questions | `2024/outstanding/33_salience_prediction_inquisitive_questions.pdf` |

---

## 4. Tier 3 — 其他奖项 / SAC Highlights（9 篇明确点名）

### 4.1 EMNLP 2025 其他奖项（7 篇）

| # | Anthology ID | 奖项 | 标题 | 路径 |
|---:|---|---|---|---|
| 34 | `2025.emnlp-main.1180` | Best Special Theme | InterIDEAS: Philosophical Intertextuality via LLMs | `2025/others/34_interideas_philosophical_intertextuality.pdf` |
| 35 | `2025.emnlp-main.90`   | Best Resource | Autoformalization in the Wild: Assessing LLMs on Real-World Mathematical Definitions | `2025/others/35_autoformalization_in_the_wild.pdf` |
| 36 | `2025.emnlp-main.1653` | Social Impact | AccessEval: Benchmarking Disability Bias in Large Language Models | `2025/others/36_accesseval_disability_bias.pdf` |
| 37 | `2025.emnlp-main.1410` | People's Choice | Randomly Removing 50% of Dimensions in Text Embeddings has Minimal Impact on Retrieval and Classification Tasks | `2025/others/37_randomly_removing_50_dimensions.pdf` |
| 40 | `2025.emnlp-main.37`   | SAC Highlight | PAFT: Prompt-Agnostic Fine-Tuning | `2025/others/40_paft_prompt_agnostic_finetuning.pdf` |
| 41 | `2025.emnlp-main.108`  | SAC Highlight | Constructions are Revealed in Word Distributions | `2025/others/41_constructions_revealed_word_distributions.pdf` |
| 42 | `2025.emnlp-main.148`  | SAC Highlight | Whisper-UT: A Unified Translation Framework for Speech and Text | `2025/others/42_whisper_ut_unified_translation.pdf` |

### 4.2 EMNLP 2024 其他奖项（2 篇）

| # | Anthology ID | 奖项 | 标题 | 路径 |
|---:|---|---|---|---|
| 38 | `2024.emnlp-main.277`  | Resource Paper | KidLM: Advancing Language Models for Children – Early Insights and Future Directions | `2024/others/38_kidlm_language_models_for_children.pdf` |
| 39 | `2024.emnlp-main.1074` | Best Special Theme | DEM: Distribution Edited Model for Training with Mixed Data Distributions | `2024/others/39_dem_distribution_edited_model.pdf` |

---

## 5. 与本仓库 EDO/TCPB 研究最相关的论文（重点优先读）

下面 5 篇按"对当前论文写作 / 方法定位 / Limitations 段落最具直接借鉴价值"排序，建议优先深读：

| 优先级 | 路径 | 借鉴点 |
|---|---|---|
| ⭐⭐⭐ | `2025/outstanding/12_micro_personalized_preference.pdf` | `MiCRo` 是显式 mixture + **context-aware routing**，与 TCPB 的"局部 belief 路由"机制最近邻；可学其 routing 公式形式化与对照 baseline 结构 |
| ⭐⭐⭐ | `2024/outstanding/31_super_evaluating_research_repos_agents.pdf` | `SUPER` 评估 LLM agent 完成任务能力，包含子问题/端到端两层粒度——可作为 EDO 后续 benchmark 设计参考（用户提到"agentic workflow"） |
| ⭐⭐ | `2024/outstanding/19_blind_spots_evaluator_llms_checklists.pdf` | reviewer LLM 不可靠的实证证据，呼应 idea.md 主张的"self-reflection hubris"；可作为 §2.2 Related Work 引用 |
| ⭐⭐ | `2024/outstanding/27_planning_based_reasoning_trajectories.pdf` | 用 process reward + trajectory collection 学规划——对 Stage-2 EDO 的 split 子任务 reward 设计有借鉴 |
| ⭐⭐ | `2024/best/05_pretraining_data_detection_divergence.pdf` | EMNLP 2024 Best Paper 的"形式化清晰 + Limitations 严谨"风格典范，建议作为最终 paper polish 的对照范本 |

---

## 6. 已完成校验

- 文件总数：**42 / 42**
- 总大小：**140.5 MB**
- magic bytes 校验：全部通过 (`%PDF-` 开头)
- 校验命令：`Get-ChildItem -Recurse references/emnlp -Filter *.pdf | ForEach-Object { read first 5 bytes, expect '%PDF-' }`
- 日期：2026-04-19

---

## 7. 后续可选下载（用户拍板后再补）

用户原列表说"约 25 篇 Tier 3 + 全部 SAC Highlights"，但只显式点名 9 篇。下面是与本仓库主题最相关的潜在补下候选（**等用户确认再下**）：

### 7.1 强相关 SAC Highlights（多 agent / 协作 / 评估）

- `2025.emnlp-main.???` `ReSo: A Reward-driven Self-organizing LLM-based Multi-Agent System for Reasoning Tasks` —— **直接对标 EDO 的"组织自形成"主张**
- `2025.emnlp-main.???` `Collab-Overcooked: Benchmarking and Evaluating Large Language Models as Collaborative Agents` —— 协作型 benchmark
- `2025.emnlp-main.???` `Mind the Blind Spots: A Focus-Level Evaluation Framework for LLM Reviews` —— 与 reviewer-loop 评估直接相关
- `2025.emnlp-main.???` `AMACE: Automatic Multi-Agent Chart Evolution for Iteratively Tailored Chart Generation` —— 多 agent 演进

### 7.2 EMNLP 2024 Social Impact / Resource（次相关）

- 用户列表未显式点名，可按需补；建议至少补 `User-Centric Multi-Intent Benchmark for Evaluating LLMs`（与 idea 评测体系相关）

如需补下，告知"补 7.1" 或 "补 7.1+7.2"，我会用相同方式查 ID + 校验下载。
