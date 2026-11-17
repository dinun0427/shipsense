from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.services.predictor import DelayPredictor, SentimentModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    d = Path(settings.model_dir)
    app.state.delay = DelayPredictor(d / "delay_model.joblib")
    app.state.sentiment = SentimentModel(d / "sentiment_model.joblib")
    yield


app = FastAPI(title="ShipSense API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
