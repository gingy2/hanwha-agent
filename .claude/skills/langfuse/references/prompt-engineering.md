# Prompt Engineering Guide (summary)

## Universal Principles
1. **Clarity and specificity** — state the required output format, constraints, and, when order matters, numbered steps.
2. **Structured formatting** — labeled sections and XML tags to distinguish different prompt components.
3. **Role assignment** — a focused system prompt helps direct the model's tone and behavior.
4. **Reasoning transparency** — explaining the rationale behind important rules enables better generalization.

## Systematic Debugging
When adjusting existing prompts:
- Identify concrete failures before attempting fixes
- Trace issues back to specific prompt gaps or ambiguities
- Address error categories broadly rather than single instances
- Maintain proven functionality while making edits
- Test one change at a time for clear attribution

## Model-Specific Considerations
Claude reasoning models benefit from goal-level instructions and native thinking capabilities; standard models often need more prescriptive, density-packed guidance and explicit chain-of-thought prompting.
