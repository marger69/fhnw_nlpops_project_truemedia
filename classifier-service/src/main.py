"""Application entry point for the classifier service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app
from pydantic import BaseModel, field_validator

from src import config
from src.classifier import Classifier
from src.metrics import ServiceMetrics
from src.microbatch import MicroBatcher

classifier = Classifier()
metrics = ServiceMetrics()
batcher = MicroBatcher(
    lambda comments: classifier.classify_batch(comments),
    config.BATCH_WINDOW_MS,
    config.MAX_BATCH_SIZE,
    metrics,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    batcher.start()
    yield
    await batcher.stop()


app = FastAPI(title="Comment Classifier", lifespan=lifespan)
app.mount("/metrics", make_asgi_app(registry=metrics.registry))


class ClassifyRequest(BaseModel):
    comment: str

    @field_validator("comment")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("comment must not be empty")
        return value


class ClassifyResponse(BaseModel):
    comment: str
    label: str
    score: float


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
async def classify(request: ClassifyRequest) -> ClassifyResponse:
    label, score = await batcher.submit(request.comment)
    return ClassifyResponse(comment=request.comment, label=label, score=score)
