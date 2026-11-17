from pathlib import Path

import joblib
import numpy as np
import pandas as pd

CAT = ["category", "customer_state", "seller_state"]


class DelayPredictor:
    def __init__(self, path: Path):
        art = joblib.load(path)
        self.model = art["model"]
        self.features = art["features"]
        self.categories = art["categories"]
        self.threshold = art["threshold"]
        self.version = art["version"]

    def _row(self, r) -> dict:
        price, freight = r.price_sum, r.freight_sum
        return {
            "n_items": r.n_items,
            "n_sellers": r.n_sellers,
            "price_sum": price,
            "freight_sum": freight,
            "weight_g": r.weight_g,
            "volume_cm3": r.volume_cm3,
            "distance_km": r.distance_km,
            "same_state": int(r.customer_state.upper() == r.seller_state.upper()),
            "purchase_hour": r.purchase_timestamp.hour,
            "purchase_dow": r.purchase_timestamp.weekday(),
            "approval_hours": (
                r.approved_timestamp - r.purchase_timestamp
            ).total_seconds()
            / 3600,
            "promised_days": (
                r.estimated_delivery_date - r.purchase_timestamp
            ).total_seconds()
            / 86400,
            "freight_ratio": freight / (price + 1),
            "category": r.category,
            "customer_state": r.customer_state.upper(),
            "seller_state": r.seller_state.upper(),
        }

    def predict(self, req) -> dict:
        X = pd.DataFrame([self._row(req)]).reindex(columns=self.features)
        numeric = [c for c in self.features if c not in CAT]
        X[numeric] = X[numeric].astype(float)
        for c in CAT:
            X[c] = pd.Categorical(X[c], categories=self.categories[c])
        p = float(self.model.predict_proba(X)[0, 1])
        contrib = self.model.predict(X, pred_contrib=True)[0][
            :-1
        ]  # last value is the bias
        top = np.argsort(-np.abs(contrib))[:3]
        factors = [
            {
                "feature": self.features[i],
                "contribution": round(float(contrib[i]), 3),
                "direction": "increases risk" if contrib[i] > 0 else "reduces risk",
            }
            for i in top
        ]
        label = (
            "high"
            if p >= self.threshold
            else "medium"
            if p >= self.threshold / 2
            else "low"
        )
        return {
            "late_probability": round(p, 4),
            "risk_label": label,
            "top_factors": factors,
            "model_version": self.version,
        }


class SentimentModel:
    def __init__(self, path: Path):
        art = joblib.load(path)
        self.pipeline = art["pipeline"]
        self.version = art["version"]

    def predict(self, text: str) -> dict:
        proba = self.pipeline.predict_proba([text])[0]
        i = int(np.argmax(proba))
        return {
            "sentiment": str(self.pipeline.classes_[i]),
            "confidence": round(float(proba[i]), 4),
            "model_version": self.version,
        }
