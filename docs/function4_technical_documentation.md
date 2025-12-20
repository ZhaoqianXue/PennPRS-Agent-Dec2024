# Function 4 Technical Documentation: Training PRS Models

## Overview
Function 4 enables users to train Polygenic Risk Score (PRS) models using the PennPRS ecosystem. It provides an intelligent agent workflow that guides users to either use existing models or train new ones using their own or public GWAS summary statistics.

## Architecture

### System Flow

The system follows a linear 3-step interactive workflow:

```mermaid
graph TD
    %% Step 0: Initialization
    subgraph "Step 0: Disease Selection"
        Start([User Entry]) --> UI_Grid[UI: Popular Disease Grid]
        UI_Grid -->|Select| SetTrait[Set Context: Disease/Trait]
        note right of UI_Grid
            Common AI4Medicine Diseases:
            - Alzheimer's Disease
            - Type 2 Diabetes
            - Coronary Artery Disease
            - Breast Cancer
            - etc.
        end
    end

    %% Step 1 flow
    SetTrait --> Fetch{Fetch Models}
    
    subgraph "Step 1: Model Recommendation & Training"
        direction TB
        Fetch -->|API| PGSC[PGS Catalog]
        Fetch -->|API| PennP[PennPRS Public]
        
        PGSC & PennP --> Cards[UI: Model Cards Display]
        Cards -->|Show Basic Info| CardView[Card: Name, ID, Ancestry]
        
        CardView -->|Click 'Details'| ReportView[UI: Detailed Report Modal]
        ReportView -->|Action: Use This| SelectExisting[Set Context: Selected Model]
        
        Cards -->|Action: Train New| ConfigUI[UI: Training Configuration]
        ConfigUI -->|Option| DefaultParams[Default Parameters]
        ConfigUI -->|Option| CustomParams[Custom Source/Method/Pop]
        
        CustomParams & DefaultParams --> Submit[POST /api/add_job]
        Submit --> Poll{Poll Status}
        Poll -->|Running| Poll
        Poll -->|Completed| Download[Download Result]
        Download -->|Add to List| Cards
        Download --> SelectNew[Set Context: New Model (Selected)]
    end

    %% Convergence
    SelectExisting --> Comparision{Contrast & Compare}
    SelectNew --> Comparision
    Comparision --> Ready{Model Confirmed}

    %% Step 2 flow
    subgraph "Step 2: Downstream Applications"
        Ready --> AppTabs[UI: Function Tabs]
        
        AppTabs -->|Tab 1| F1[Function 1: Evaluation]
        F1 -->|Action| Benchmark[Run Benchmarking]
        
        AppTabs -->|Tab 2| F2[Function 2: Ensemble]
        F2 -->|Action| TheOne[Run 'The One' Algorithm]
        
        AppTabs -->|Tab 3| F3[Function 3: Proteomics]
        F3 -->|Action| ProtIntegration[Integrate Proteomics Data]
    end
    
    Benchmark & TheOne & ProtIntegration --> ResultView([Final Result View])
```

### Components
1.  **Workflow Agent (LangGraph)**: Orchestrates the conversation and decision-making process.
2.  **PennPRS Client**: Handles communication with the PennPRS API (`https://pennprs.org/api`).
3.  **PGS Catalog Client**: Fetches metadata about existing scores (`https://www.pgscatalog.org/rest`).

### Data Flow
1.  **User Request**: User expresses interest in a phenotype (e.g., "Alzheimer's").
2.  **Input Analysis**: Agent checks if models exist in PennPRS/PGS Catalog.
3.  **Recommendation**: Agent recommends existing models found in PGS Catalog.
4.  **Decision**: User chooses "Use Existing" or "Train New".
5.  **Training (if selected)**:
    - User provides/selects GWAS data.
    - Agent submits job to PennPRS API.
    - Agent polls for status.
6.  **Output**: JSON report / Download link for the model.

## Technical Implementation

### 1. Core Logic (`src/core`)
-   **`pennprs_client.py`**:
    -   `add_single_job(...)`: Submits training jobs.
    -   `get_jobs(...)`: Checks job status.
    -   `download_results(...)`: Retrieves completed model.
    -   `search_public_results(...)`: Searches `pennprs.org/result` for public models (via `results_meta_data.json`).
-   **`pgs_catalog_client.py`**:
    -   `search_scores(trait)`: Fetches scores from `/score/all` and performs client-side filtering (filtering workaround due to API search limitations).
    -   `get_score_metadata(pgs_id)`: Fetches details for a specific score.

### 2. Workflow Modules (`src/modules/function4`)
-   **`models.py`**: Pydantic models for state management.
    -   `Function4State`: Tracks step, user choices, job ID, etc.
-   **`workflow.py`**: LangGraph graph definition.
    -   Nodes: `input_analysis`, `pgs_search`, `model_decision`, `submit_training`, `poll_status`.

### 3. API Integration details
-   **PennPRS API**:
    -   Base URL: `https://pennprs.org/api`
    -   Authentication: Email-based.
-   **PGS Catalog API**:
    -   Base URL: `https://www.pgscatalog.org/rest`
    -   Endpoints used: `/score/all`, `/score/{id}`.

## Configuration
-   `OPENAI_API_KEY`: Required for the LLM agent.
-   `PENNPRS_EMAIL`: (Optional) Default email for API jobs.
