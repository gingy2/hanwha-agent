# Langfuse Dataset Construction Workflow (summary)

## Core Purpose
Guides collaborative creation of Langfuse datasets, particularly a "minimal but complete dataset" for quality checks or regression prevention.

## Key Process Steps
Interview → proposal → approval → implementation:
1. Consult the Langfuse Academy datasets guide and current documentation
2. Clarify the underlying business problem through user interviews
3. Review available context (existing traces, scores, feedback, etc.)
4. Propose dataset distribution dimensions and item schema for approval
5. Generate a minimal draft (typically 5-12 items) for review
6. Have users validate expected outputs before finalizing

## Critical Guardrails
Do not create, upsert, reshape, or upload a live Langfuse dataset until the user has approved the dataset goal, source mix, item schema, and first minimal draft.

Keep structural clarity by separating `input`, `expectedOutput`, and `metadata` — additional notes belong in metadata, not in input or output fields.

Prefer starting small and reviewable over attempting broad coverage in initial versions.
