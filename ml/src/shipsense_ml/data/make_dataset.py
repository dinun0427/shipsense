from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/processed")


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"olist_{name}_dataset.csv")


def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance between two points on Earth, in km."""
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi, dlmb = p2 - p1, np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def zip_latlng() -> pd.DataFrame:
    # The geolocation table has many rows per zip prefix: take the median.
    geo = load("geolocation")
    return (
        geo.groupby("geolocation_zip_code_prefix")
        .agg(lat=("geolocation_lat", "median"), lng=("geolocation_lng", "median"))
        .reset_index()
    )


def build_orders() -> pd.DataFrame:
    orders = load("orders")
    for col in [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]:
        orders[col] = pd.to_datetime(orders[col])

    # Only delivered orders with all needed dates have a valid target.
    orders = orders[
        (orders.order_status == "delivered")
        & orders.order_delivered_customer_date.notna()
        & orders.order_approved_at.notna()
    ].copy()
    orders["is_late"] = (
        orders.order_delivered_customer_date > orders.order_estimated_delivery_date
    ).astype(int)

    # One order can hold several items: summarize them per order.
    items = load("order_items").merge(load("products"), on="product_id", how="left")
    items["product_weight_g"] = items.product_weight_g.replace(
        0, np.nan
    )  # zero = unknown
    items["volume_cm3"] = (
        items.product_length_cm * items.product_height_cm * items.product_width_cm
    )
    per_order = (
        items.groupby("order_id")
        .agg(
            n_items=("order_item_id", "max"),
            n_sellers=("seller_id", "nunique"),
            price_sum=("price", "sum"),
            freight_sum=("freight_value", "sum"),
            weight_g=("product_weight_g", lambda s: s.sum(min_count=1)),
            volume_cm3=("volume_cm3", lambda s: s.sum(min_count=1)),
            seller_id=("seller_id", "first"),
            category=("product_category_name", "first"),
        )
        .reset_index()
    )

    # Translate Portuguese category names to English.
    tr = pd.read_csv(RAW / "product_category_name_translation.csv")
    per_order = per_order.merge(
        tr, left_on="category", right_on="product_category_name", how="left"
    )
    per_order["category"] = per_order.product_category_name_english.fillna("unknown")
    per_order = per_order.drop(
        columns=["product_category_name", "product_category_name_english"]
    )

    # Locations -> coordinates -> distance between seller and customer.
    geo = zip_latlng()
    cust = load("customers")[
        ["customer_id", "customer_zip_code_prefix", "customer_state"]
    ]
    cust = cust.merge(
        geo.rename(
            columns={
                "geolocation_zip_code_prefix": "customer_zip_code_prefix",
                "lat": "cust_lat",
                "lng": "cust_lng",
            }
        ),
        on="customer_zip_code_prefix",
        how="left",
    )
    sell = load("sellers")[["seller_id", "seller_zip_code_prefix", "seller_state"]]
    sell = sell.merge(
        geo.rename(
            columns={
                "geolocation_zip_code_prefix": "seller_zip_code_prefix",
                "lat": "sell_lat",
                "lng": "sell_lng",
            }
        ),
        on="seller_zip_code_prefix",
        how="left",
    )

    df = (
        orders.merge(per_order, on="order_id", how="inner")
        .merge(cust, on="customer_id", how="left")
        .merge(sell, on="seller_id", how="left")
    )

    # Features that are known at prediction time (right after approval).
    df["distance_km"] = haversine_km(df.cust_lat, df.cust_lng, df.sell_lat, df.sell_lng)
    df["same_state"] = (df.customer_state == df.seller_state).astype(int)
    df["purchase_hour"] = df.order_purchase_timestamp.dt.hour
    df["purchase_dow"] = df.order_purchase_timestamp.dt.day_of_week
    df["purchase_month"] = df.order_purchase_timestamp.dt.month
    df["approval_hours"] = (
        df.order_approved_at - df.order_purchase_timestamp
    ).dt.total_seconds() / 3600
    df["promised_days"] = (
        df.order_estimated_delivery_date - df.order_purchase_timestamp
    ).dt.total_seconds() / 86400
    df["freight_ratio"] = df.freight_sum / (df.price_sum + 1)

    # Remove impossible rows.
    df = df[(df.promised_days > 0) & (df.approval_hours >= 0)]
    return df


def build_reviews() -> pd.DataFrame:
    r = load("order_reviews")
    r["review_creation_date"] = pd.to_datetime(r.review_creation_date)
    # Some orders have several reviews: keep the most recent one.
    r = r.sort_values("review_creation_date").drop_duplicates("order_id", keep="last")
    text = r.review_comment_title.fillna("") + " " + r.review_comment_message.fillna("")
    r["text"] = text.str.replace(r"\s+", " ", regex=True).str.strip()
    r = r[r.text.str.len() > 0].copy()
    # 1-2 stars negative, 3 neutral, 4-5 positive.
    r["sentiment"] = pd.cut(
        r.review_score, bins=[0, 2, 3, 5], labels=["negative", "neutral", "positive"]
    ).astype(str)
    return r[["order_id", "review_creation_date", "review_score", "text", "sentiment"]]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    orders_df = build_orders()
    reviews_df = build_reviews()
    orders_df.to_parquet(OUT / "orders_features.parquet", index=False)
    reviews_df.to_parquet(OUT / "reviews.parquet", index=False)
    print("orders:", orders_df.shape, "late rate:", round(orders_df.is_late.mean(), 3))
    print("reviews:", reviews_df.shape)
    print(reviews_df.sentiment.value_counts(normalize=True).round(3))
