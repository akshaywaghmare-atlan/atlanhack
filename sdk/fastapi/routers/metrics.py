from typing import List

from fastapi import APIRouter, Depends, Request
from opentelemetry.proto.metrics.v1.metrics_pb2 import MetricsData
from sqlalchemy.orm import Session

from sdk.database import get_session
from sdk.schemas import Metric
from sdk.interfaces.metrics import Metrics

router = APIRouter(
    prefix="/telemetry/v1/metrics",
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=list[Metric])
async def read_metrics(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return Metrics.get_metrics(session, skip, limit)


@router.post("", response_model=List[Metric])
async def create_metrics(request: Request, session: Session = Depends(get_session)):
    body = await request.body()
    metric_message = MetricsData()
    metric_message.ParseFromString(body)
    return Metrics.create_metrics(session, metric_message)
