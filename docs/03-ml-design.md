# ML Design: Delivery Delay Model

## Target
`is_late = 1` if `order_delivered_customer_date` is after
`order_estimated_delivery_date`, otherwise 0.
Only delivered orders have a target. About 8% of them are late.

## Prediction moment
Right after an order is approved. The model may only use information
that exists at that moment.

## Allowed features
- Purchase time (hour, weekday, month)
- Approval delay (approved time minus purchase time)
- Promised delivery days (estimated date minus purchase date)
- Price, freight value, number of items, product weight and volume
- Product category
- Customer state and seller state
- Distance between seller and customer
- Seller history (late rate), computed only from earlier data

## Forbidden features (data leakage)
- Actual delivery date
- Carrier pickup date
- Review score or review text
- Anything that happens after the prediction moment

## Train, validation and test split
Split by time, not randomly:
- First 70% of orders by purchase time: training
- Next 15%: validation (choose settings and threshold here)
- Last 15%: test (look at it once, at the end)

Why: in real use we predict the future from the past. A random split would
let the model see the future during training and give fake, too-good scores.

## Metrics
Accuracy is misleading because only about 8% of orders are late.
Use PR-AUC, ROC-AUC, precision and recall, and always compare with a baseline.

## Baselines
1. Always predict the late rate (PR-AUC is about 0.08)
2. Logistic regression on numeric features
