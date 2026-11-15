# Experiment Log: Delay Model

All decisions use the validation split. Test was looked at only as a rough warning.

| Experiment | Change | Val PR-AUC | Val ROC-AUC | Decision |
| --- | --- | --- | --- | --- |
| Baseline B | Logistic regression | 0.145 | n/a | Reference |
| 1 | LightGBM, all features | 0.154 | 0.733 | Stopped at round 6 |
| 2 | Removed purchase_month | 0.173 | 0.746 | Keep: month does not generalize to new months |
| 3 | num_leaves 31 to 8, min_child_samples 40 to 200 | 0.177 | 0.762 | Keep: simpler model generalizes better |
| 4 | Removed seller history features | 0.184 | 0.767 | Keep: history from the training period was stale later |

## Findings
- Late rate drifts over time: 9.0% in train, 5.3% in validation, 6.6% in test.
- Final test PR-AUC is about 0.09 against a 0.066 "always guess" baseline, a small
  but real improvement.
- Order data alone cannot see weather, carrier strikes or road problems, so a
  modest score is expected.
- Early stopping must watch PR-AUC only (first_metric_only=True), because
  class weighting makes logloss worse by design.
