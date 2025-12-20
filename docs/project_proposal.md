# PennPRS_Agent, use ADRD as example

## Users
- User having indiviual-level data (AD label and genetic data), deployed locally.
- If no indiviual-level data, we have in-house data can be used.
- User may also have GWAS summary statsitcis of interest.

## Focusing
- Risk prediction and stratification.
- Omics data (association and prediction and stratification).

## Function
### Function(1): Benchmarking AD PRS Methods
- Benchmarking AD PRS methods on your local data (PennPRS FinnGen models, use UKB as testing data);
- AD GWAS data resources (FinnGen for now) and PRS methods.

### Function(2): The One: ensemble models cross phenotypes
- (PennPRS models for now)

### Function(3): Proteomics PRS Models
- Protomics PRS models for AD, do marginal proteins, also can we do multiple proteins together?
- Pertentially combine with "The One"
- (PennPRS models for now)

### Function(4): Training PRS Models
- Train PRS models (provide their own GWAS summary statsitcis, no need to click on our website).
- Learn about PennPRS https://pennprs.org/ and PGS Catalog https://www.pgscatalog.org/ then setup the agent workflow. 
- Function(4) Workflow (New 3-Step Interaction):
    1. **Step 0: Disease Selection**:
        - User starts by selecting a target disease (e.g., AD, T2D) from a predefined grid.
    2. **Step 1: Model Recommendation & Training**:
        - **Model Cards**: System displays formatted cards for existing models (PennPRS/PGS Catalog) and any user-trained models.
        - **Training**: User can choose to train a new model via PennPRS API. Newly trained models are added to the list for comparison.
        - **Reports**: Detailed markdown reports available for any model.
    3. **Step 2: Downstream Applications**:
        - Once a model is selected/trained, user proceeds to Function(1) (Evaluation), Function(2) (Ensemble), or Function(3) (Proteomics).

## Random thoughts
- PennPRS https://pennprs.org/ and PGS Catalog https://www.pgscatalog.org/.
- Pathway analysis.
- UKB-RAP and AOU deployment, for now, we do it locally.
- Can we make it smarter? Which will be useful for certain tasks.
- Follow-up post-PRS analysis code.

## Tech Stack
- Frontend: React + Next.js + TypeScript (for type safety) + Tailwind CSS (for styling)
- Backend: FastAPI + LangGraph + Pydantic
- LLM: gpt-5-mini

# Task
- 你的任务是实现Function(4): Training PRS Models，首先请你阅读`.cursorrules`，写一个详细的技术文档。