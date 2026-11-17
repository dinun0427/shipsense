from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import OrderFact, Prediction, ReviewAnalysis
from app.db.session import get_db
from app.schemas.api import DelayRequest, DelayResponse, ReviewRequest, ReviewResponse

router = APIRouter()


@router.post("/predict-delay", response_model=DelayResponse)
def predict_delay(req: DelayRequest, request: Request, db: Session = Depends(get_db)):
    result = request.app.state.delay.predict(req)
    db.add(
        Prediction(
            input_json=req.model_dump(mode="json"),
            late_probability=result["late_probability"],
            risk_label=result["risk_label"],
            top_factors_json=result["top_factors"],
            model_version=result["model_version"],
        )
    )
    db.commit()
    return result


@router.post("/analyze-review", response_model=ReviewResponse)
def analyze_review(req: ReviewRequest, request: Request, db: Session = Depends(get_db)):
    result = request.app.state.sentiment.predict(req.text)
    db.add(ReviewAnalysis(text=req.text, **result))
    db.commit()
    return result


@router.get("/insights/late-rate")
def late_rate(by: str = "state", db: Session = Depends(get_db)):
    col = OrderFact.customer_state if by == "state" else OrderFact.purchase_month
    q = (
        select(
            col.label("key"),
            func.avg(OrderFact.is_late).label("late_rate"),
            func.count().label("orders"),
        )
        .group_by(col)
        .order_by(col)
    )
    return [
        {"key": str(r.key), "late_rate": float(r.late_rate), "orders": r.orders}
        for r in db.execute(q)
    ]


@router.get("/insights/sentiment")
def sentiment_trend(db: Session = Depends(get_db)):
    q = (
        select(
            OrderFact.purchase_month.label("month"),
            func.avg(OrderFact.review_score).label("avg_score"),
            func.count(OrderFact.review_score).label("reviews"),
        )
        .group_by(OrderFact.purchase_month)
        .order_by(OrderFact.purchase_month)
    )
    return [
        {
            "month": str(r.month),
            "avg_score": float(r.avg_score or 0),
            "reviews": r.reviews,
        }
        for r in db.execute(q)
    ]


@router.get("/predictions")
def recent_predictions(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Prediction).order_by(Prediction.id.desc()).limit(min(limit, 100))
    )
    return [
        {
            "id": p.id,
            "created_at": p.created_at,
            "late_probability": p.late_probability,
            "risk_label": p.risk_label,
            "model_version": p.model_version,
        }
        for p in rows
    ]
