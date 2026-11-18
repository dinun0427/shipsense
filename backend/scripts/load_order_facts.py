import pandas as pd
from sqlalchemy import text

from app.db.session import engine

orders = pd.read_parquet("../data/processed/orders_features.parquet")
reviews = pd.read_csv(
    "../data/raw/olist_order_reviews_dataset.csv", parse_dates=["review_creation_date"]
)
# One review per order: keep the most recent.
reviews = reviews.sort_values("review_creation_date").drop_duplicates(
    "order_id", keep="last"
)[["order_id", "review_score"]]

facts = orders.merge(reviews, on="order_id", how="left")
facts["purchase_month"] = (
    facts.order_purchase_timestamp.dt.to_period("M").dt.to_timestamp().dt.date
)
facts["review_score"] = facts.review_score.astype("Int64")
facts = facts[
    [
        "order_id",
        "purchase_month",
        "customer_state",
        "seller_id",
        "is_late",
        "review_score",
    ]
]

with engine.begin() as conn:
    conn.execute(text("DELETE FROM order_facts"))  # safe to re-run
facts.to_sql("order_facts", engine, if_exists="append", index=False, chunksize=5000)
print(len(facts), "rows loaded")
