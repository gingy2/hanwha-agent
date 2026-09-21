# Judge Calibration (LLM-as-a-Judge) — summary

Validates LLM judge outputs against human labels using Langfuse datasets and experiments. Two modes: simple calibration for quick accuracy checks, advanced calibration for confusion-matrix metrics.

1. **Mode selection** — Simple: "does this judge match human labels?" (accuracy only). Advanced: used when confusion matrices, thresholds, or production automation are needed.
2. **Primary workflow** — Confirm dataset details, choose mode, run the judge as a Langfuse experiment, compare outputs to `expectedOutput`, return results.
3. **Experiment workflow** — Fetch current SDK docs before implementation. Load dataset and judge prompt → define positive/negative label sets → task function compiles prompt and calls judge model → item evaluator compares judge output to expected output → run evaluator aggregates accuracy metrics.
4. **Label validation** — Normalize labels deterministically (whitespace, casing). Exclude invalid labels from denominators.
5. **Metrics** — Simple: `accuracy = matches / valid_rows`. Advanced: precision, recall, F1, TPR, TNR with zero-denominator guardrails.
6. **Report format** — Simple: dataset name, valid rows, invalid count, accuracy, recommendation. Advanced: adds confusion matrix, all metrics, failure direction analysis, actionable recommendations.
7. **Failure modes** — Unconstrained label vocabularies, leaking ground truth into tasks, ignoring class imbalance. After calibration, iterate on dev data or freeze and monitor drift.
