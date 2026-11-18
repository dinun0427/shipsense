import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models  # noqa: F401
from app.db.session import Base, get_db
from app.main import app


class FakeDelay:
    def predict(self, req):
        return {
            "late_probability": 0.42,
            "risk_label": "medium",
            "model_version": "test",
            "top_factors": [
                {
                    "feature": "distance_km",
                    "contribution": 0.5,
                    "direction": "increases risk",
                }
            ],
        }


class FakeSentiment:
    def predict(self, text):
        return {"sentiment": "negative", "confidence": 0.9, "model_version": "test"}


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.state.delay = FakeDelay()
    app.state.sentiment = FakeSentiment()
    yield TestClient(app)
    app.dependency_overrides.clear()
