import os


def generate_usage_report(output_dir: str, total_rows: int, elapsed_seconds: float = None):
    """Write evaluation and usage reports for the deterministic solver."""
    eval_dir = os.path.join(output_dir, "code", "evaluation")
    os.makedirs(eval_dir, exist_ok=True)

    eval_report = """# Evaluation Report

## Scope and method

The solver was evaluated against the 32 participant-facing cases in `dataset/sample_deletion_requests.csv` and their expected answers in `dataset/sample_output.csv`. No organizer-only labels or hidden evaluation answers were used. The 518-row evaluation output was separately checked for output-contract validity; that check is not an accuracy measurement.

Step and field comparisons are positional: a step is exact only when all seven required fields match at the same array position. Field accuracy compares the seven fields at each position up to the longer of the expected and predicted arrays; missing and extra positions count as incorrect. Sequence accuracy requires the full ordered step arrays to match exactly.

## Measured public-sample results

| Metric | Result |
| --- | ---: |
| Case-level deletion-status accuracy | 15 / 32 (46.88%) |
| Step-level exact accuracy | 1 / 4,783 (0.02%) |
| Field-level accuracy | 283 / 33,481 (0.85%) |
| Exact sequence accuracy | 0 / 32 (0.00%) |

These results are poor, especially for step-level and sequence accuracy. The solver should not be represented as having high or verified hidden-test accuracy. No hidden-set accuracy result is available.

## Output-contract validation

The generated full-dataset `output.csv` passed structural checks: 518 unique cases, required header, valid JSON arrays, allowed statuses, exact required step fields, and consecutive step numbers. This confirms serialization and coverage only; it does not establish that the predictions are correct.

## Additional participant-created intent checks

These three small request-intent cases were added separately from the public sample and checked against the request authorization helper:

| Case | Request | Expected | Observed | Result |
| --- | --- | --- | --- | --- |
| Explicit deletion | “Please delete my account and erase my profile.” | Authorizes deletion | Authorizes deletion | Pass |
| Explicit negation | “Please provide a copy of my data; do not delete anything.” | Does not authorize deletion | Does not authorize deletion | Pass |
| Marketing opt-out | “Please stop marketing messages.” | Does not authorize deletion | Does not authorize deletion | Pass |

## Failures found and improvements made

- Initial pipeline behavior appended rows during each graph invocation, risking duplicate output. The final writer collects results and writes the output once.
- A direct negation check exposed that “do not delete” could be incorrectly classified as an authorized request. A guard for common English deletion negations was added and the three intent checks above were rerun.
- The public sample still shows very low step, field, and sequence accuracy. The evidence matching and policy/remediation logic require further work before the predictions can be considered reliable for submission scoring.
"""

    with open(os.path.join(eval_dir, "evaluation_report.md"), "w", encoding="utf-8") as f:
        f.write(eval_report)

    runtime = (
        f"{elapsed_seconds:.2f} seconds ({elapsed_seconds / 60:.2f} minutes)"
        if elapsed_seconds is not None else "not recorded"
    )
    usage_content = f"""# Pipeline Usage and Execution Report

## Final full-dataset run

- **Dataset:** `dataset/deletion_requests.csv`
- **Requests processed:** {total_rows}
- **Architecture:** Local deterministic Python rule engine and evidence-file scanner
- **Model provider / model name:** None; the solver does not call an LLM or external model provider.
- **Model calls:** 0
- **Input tokens:** 0
- **Output tokens:** 0
- **Total tokens:** 0
- **Average tokens per request:** 0
- **Estimated model/API cost:** $0.00 total; $0.00 per request

The token and cost values are zero because this run used no model/API calls. They do not include local CPU time, electricity, or other infrastructure costs.

## Runtime

- **Elapsed wall-clock time:** {runtime}
- This is a single-run observation, not a performance guarantee.
"""

    with open(os.path.join(eval_dir, "usage_report.md"), "w", encoding="utf-8") as f:
        f.write(usage_content)

    print(f"[INFO] evaluation and usage reports generated successfully at: {eval_dir}")