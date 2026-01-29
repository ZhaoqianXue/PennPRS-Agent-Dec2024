# References

This document lists the key academic papers and research that inform the architectural and strategic decisions of the PennPRS Agent project, particularly regarding Multi-Agent systems and autonomous scientific reasoning.

## Core Agentic AI & Orchestration

### [1] The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery
- **Authors**: Chris Lu, Cong Lu, Robert Tjarko Lange, Jakob Foerster, Jeff Clune, David Ha
- **Venue**: arXiv / Sakana AI (2024)
- **Contribution**: Demonstrates a fully autonomous agentic loop for scientific research, from hypothesis generation to experiment execution and peer-review-style evaluation. Justifies the use of autonomous Orchestrator Agents in scientific domains.
- **Link**: [arXiv:2408.06292](https://arxiv.org/abs/2408.06292)

### [2] Chain-of-Abstraction: Learning to Use Large Language Models with Abstract Planning
- **Authors**: Silin Gao, et al.
- **Venue**: NeurIPS (2024)
- **Contribution**: Proposes a "Chain-of-Abstraction" (CoA) framework where agents learn to create abstract multi-step plans before calling concrete tools. This informs the PennPRS Orchestrator's ability to plan cross-disease reasoning paths before executing specific database queries.
- **Link**: [arXiv:2401.17464](https://arxiv.org/abs/2401.17464)

### [3] Quiet-STaR: Language Models Can Teach Themselves to Think Before Speaking
- **Authors**: Eric Zelikman, Georges Harik, Yoram Bachrach, Oriol Vinyals, Noah D. Goodman
- **Venue**: arXiv (2024) - Evolution of the STaR (Self-Taught Reasoner) framework
- **Contribution**: Introduces a method for LLMs to generate internal "thoughts" or search-based reasoning paths before generating an output. Supports the "Reasoning-on-the-fly" and "Self-Correction" capabilities required for our Orchestrator Agent.
- **Link**: [arXiv:2403.09629](https://arxiv.org/abs/2403.09629)

---

## Domain Specific & Tooling (Internal References)
- **PennPRS API Documentation**: Internal documentation for the PennPRS training engine.
- **PGS Catalog (PGSc)**: External resource for existing Polygenic Risk Score models.
- **All of Us Research Program**: NIH-funded large-scale genomic cohort used for empirical validation.
