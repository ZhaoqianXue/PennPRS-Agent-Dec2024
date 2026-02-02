# LLM 文献挖掘技术栈优化路线图 (2026)

> **创建日期**: 2026年1月15日
> **背景**: 基于对当前 `src/modules/literature` 实现与 2026 年初 SOTA Agentic 架构的对比评估。本文件列出了将系统升级至最先进水平的 5 条关键技术建议。

---

## 🚀 待办事项清单 (To-Do List)

### 1. 升级为 "LangExtract" 可信循证引擎 (Trustworthy Evidence Engine)
**现状**: 当前提取器基于简单的全文本投喂，缺乏证据展示能力，且在处理长文档结构（如区分 Discovery/Replication 队列）时容易混淆。
**核心目标**: 引入 Google **LangExtract** 技术栈，最大化利用其**结构化溯源**与**交互式可视化**能力。
**优化任务**:
- [x] **Engine Core**: 部署 `src/lib/langextract`，利用其 **Smart Chunking** 策略处理超长论文（已实现基础分块与 Evidence 定位）。
- [x] **Interactive Validity**: 实现 **Evidence Visualization**，为每个提取出的 h²/PRS 数值生成高亮原文的 HTML 验证片段，实现“点击即达”的核查体验。
- [ ] **Context-Aware Logic**: 利用 LangExtract 的层级感知能力，精确区分 **Discovery** 与 **Replication** 阶段的样本量和结果，避免张冠李戴。
- [ ] **Dynamic Few-Shot**: 构建基于 Schema 的动态样本库，针对提取失败的案例自动注入修正样本。
- [ ] **预期收益**: 将 Extraction 从“黑盒处理”升级为“透明可信系统”，人工复核效率提升 5-10 倍。

### 2. 从 "Prompt Engineering" 转向 "DSPy 编程性优化"
**现状**: 依赖 `prompts.py` 中大量手写的静态 Prompt、Few-Shot 示例和复杂的负面约束。
**问题**: 静态 Prompt 脆弱，难以维护，且无法随模型升级自动优化。
**优化任务**:
- [ ] 引入 **DSPy (Declarative Self-Improving Language Programs)** 框架。
- [ ] 定义提取任务的 `Signatures` (输入: 全文 -> 输出: 结构化数据)，替代手写 Prompt。
- [ ] 使用 `MIPROv2` 或 `BootstrapFewShot` 优化器，利用 Ground Truth 数据自动编译和优化 Prompt。
- [ ] **预期收益**: 提取准确率提升 20-30%，增强系统鲁棒性。

### 3. 从 "Text-Only" 转向 "Multimodal Table Extraction" (视觉多模态例如Docling (IBM)，仅在后续引入非OA文献时再添加）
**现状**: 仅依赖 PDF 转换后的 `full_text` 文本。
**问题**: 30%-50% 的关键数值（h², rg 矩阵）存在于表格图片中，PDF 转文本常破坏表格结构。
**优化任务**:
- [ ] 修改爬虫模块，支持截取论文中的 **Figures** 和 **Tables**。
- [ ] 增加 `ChartExtractor` Agent，集成 **VLM (Vision-Language Models)** (如 GPT-5-Vision)。
- [ ] 直接从表格图像中读取数值，而非依赖 OCR 文本。
- [ ] **预期收益**: 大幅提升表格密集型数据（如 GWAS 汇总表）的提取成功率。

### 4. 从 "Linear DAG" 转向 "Reflexion Loops" (反思循环)
**现状**: `pipeline.py` 使用单向线性的 LangGraph (`Search -> Classify -> Extract -> Validate`)。
**问题**: 验证失败的数据直接被丢弃或标记为人工审核，浪费了 LLM 的自我纠错能力。
**优化任务**:
- [ ] 改造 LangGraph，构建 **Reflexion (反思) 闭环**。
- [ ] 实现 **Self-Correction**: 当 `Validator` 报错时，将错误反馈回 `Extractor` 要求重试。
- [ ] 实现 **Active Lookups**: 允许 Agent 在数据缺失时自主搜索引用文献。
- [ ] **预期收益**: 自动化程度大幅提升，减少人工审核队列长度。

---

## ✅ 已完成 / 归档 (Completed / Archived)

### [已完成] 采用 Native Structured Outputs (严格模式)
**优化任务**:
- [x] 升级 OpenAI 客户端调用方式。
- [x] 在 `llm_config.py` 中启用 API 原生的 **Strict Structured Outputs (`"strict": true`)**。
- [x] 直接传入 Pydantic 模型作为 schema 定义。
- [x] **预期收益**: 从底层根除 JSON 格式错误和 Schema 违规，降低重试成本。

### [已完成] 核心提取器升级为 "GPT-5-Mini" (原计划: Reasoning Models)
**说明**: 原计划采用推理模型 (Reasoning Models) 处理复杂提取任务，但出于成本和速度平衡考虑，暂时转向能力更强但性价比更高的 **GPT-5-Mini**。
**优化任务**:
- [x] 在 `llm_config.py` 中支持推理模型配置。
- [x] 将核心 `LITERATURE_EXTRACTOR` 模型配置从 `gpt-5-nano` 升级为 **`gpt-5.2`**。
- [x] **预期收益**: 相比 Nano 显著提升复杂语境理解能力，减少幻觉，同时保持较低推理成本。

