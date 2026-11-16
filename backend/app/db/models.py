from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    input_json: Mapped[dict] = mapped_column(JSON)
    late_probability: Mapped[float] = mapped_column(Float)
    risk_label: Mapped[str] = mapped_column(String(10))
    top_factors_json: Mapped[list] = mapped_column(JSON)
    model_version: Mapped[str] = mapped_column(String(40))


class ReviewAnalysis(Base):
    __tablename__ = "review_analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    text: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[str] = mapped_column(String(10))
    confidence: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(40))


class OrderFact(Base):
    __tablename__ = "order_facts"
    order_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    purchase_month: Mapped[date] = mapped_column(Date, index=True)
    customer_state: Mapped[str] = mapped_column(String(2), index=True)
    seller_id: Mapped[str] = mapped_column(String(40), index=True)
    is_late: Mapped[int] = mapped_column(Integer)
    review_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
