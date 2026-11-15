from datetime import datetime
from pathlib import Path

import joblib
import lightgbm as lgb
import mlflow
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NUM = [
    "n_items",
    "n_sellers",
    "price_sum",
    "freight_sum",
    "weight_g",
    "volume_cm3",
    "distance_km",
    "same_state",
    "purchase_hour",
    "purchase_dow",
    "approval_hours",
    "promised_days",
    "freight_ratio",
]
SELLER = []
CAT = ["category", "customer_state", "seller_state"]
FEATURES = NUM + SELLER + CAT


def fit_seller_stats(df, prior, k=20):
    # Late rate per seller. Sellers with few orders are pulled toward the overall rate.
    g = df.groupby("seller_id").is_late.agg(["sum", "count"])
    return pd.DataFrame(
        {
            "seller_late_rate": (g["sum"] + prior * k) / (g["count"] + k),
            "seller_orders": g["count"],
        }
    )


def apply_seller_stats(df, stats, prior):
    out = df.join(stats, on="seller_id")
    out["seller_late_rate"] = out["seller_late_rate"].fillna(prior)
    out["seller_orders"] = out["seller_orders"].fillna(0)
    return out


def to_matrix(df, categories):
    X = df[FEATURES].copy()
    for c in CAT:
        X[c] = pd.Categorical(X[c], categories=categories[c])
    return X


def metrics(y, p, thr):
    pred = (p >= thr).astype(int)
    return {
        "pr_auc": average_precision_score(y, p),
        "roc_auc": roc_auc_score(y, p),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred),
    }


def main():
    df = (
        pd.read_parquet("data/processed/orders_features.parquet")
        .sort_values("order_purchase_timestamp")
        .reset_index(drop=True)
    )
    n = len(df)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    train, val, test = df.iloc[:i1].copy(), df.iloc[i1:i2].copy(), df.iloc[i2:].copy()
    prior = train.is_late.mean()

    # Seller features for TRAIN are computed "out of fold", so a row never sees its own label.
    parts = []
    for fit_idx, app_idx in KFold(5, shuffle=True, random_state=42).split(train):
        stats = fit_seller_stats(train.iloc[fit_idx], prior)
        parts.append(apply_seller_stats(train.iloc[app_idx], stats, prior))
    train = pd.concat(parts).sort_index()
    seller_stats = fit_seller_stats(train, prior)
    val = apply_seller_stats(val, seller_stats, prior)
    test = apply_seller_stats(test, seller_stats, prior)

    categories = {c: sorted(train[c].dropna().unique().tolist()) for c in CAT}
    X_tr, X_va, X_te = (to_matrix(d, categories) for d in (train, val, test))
    y_tr, y_va, y_te = train.is_late, val.is_late, test.is_late

    mlflow.set_experiment("delay-model")
    with mlflow.start_run():
        # Baseline A: always predict the overall late rate.
        print(
            "Baseline A (always guess the late rate): PR-AUC =",
            round(float(y_va.mean()), 3),
        )
        mlflow.log_metric("baseline_prior_val_pr_auc", float(y_va.mean()))

        # Baseline B: logistic regression on numeric features.
        base = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced"),
        )
        base.fit(X_tr[NUM + SELLER], y_tr)
        base_pr = average_precision_score(
            y_va, base.predict_proba(X_va[NUM + SELLER])[:, 1]
        )
        print("Baseline B (logistic regression): PR-AUC =", round(float(base_pr), 3))
        mlflow.log_metric("baseline_logreg_val_pr_auc", float(base_pr))

        params = dict(
            n_estimators=3000,
            learning_rate=0.03,
            num_leaves=8,
            min_child_samples=200,
            subsample=0.8,
            subsample_freq=1,
            colsample_bytree=0.8,
            scale_pos_weight=(1 - prior) / prior,
            random_state=42,
        )
        model = lgb.LGBMClassifier(**params)
        model.fit(
            X_tr,
            y_tr,
            eval_set=[(X_va, y_va)],
            eval_metric="average_precision",
            callbacks=[
                lgb.early_stopping(100, first_metric_only=True),
                lgb.log_evaluation(100),
            ],
        )

        p_va = model.predict_proba(X_va)[:, 1]
        # Pick the highest threshold that still catches at least 60% of late orders.
        prec, rec, thr = precision_recall_curve(y_va, p_va)
        ok = np.where(rec[:-1] >= 0.60)[0]
        threshold = float(thr[ok[-1]]) if len(ok) else 0.5

        val_m = metrics(y_va, p_va, threshold)
        test_m = metrics(y_te, model.predict_proba(X_te)[:, 1], threshold)
        mlflow.log_params({k: v for k, v in params.items() if k != "scale_pos_weight"})
        mlflow.log_param("threshold", threshold)
        mlflow.log_metrics({f"val_{k}": v for k, v in val_m.items()})
        mlflow.log_metrics({f"test_{k}": v for k, v in test_m.items()})
        print("LightGBM VALIDATION:", {k: round(float(v), 3) for k, v in val_m.items()})
        print(
            "LightGBM TEST      :", {k: round(float(v), 3) for k, v in test_m.items()}
        )

        version = datetime.now().strftime("%Y%m%d-%H%M")
        Path("models").mkdir(exist_ok=True)
        joblib.dump(
            {
                "model": model,
                "features": FEATURES,
                "categories": categories,
                "threshold": threshold,
                "seller_stats": seller_stats,
                "prior": float(prior),
                "version": version,
            },
            "models/delay_model.joblib",
        )
        mlflow.log_artifact("models/delay_model.joblib")


if __name__ == "__main__":
    main()
