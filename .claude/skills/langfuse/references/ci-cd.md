# Langfuse CI/CD (summary)

Implementing regression checks in GitHub Actions using the `langfuse/experiment-action`.

## Setup steps
1. **Repository verification** — confirm the repository is GitHub-hosted; the experiment action is GitHub-specific.
2. **Evaluator configuration** — determine which evaluators and run evaluators to implement.
3. **Regression thresholds** — decide whether threshold limits should be set and their values.
4. **Dataset validation** — use the Langfuse CLI to verify dataset existence/structure before implementation (list datasets, inspect sample items).
5. **Workflow triggering** — decide activation (PR, push, manual dispatch, etc.).
6. **Credentials** — configure GitHub secrets for Langfuse auth and any third-party provider APIs the evaluators need.

## Common failure points
Missing CLI authentication, incorrect secret configuration, restricted secret access in forked PRs. Verify environment variables and workflow inputs before deployment.
