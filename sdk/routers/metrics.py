from typing import List

from fastapi import APIRouter, Depends, Request
from opentelemetry.proto.metrics.v1.metrics_pb2 import MetricsData
from sqlalchemy.orm import Session

from sdk.database import SessionLocal
from sdk.schemas import Metric, MetricCreate
from sdk.interfaces.metrics import Metrics


router = APIRouter(
    prefix="/telemetry/v1/metrics",
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[Metric])
async def read_metrics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Metrics.get_metrics(db, skip, limit)


@router.post("")
async def create_metrics(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    metric_message = MetricsData()
    metric_message.ParseFromString(body)
    Metrics.create_metrics(db, metric_message)