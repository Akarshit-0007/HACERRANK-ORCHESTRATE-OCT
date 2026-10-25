# Evaluation Report

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
