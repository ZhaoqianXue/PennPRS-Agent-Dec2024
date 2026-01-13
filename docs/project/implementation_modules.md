# PennPRS Agent - 模块化实现计划

> **文档创建日期**: 2026年1月11日  
> **基于**: `docs/project/project_proposal.md`  
> **目标**: 将剩余工作拆解为独立、可并行开发的功能模块

---

## 🎯 项目现状总结

### ✅ 已完成功能

| 功能模块 | 完成状态 | 描述 |
|---------|---------|------|
| **PGS Catalog 集成** | ✅ 完成 | 已能搜索和展示 PGS Catalog 中的 PRS 模型 |
| **PennPRS 训练 API** | ✅ 完成 | 单/多祖源 PRS 模型训练功能已实现 |
| **前端 Disease 模块** | ✅ 完成 | ModelGrid, TrainingConfigForm 等组件 |
| **Open Targets 集成** | ✅ 完成 | 疾病搜索和关联功能 |
| **Protein 模块基础** | ✅ 完成 | OmicsPred 蛋白质组学 PRS 搜索 |
| **LLM 文献挖掘引擎 (核心)** | ✅ 完成 | PubMed 客户端、分类器、提取器、验证器、工作流 |

### 🚧 待开发功能

根据 `project_proposal.md`，以下核心功能尚未实现：

1. **LLM 文献自动提取系统** (核心引擎) ✅ **核心已完成**
   - ✅ **PRS 模型提取** - 从文献中发现尚未被 PGS Catalog 收录的 PRS 模型
   - ✅ **h² 估计值提取** - 从文献中提取 SNP-heritability 数据
   - ✅ **rg 相关性提取** - 从文献中提取遗传相关性数据
   - 🚧 **API Endpoints** - 待实现 REST API 接口
   - 🚧 **前端集成** - 待在 ModelGrid 等组件中显示数据来源
2. **Heritability (h²) 子模块** - 查询与展示
3. **Genetic Correlation (rg) 子模块** - 查询、展示与 BIGA 训练
4. **跨模块整合分析** - Genetic Profile 统一视图
5. **BIGA API 集成** - 自定义遗传相关性计算

---

## 📦 模块拆解方案

### 模块 1: LLM 文献挖掘引擎 (Literature Mining Engine)

#### 1.1 功能描述

构建 LLM 驱动的 PubMed 文献自动发现和信息提取系统，作为整个平台的数据生产管道。

**🎯 核心价值**: 突破 PGS Catalog 的手动审核瓶颈，实现 PRS 模型的 **双数据源架构**：
- **数据源 1**: PGS Catalog REST API（现有，已完成）
- **数据源 2**: LLM 从 PubMed 文献直接提取（新增，待开发）

通过 LLM 文献挖掘，系统可以发现**尚未被 PGS Catalog 收录的最新 PRS 模型**，并以相同的 Schema 存储，使前端 ModelGrid 可以无缝展示来自两个数据源的模型。

#### 1.2 Agentic Architecture (Supervisor + Workers)

```
      ┌─────────────────────────────────┐
      │        SUPERVISOR AGENT          │
      │  (Orchestrator - Not an LLM)     │
      ├─────────────────────────────────┤
      │ • Manages workflow state        │
      │ • Routes papers to workers      │
      │ • Aggregates results            │
      │ • Handles retries/errors        │
      └───────────────┬─────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│CLASSIFIER AGT │ │ EXTRACTOR AGTS│ │VALIDATOR AGT  │
│     (LLM)     │ │   (LLM x 3)   │ │ (Rule-based)  │
├───────────────┤ ├───────────────┤ ├───────────────┤
│ Task: Multi-  │ │┌─────────────┐│ │ Task: Schema  │
│ label classification││PRS Extractor││ │ validation +  │
│               │ │├─────────────┤│ │ deduplication │
│ Input: Abstract ││h2 Extractor ││ │               │
│               │ │├─────────────┤│ │ NOT an LLM!   │
│ Output: Labels│ ││rg Extractor ││ │(Deterministic)│
└───────────────┘ │└─────────────┘│ └───────────────┘
                  └───────────────┘
```

#### 1.3 Sub-task Breakdown

