# Langfuse User Feedback Implementation Guide (summary)

Structured workflow for capturing user feedback as Langfuse scores.

## Phase 1 — determine feedback to capture
Check if users have specific feedback requests. If not, present a few UX options for how feedback could work before building anything — review the Capturing Signals docs and examine the app's existing scores. When proposing metrics, present a table: priority (P0/P1/...), current implementation status, signal naming (based on observed behavior, not desired outcomes), explanation with known limitations, effort estimate (XS–L), implementation approach.

## Phase 2 — implementation
Consult the user feedback loop guide and current SDK documentation before writing code.

## Phase 3 — verification
Test each signal to confirm proper name, value, data type, and attachment in Langfuse.

## Core principle
Name signals after the observed signal, not the quality you hope it represents. Reuse consistent naming across applications.
