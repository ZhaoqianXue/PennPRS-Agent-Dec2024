# PennPRS Agent - Web Flow Redesign

## 1. Overview
The PennPRS Agent platform is being restructured to support three parallel functional domains:
1.  **PRS-Disease**: Predicting disease risk (Binary classification).
2.  **PRS-Protein**: Predicting protein expression levels (Regression).
3.  **PRS-Image**: Predicting image-derived phenotypes (IDPs) (Regression).

Currently, development will focus on the **Disease** module, with Protein and Image serving as placeholders for future expansion.

## 2. Page Flow & Architecture

### 2.1. Main Page (Landing Page)
**Purpose**: The entry point for the user to select the functional domain.
*   **Layout**: A clean landing page featuring three distinct cards/modules.
*   **Modules**:
    1.  **Disease** (Active): Clickable. Navigates to the Disease Page.
    2.  **Protein** (Inactive/Coming Soon): Placeholder.
    3.  **Image** (Inactive/Coming Soon): Placeholder.

### 2.2. Disease Page
**Purpose**: The main workspace for Disease PRS tasks.
*   **Layout**: Split screen.
    *   **Left**: Interactive Canvas (Visual interface).
    *   **Right**: Chat/Dialogue Interface (Agent interaction).

#### 2.2.1. Initial State (Entry)
*   **Action**: Upon entering the Disease Page, the Agent (in the chat) or a Modal/UI prompt asks the user to choose their primary intent:
    *   **Option A**: Search & Use Existing Models (from PGS Catalog / PennPRS).
    *   **Option B**: Train Custom Model (using User's GWAS data).

#### 2.2.2. Workflow A: Search/Use Existing Models
*   **Trigger**: User selects "Search Existing Models".
*   **Canvas State**: Displays the **Disease Selection Grid** (current homepage state).
    *   Grid of cards representing different diseases (e.g., Alzheimer's, Type 2 Diabetes).
*   **User Action**: User clicks a Disease Card.
*   **System Action**:
    *   Trigger the "Search Models" workflow.
    *   Agent searches for available models for the selected disease.
    *   Results are displayed in the chat or canvas (Model Cards).

#### 2.2.3. Workflow B: Train Custom Model
*   **Trigger**: User selects "Train Custom Model".
*   **UI Response**: Opens the **Train Custom Model Modal/Form** (similar to the current "Train" button functionality).
*   **Form Content**:
    *   Input fields for Job Name.
    *   Selection for Traits/Target.
    *   File Upload / Selection for GWAS Summary Statistics.
    *   Parameter configuration (Methods, Populations, etc.).
*   **Action**: User submits the form to start the training job via the PennPRS API.

## 3. Summary of Changes
1.  **New Landing Page**: The current "Disease Grid" page is moved one level deep. The new root is the 3-module selection page.
2.  **Branching Logic**: Explicit choice at the start of the Disease module between "Consumption" (Search) and "Creation" (Train).
3.  **Navigation**: Added hierarchy to accommodate parallel functionalities.

## 4. Visual Workflow

```mermaid
graph TD
    A[Main Page] --> B{Select Module}
    B -->|Disease| C[Disease Page]
    B -->|Protein| D[Protein Page<br/>(Coming Soon)]
    B -->|Image| E[Image Page<br/>(Coming Soon)]

    C --> F{User Intent}
    F -->|Search Existing Models| G[Disease Selection Grid]
    F -->|Train Custom Model| H[Training Form Modal]

    G -->|Select Disease| I[Search Results / Model Cards]
    H -->|Submit Config| J[Start Training Job]
```
