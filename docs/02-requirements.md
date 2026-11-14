# Requirements

| ID | Type | Requirement |
| --- | --- | --- |
| F1 | Functional | A user can submit order details and receive a late-delivery probability |
| F2 | Functional | The response lists the top factors behind the prediction |
| F3 | Functional | A user can submit review text and receive a sentiment label |
| F4 | Functional | A dashboard shows late rate by state and monthly trend |
| F5 | Functional | Every prediction is stored with a timestamp and model version |
| N1 | Non-functional | Prediction API responds in under 300 ms (p95) locally |
| N2 | Non-functional | All code is covered by automated tests in CI |
| N3 | Non-functional | The whole system starts with one command (`docker compose up`) |
| N4 | Non-functional | Training runs are reproducible from tracked data and code |

## User stories
- As an operations analyst, I want to see the risk of a delayed order so that
  I can contact the seller before the customer is disappointed.
- As an operations analyst, I want to see which states have the most late
  deliveries so that I can focus on the worst regions.
- As a support agent, I want to see whether a review is negative so that I
  can answer unhappy customers first.
