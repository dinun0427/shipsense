# Sentiment Model

Task: classify Portuguese review text as negative, neutral or positive
(1-2 stars, 3 stars, 4-5 stars).

Split by time: oldest 70% train, next 15% validation, newest 15% test.
Metric: macro-F1, because 66% of reviews are positive.

| Experiment | Val macro-F1 | Decision |
| --- | --- | --- |
| TF-IDF words (1-2 grams) + logistic regression | 0.672 | Keep |
| Added character n-grams | 0.677 | Reverted: gain of 0.005 is within noise, and the model is larger and slower |

## Results on the test set (final model)
- Macro-F1 0.668, accuracy 0.83
- Negative F1 0.81, positive F1 0.91, neutral F1 0.29

## Limitations
- Neutral (3-star) reviews are hard: they mix praise and complaints.
- Only 41% of orders have a review with text.
- Star rating is a proxy for sentiment, so labels are noisy.
- Brazilian Portuguese, 2016 to 2018 only.

## Known weakness
- "produto chegou muito atrasado" (arrived very late) is classified positive
  (confidence 0.58). Words like "produto chegou" appear mostly in positive
  reviews, and a bag-of-words model cannot read negation or meaning.
- Possible upgrade: fine-tune a Portuguese transformer and compare on the
  same test set.
