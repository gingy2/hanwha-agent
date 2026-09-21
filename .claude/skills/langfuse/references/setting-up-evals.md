# Setting Up Evals (summary)

Prioritizes discovery over immediate implementation.

1. **Determine evaluation type** — establish whether you need online (real-time production) or offline (batch/experimental) evaluation by clarifying what business decision the metrics will inform.
2. **Build metric set** — metrics must "name a specific observable behavior, be measurable, and change a decision." Without predefined metrics: online → implement user feedback workflows first; offline → analyze existing datasets and identify what matters through manual review patterns.
3. **Implementation** — only proceed after explicit metric confirmation. Avoid defaulting to LLM-as-a-judge evaluators; present methodological trade-offs to users.

## Critical principles
Prioritize understanding user needs over rushing to solutions — "people often say they want evals without knowing what they actually need." Before deployment, validate that observations match the target filter and won't be scored duplicatively. If using LLM judges, calibrate against real examples first (see `judge-calibration.md`).
