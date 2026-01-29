# Proposal Enhancement TODO

Based on analysis of the **LLM Agentic Engineering Knowledge Base** (Anthropic Long-Running Agents, Anthropic Context Engineering, Manus Context Engineering), the following adjustments are required for `proposal.md`.

---

## Timing Classification

Each TODO item is classified by **when** it needs to be addressed:

| Tag | Meaning | Impact |
| :--- | :--- | :--- |
| `PRE-PROTO` | **Pre-Prototype Constraint** | Must decide before prototype development; changing later requires significant refactoring |
| `POST-PROTO` | **Post-Prototype Optimization** | Can be added after prototype; easy to layer on existing code |

### Pre-Prototype Decisions Required

These 3 architectural decisions **must be made before prototype development**:

1. **Tool Definition Strategy**: Static tools + logit masking vs dynamic tool injection
2. **JIT Context Loading vs Pre-load All**: Return references vs full data from tools
3. **Error Trace Retention Policy**: Keep failed actions in history vs hide and retry

---

## P0 - Critical (Must Do)

### 1. Add "Context Engineering Framework" Section

**Location**: Under `## Architecture` section

**Content to Add**:
- [ ] **Context State Management**: Define how the agent manages context window state `POST-PROTO`
- [ ] **Memory Externalization**: Define file-based memory mechanism (`todo.md`, `agent-progress.md`) `POST-PROTO`
- [ ] **Compaction Strategy**: Define context compression strategy and trigger conditions `POST-PROTO`
- [ ] **JIT Data Loading**: Define just-in-time context retrieval vs pre-loaded context `PRE-PROTO`

**Reference**: 
- Anthropic Context Engineering: "Compaction", "Structured Note-taking"
- Manus: "Use the File System as Context", "Manipulate Attention Through Recitation"

---

### 2. Add Context Engineering Module to Implementation Plan

**Location**: Phase 2, as new Module 3.5 or Module 6

**Content to Add**:
- [ ] **Module X: Context Engineering Infrastructure** `POST-PROTO`
  - Progress File mechanism (similar to `claude-progress.txt`)
  - Todo Recitation mechanism (similar to Manus `todo.md`)
  - Compaction trigger and strategy
  - Error trace retention strategy (decision is `PRE-PROTO`, implementation is `POST-PROTO`)

**Reference**:
- Anthropic Long-Running Agents: "claude-progress.txt", "feature_list.json"

---

## P1 - Important (Should Do)

### 3. Enhance Module 3 (Prompt Engineering)

**Location**: Phase 2 > Module 3

**Content to Add**:
- [ ] **"Right Altitude" Design Principle**: Balance between hardcoded complexity and vague guidance `POST-PROTO`
- [ ] **JIT Context Loading Strategy**: Lightweight identifiers + on-demand data loading `PRE-PROTO`
- [ ] **Diversity Strategy**: Avoid few-shot pattern rigidity through structured variation `POST-PROTO`
- [ ] **Prompt Prefix Stability**: Avoid timestamps or dynamic content at prompt start (KV-cache) `POST-PROTO`

**Reference**:
- Anthropic Context Engineering: "System prompts should be at the right altitude"
- Manus: "Don't Get Few-Shotted", "Keep your prompt prefix stable"

---

### 4. Enhance Module 4 (Toolset Implementation)

**Location**: Phase 2 > Module 4

**Content to Add**:
- [ ] **KV-Cache Friendly Design**: Stable prefix, append-only context, deterministic serialization `POST-PROTO`
- [ ] **Token-Efficient Tool Output**: Minimize observation size, use restorable compression `POST-PROTO`
- [ ] **Logit Masking Strategy**: Use masking instead of dynamic tool add/remove `PRE-PROTO`
- [ ] **Self-Contained Tools**: Each tool should be robust to errors and unambiguous `POST-PROTO`

**Reference**:
- Manus: "Design Around the KV-Cache", "Mask, Don't Remove"
- Anthropic Context Engineering: "Tools should be self-contained, robust to error"

---

### 5. Add "Error Recovery & Testing" Content

**Location**: New subsection under Architecture or new Module in Phase 4

**Content to Add**:
- [ ] **Error Trace Retention**: Keep failed actions in context (don't hide errors) `PRE-PROTO`
- [ ] **Recovery Protocol**: Define how agent recovers from failures `POST-PROTO`
- [ ] **End-to-End Testing Strategy**: Browser automation or equivalent validation `POST-PROTO`

**Reference**:
- Manus: "Keep the Wrong Stuff In"
- Anthropic Long-Running Agents: "Testing" section, Puppeteer MCP

---

## P2 - Nice to Have (Optional)

### 6. Evaluate Initializer Agent Pattern

**Location**: Architecture section

**Content to Consider**:
- [ ] **Single Agent vs Dual Agent**: Current design uses single agent; evaluate if complex tasks need Initializer + Coding Agent pattern `POST-PROTO`
- [ ] **Session Handoff Protocol**: If multi-context-window scenarios are expected, define handoff mechanism `POST-PROTO`

**Reference**:
- Anthropic Long-Running Agents: "Initializer Agent" + "Coding Agent" two-part solution

---

## Summary Table

| Priority | Item | Timing | Status |
| :--- | :--- | :--- | :--- |
| P0 | Add Context Engineering Framework section | Mixed | [ ] |
| P0 | Add Context Engineering Module to Implementation Plan | POST-PROTO | [ ] |
| P1 | Enhance Module 3 (Prompt Engineering) | Mixed | [ ] |
| P1 | Enhance Module 4 (Toolset Implementation) | Mixed | [ ] |
| P1 | Add Error Recovery & Testing content | Mixed | [ ] |
| P2 | Evaluate Initializer Agent Pattern | POST-PROTO | [ ] |

---

## Pre-Prototype Action Items (Must Do Now)

These specific items **must be decided before prototype development**:

| # | Decision | Options | Recommended | Done |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Tool Definition Strategy | Static+Mask vs Dynamic | Static+Mask | [x] |
| 2 | JIT Context Loading | JIT vs Pre-load | JIT (return references) | [x] |
| 3 | Error Trace Retention | Keep vs Hide | Keep in history | [x] |

> **Status**: All PRE-PROTO decisions have been documented in `proposal.md` under `## Architecture > ### Agent Engineering Constraints`.

---

## Notes

- All changes should align with the three knowledge base documents in `.agent/knowledge/context_engineering/`
- Updates should maintain proposal's existing functional design while adding reliability engineering layer
- Consider creating a dedicated "Context Engineering" section rather than scattering content across modules
