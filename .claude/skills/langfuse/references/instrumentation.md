# Langfuse Observability Guide - Full Content

## Overview
This document provides comprehensive guidance on instrumenting LLM applications with Langfuse tracing, following best practices tailored to specific use cases.

## Workflow Summary

### 1. Assess Current State
Evaluate the project by checking:
- Langfuse SDK installation status
- LLM frameworks in use (OpenAI SDK, LangChain, LlamaIndex, Vercel AI SDK, etc.)
- Existing instrumentation presence

**Recommendation:** Use framework integrations when available, as they "capture more context automatically and require less code than manual instrumentation."

### 2. Verify Baseline Requirements

Essential trace elements include:

| Requirement | Details |
|---|---|
| Model name | Enables model comparison and filtering |
| Token usage | Supports automatic cost calculation |
| Descriptive names | Makes traces findable (e.g., `chat-response` vs. `trace-1`) |
| Proper span hierarchy | Shows which step is slow or failing |
| Correct observation types | Use specific types (`retriever`, `agent`) rather than generic `tool`/`span` |
| Data protection | Mask PII and confidential information |
| Meaningful input/output | Capture relevant data while avoiding sensitive arguments |

**Beyond baseline context** to consider adding:
- `session_id`: Groups conversations
- `user_id`: Enables user filtering and cost attribution
- `feature` tags: Per-feature analytics
- `customer_tier` tags: Segment-based analysis
- Feedback scores: Quality filtering
- Media handling: For images, audio, files

### 3. Self-Audit Traces (Required)

This critical loop involves:

**a.** Execute the instrumented path end-to-end to generate traces

**b.** Retrieve traces from Langfuse using available tools (CLI, REST API, SDK, MCP)

**c.** Audit against best practices at: https://langfuse.com/docs/observability/best-practices

The guidance emphasizes: "Ask yourself, for each observation: is all data that a user might need in the future, to understand exactly what context the agent had when it made decisions, available in Langfuse?"

**d.** Fix identified gaps and re-run until traces meet standards

### 4. Explore Traces With Users

Guide users to explore Langfuse UI features:
- Traces view for individual requests
- Sessions view for grouped conversations
- Dashboard for filtered views
- Scores for quality metrics

## Multi-agent Systems Guidance

For systems dispatching other agents:

- **Type subagent execution as `agent`**, not generic `tool`/`span`, to preserve visibility in the Agent Graph
- **Avoid duplicate nodes** by emitting only the `agent` observation when execution is visible
- **Nest recursively** with proper sibling relationships
- **Use distinctive names** to differentiate subagents in trees and graphs

## Common Mistakes Reference

| Error | Solution |
|---|---|
| Missing `flush()` in scripts | Call `langfuse.flush()` before exit |
| Flat traces | Use nested spans for distinct steps |
| Generic naming | Use descriptive names like `chat-response` |
| Logging sensitive data | Mask PII before tracing |
| Not explicitly setting input | Use framework-specific methods to set only relevant input |
| Manual over integration | Prefer framework integrations |
| Import order issues | Load environment variables before Langfuse import; import Langfuse before OpenAI client |

---

**Reference Documentation:** https://langfuse.com/docs/tracing
