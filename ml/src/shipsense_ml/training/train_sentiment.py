from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.pipeline import make_pipeline


def main():
    reviews = (
        pd.read_parquet("data/processed/reviews.parquet")
        .sort_values("review_creation_date")
        .reset_index(drop=True)
    )
    i1, i2 = int(len(reviews) * 0.70), int(len(reviews) * 0.85)
    train, val, test = reviews.iloc[:i1], reviews.iloc[i1:i2], reviews.iloc[i2:]
    print("rows:", len(train), len(val), len(test))

    pipe = make_pipeline(
        TfidfVectorizer(
            ngram_range=(1, 2), min_df=3, sublinear_tf=True, lowercase=True
        ),
        LogisticRegression(max_iter=2000, class_weight="balanced"),
    )

    mlflow.set_experiment("sentiment-model")
    with mlflow.start_run():
        pipe.fit(train.text, train.sentiment)
        val_f1 = f1_score(val.sentiment, pipe.predict(val.text), average="macro")
        test_f1 = f1_score(test.sentiment, pipe.predict(test.text), average="macro")
        mlflow.log_metrics({"val_macro_f1": val_f1, "test_macro_f1": test_f1})
        print("VALIDATION macro-F1:", round(float(val_f1), 3))
        print("TEST macro-F1      :", round(float(test_f1), 3))
        print()
        print(classification_report(test.sentiment, pipe.predict(test.text)))

        Path("models").mkdir(exist_ok=True)
        joblib.dump(
            {"pipeline": pipe, "version": "tfidf-lr-v1"},
            "models/sentiment_model.joblib",
        )


if __name__ == "__main__":
    main()