```
Module 1: Literature Mining Engine (Agentic Architecture)

├── 1.1 SUPERVISOR (Orchestrator - Not an LLM)
│   ├── PubMed Search via E-utilities API
│   ├── Workflow state management
│   ├── Routes papers to Classifier → Extractors → Validator
│   ├── Aggregates results from all agents
│   └── Handles retries and error recovery
│
├── 1.2 CLASSIFIER AGENT (LLM)
│   ├── Input: Paper abstract + title
│   ├── Task: Multi-label classification
│   │   ├── PRS_PERFORMANCE - Contains PRS model metrics
│   │   ├── HERITABILITY - Contains h² estimates
│   │   ├── GENETIC_CORRELATION - Contains rg data
│   │   └── NOT_RELEVANT
│   └── Output: Category labels + Confidence scores
│
├── 1.3 EXTRACTOR AGENTS (LLM × 3, run in parallel)
│   │
│   ├── PRS Extractor
│   │   ├── AUC, R², C-index
│   │   ├── variants count, sample size
│   │   ├── method (PRS-CS, LDpred2, C+T)
│   │   ├── ancestry, cohort
│   │   └── GWAS ID (GCST...)
│   │
│   ├── h² Extractor
│   │   ├── h² estimate, SE
│   │   ├── method (LDSC, GCTA, GREML)
│   │   ├── sample size, ancestry
│   │   └── PMID
│   │
│   └── rg Extractor
│       ├── trait1, trait2
│       ├── rg, SE, p-value
│       ├── method (LDSC, HDL, GNOVA)
│       └── PMID
│
├── 1.4 VALIDATOR AGENT (Rule-based, NOT an LLM)
│   ├── Schema validation per data type
│   ├── Range checks (0.5 ≤ AUC ≤ 1.0, 0 ≤ h² ≤ 1.0, -1 ≤ rg ≤ 1)
│   ├── De-duplication against PGS Catalog
│   └── Manual review queue for low-confidence extractions
│
└── 1.5 STORAGE LAYER
    ├── Unified database schema (PGS Catalog compatible)
    ├── Source tagging: "pgs_catalog" | "literature_mining"
    └── PMID traceability links
```

#### 1.4 File Structure

```
src/modules/literature/
├── __init__.py              ✅ 已完成 - 模块导出
├── pubmed_client.py         ✅ 已完成 - PubMed E-utilities API 客户端
├── paper_classifier.py      ✅ 已完成 - LLM 文献相关性分类器
├── information_extractor.py ✅ 已完成 - LLM 结构化信息提取 (PRS/h²/rg)
├── validation.py            ✅ 已完成 - 数据校验与质量控制
├── models.py                ✅ 已完成 - 数据模型定义 (Pydantic)
└── workflow.py              ✅ 已完成 - LangGraph 文献处理工作流

data/literature/
├── raw_papers/              ✅ 目录已创建 - 原始文献元数据
├── extracted_metrics/       ✅ 目录已创建 - 提取后的结构化数据
└── validation_queue/        ✅ 目录已创建 - 待人工复核数据

tests/
└── test_literature.py       ✅ 已完成 - 模块单元测试 (17 passed)
```

#### 1.5 API Endpoints

```python
# API Endpoints - 文献处理
POST /api/literature/search          # 按疾病搜索相关文献
POST /api/literature/classify        # 对文献进行分类
POST /api/literature/extract         # 从文献提取结构化数据
GET  /api/literature/status/{job_id} # 获取处理状态

# API Endpoints - PRS 模型 (⭐ 核心接口)
GET  /api/disease/{trait}/models     # 获取合并后的 PRS 模型列表 (PGS Catalog + 文献提取)
GET  /api/disease/{trait}/models/sources  # 按数据源分组返回模型
POST /api/literature/prs/extract     # 专门针对 PRS 模型的提取任务
```

#### 1.6 Frontend Integration

| 现有组件 | 对接方式 | 变更说明 |
|---------|---------|---------|
| `ModelGrid.tsx` | 无需大改 | 后端 API 返回合并后的模型列表，前端无感知 |
| `ModelCard.tsx` | 添加 `source` 标签 | 显示数据来源 (PGS Catalog / Literature) |
| `ModelDetailModal.tsx` | 添加 PMID 链接 | 文献提取的模型需显示论文来源 |
| `SearchSummaryView.tsx` | 添加来源统计 | 展示来自两个数据源的模型数量分布 |