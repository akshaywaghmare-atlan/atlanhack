from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/", response_model=list[Metric])
async def read_metrics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Metrics.get_metrics(db, skip, limit)


@router.post("/", response_model=Metric)
async def create_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    return Metrics.create_metric(db, metric)