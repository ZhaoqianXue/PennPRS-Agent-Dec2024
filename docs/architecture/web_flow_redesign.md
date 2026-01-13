# PennPRS Agent - Web Flow Redesign

## 1. Overview

The PennPRS Agent platform is structured as a multi-module research platform supporting three parallel functional domains:

| Module | Status | Description |
|--------|--------|-------------|
| **PennPRS-Disease** | Active | Disease risk prediction (Binary classification) |
| **PennPRS-Protein** | Active | Protein expression prediction (Regression) |
| **PennPRS-Image** | Planned | Image-derived phenotypes (IDPs) prediction |

## 2. Page Architecture

### 2.1. Landing Page (Main Entry)

**Purpose**: Central hub for module selection.

**Layout**:
- Hero header with platform branding
- Three module cards in a responsive grid
- Clear visual hierarchy distinguishing active vs. coming soon modules

**Modules**:
1. **PennPRS-Disease** (Active): Full functionality - search, train, evaluate
2. **PennPRS-Protein** (Active): Full functionality - search OmicsPred scores
3. **PennPRS-Image** (Coming Soon): Placeholder for future development

### 2.2. Disease Page (PennPRS-Disease)

**Purpose**: Complete workspace for Disease PRS analysis.

**Layout**: Split-screen design
- **Left Panel**: Interactive Canvas (visual workflow)
- **Right Panel**: Chat/Dialogue Interface (agent interaction)

#### 2.2.1. Entry State

Upon entering, the system presents an intent selection:
- **Option A**: Search & Use Existing Models (from PGS Catalog / PennPRS)
- **Option B**: Train Custom Model (using GWAS data)

#### 2.2.2. Search Workflow

```
Mode Selection (Search)
    ↓
Disease Selection Grid
    - Common diseases: AD, T2D, CAD, Breast Cancer, etc.
    - Open Targets Platform search integration
    ↓
Model Search Execution
    - Query PGS Catalog API
    - Fetch PennPRS Public Models
    - Real-time progress tracking
    ↓
Model Cards Display
    - Sortable/Filterable grid
    - Key metrics: AUC, Sample Size, Ancestry
    - Multi-selection for comparison
    ↓
Model Details Modal
    - Full metadata
    - Performance breakdown
    - Download/Bookmark actions
```

#### 2.2.3. Training Workflow

```
Mode Selection (Train)
    ↓
Training Type Selection
    - Single Ancestry Training
    - Multi-Ancestry Training
    ↓
Training Configuration Form
    - Job Name
    - Target Trait/Disease
    - GWAS Source (FinnGen, UKB, Custom)
    - PRS Methods selection
    - Population parameters
    ↓
API Submission
    - POST to PennPRS API
    - Real-time status polling
    ↓
Job Completion
    - Model added to results
    - Available for evaluation
```

### 2.3. Protein Page (PennPRS-Protein)

**Purpose**: Complete workspace for Protein/Omics PRS analysis.

**Layout**: Identical split-screen design as Disease Page

#### 2.3.1. Workflow

```
Mode Selection (Search)
    ↓
Protein Search
    - Free-text query (gene name, protein name)
    - Platform filter (Olink, SomaScan, etc.)
    ↓
Score Cards Display
    - Sortable by R², Rho, Sample Size
    - Platform badges
    - Gene annotations
    ↓
Score Details Modal
    - Performance by validation cohort
    - Gene/protein associations
    - External links (UniProt, Ensembl)
```

### 2.4. Image Page (Coming Soon)

Reserved for future image-derived phenotype prediction functionality.

## 3. Component Hierarchy

```
App (page.tsx)
├── Landing Page
│   ├── Hero Header
│   └── Module Cards Grid
│       ├── Disease Module Card
│       ├── Protein Module Card
│       └── Image Module Card (Disabled)
│
├── DiseasePage
│   ├── CanvasArea (Left)
│   │   ├── ModeSelection View
│   │   ├── DiseaseGrid View
│   │   ├── ModelGrid View
│   │   │   ├── ModelCard
│   │   │   ├── SearchSummaryView
│   │   │   └── BeeSwarmChart
│   │   ├── TrainingConfigForm View
│   │   ├── MultiAncestryTrainingForm View
│   │   └── ModelDetailModal (Overlay)
│   │
│   └── ChatInterface (Right)
│       ├── Message List
│       ├── Input Field
│       └── Quick Actions
│
├── ProteinPage
│   ├── ProteinCanvasArea (Left)
│   │   ├── ModeSelection View
│   │   ├── ProteinTargetGrid View
│   │   ├── ProteinScoreCard Grid
│   │   ├── ProteinSearchSummary View
│   │   └── ProteinDetailModal (Overlay)
│   │
│   └── ProteinChatInterface (Right)
│
└── ImagePage (Future)
```

## 4. State Management

### View Navigation

Each module implements a view stack for browser-like navigation:

```typescript
const [viewStack, setViewStack] = useState<ViewType[]>(['mode_selection']);
const [forwardStack, setForwardStack] = useState<ViewType[]>([]);

// Push new view
const pushView = (newView: ViewType) => {
  setViewStack([...viewStack, newView]);
  setForwardStack([]);
};

// Go back
const goBack = () => {
  if (viewStack.length > 1) {
    const current = viewStack[viewStack.length - 1];
    setForwardStack([current, ...forwardStack]);
    setViewStack(viewStack.slice(0, -1));
  }
};
```

### View Types

```typescript
type ViewType = 
  | 'mode_selection'
  | 'disease_selection'
  | 'model_results'
  | 'training_selection'
  | 'training_config'
  | 'multi_ancestry_training'
  | 'actions'
  | 'ancestry_filter';
```

## 5. API Integration Points

| View | API Endpoint | Purpose |
|------|-------------|---------|
| Disease Search | `POST /agent/invoke` | Trigger disease model search |
| Protein Search | `POST /protein/invoke` | Trigger protein score search |
| Disease Search | `POST /opentargets/search/disease` | Disease ontology lookup |
| Training | `POST /agent/invoke` | Submit training job |
| Progress | `GET /agent/progress/{id}` | Poll search progress |
| Details | `GET /protein/score/{id}` | Fetch score details |

## 6. Visual Design

### Color Scheme

| Module | Primary Color | Accent |
|--------|--------------|--------|
| Disease | Blue (`#3B82F6`) | Indigo |
| Protein | Violet (`#8B5CF6`) | Purple |
| Image | Gray | - |

### Animation

Using Framer Motion for:
- Page transitions
- Card hover effects
- Progress indicators
- Modal entry/exit

### Responsive Breakpoints

| Breakpoint | Layout |
|------------|--------|
| Desktop (1024px+) | Side-by-side Canvas + Chat |
| Tablet (768px-1024px) | Stacked layout |
| Mobile (<768px) | Single column with tabs |

## 7. Summary of Changes (from Original Design)

1. **New Landing Page**: Module selection moved to top-level
2. **Protein Module Active**: Fully implemented with OmicsPred integration
3. **Unified Design**: Consistent layout across Disease and Protein modules
4. **Navigation Stack**: Browser-like back/forward navigation
5. **Real-time Progress**: Visual feedback during long-running searches

---

*Document Version: 2.0*
*Last Updated: 2026-01-08*
