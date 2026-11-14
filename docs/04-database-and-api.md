# Database and API Design

## Database tables

| Table | Key columns |
| --- | --- |
| predictions | id, created_at, input_json, late_probability, risk_label, top_factors_json, model_version |
| review_analyses | id, created_at, text, sentiment, confidence, model_version |
| order_facts | order_id, purchase_month, customer_state, seller_id, is_late, review_score |

## API endpoints

| Method and path | Purpose |
| --- | --- |
| GET /health | Check the service is alive |
| POST /api/v1/predict-delay | Send order details, get probability, risk label and top factors |
| POST /api/v1/analyze-review | Send review text, get sentiment and confidence |
| GET /api/v1/insights/late-rate | Late rate grouped by state or month |
| GET /api/v1/insights/sentiment | Average review score over time |
| GET /api/v1/predictions | Recent stored predictions |
