from datetime import datetime

from pydantic import BaseModel, Field


class DelayRequest(BaseModel):
    purchase_timestamp: datetime
    approved_timestamp: datetime
    estimated_delivery_date: datetime
    customer_state: str = Field(min_length=2, max_length=2)
    seller_state: str = Field(min_length=2, max_length=2)
    seller_id: str | None = None
    category: str = "unknown"
    n_items: int = Field(default=1, ge=1)
    n_sellers: int = Field(default=1, ge=1)
    price_sum: float = Field(gt=0)
    freight_sum: float = Field(ge=0)
    weight_g: float | None = Field(default=None, ge=0)
    volume_cm3: float | None = Field(default=None, ge=0)
    distance_km: float | None = Field(default=None, ge=0)


class Factor(BaseModel):
    feature: str
    contribution: float
    direction: str


class DelayResponse(BaseModel):
    late_probability: float
    risk_label: str
    top_factors: list[Factor]
    model_version: str


class ReviewRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ReviewResponse(BaseModel):
    sentiment: str
    confidence: float
    model_version: str
