# Judge Bias Report

## Bias 1: Position bias
- A wins when listed first (run1): 0.0%
- Rule of thumb: >55% may indicate position bias.

## Bias 2: Length bias
- B wins when B is longer: 2/2 (100.0%)

## Quick table

| Metric | Value |
|---|---:|
| run1 A-win rate | 0.000 |
| B-win when longer | 1.000 |
| initialized kappa | 0.556 |

## Mitigation
- Keep swap-and-average.
- Add style normalization prompt and max token budget.
- Recalibrate with 20-50 human labels.