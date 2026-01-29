# Knowledge Base

This directory contains curated technical knowledge, engineering best practices, and research summaries relevant to the development and optimization of AI agents.

## Directory Structure

### [Context Engineering](./context_engineering/)
Strategies for managing and optimizing the information (tokens) passed to LLMs to improve agent performance, latency, and cost.

- **[Manus: Context Engineering](./context_engineering/manus_context_engineering.md)**: Lessons from building Manus, focusing on KV-cache optimization, tool masking, and using the file system as external memory.
- **[Anthropic: Effective Context Engineering](./context_engineering/anthropic_context_engineering.md)**: Anthropic's mental model for curating context, including the "Goldilocks Zone" for prompts and Just-in-Time (JIT) retrieval.
- **[Anthropic: Long-Running Agents](./context_engineering/anthropic_long_running_agents.md)**: Strategies for maintaining coherence across multiple context windows using Initializer/Coding agent roles and structured progress tracking.

## How to use this knowledge
- **Context Engineering**: Reference these documents when designing prompt structures, tool definitions, or handling long-range dependencies in agent workflows.
