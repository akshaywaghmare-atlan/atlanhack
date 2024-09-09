from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sdk.database import SessionLocal
from sdk.schemas import Trace, TraceCreate
from sdk.interfaces.traces import Traces


router = APIRouter(
    prefix="/telemetry/v1/traces",
    tags=["traces"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[Trace])
async def read_traces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Traces.get_traces(db, skip, limit)


@router.post("/", response_model=Trace)
async def create_trace(trace: TraceCreate, db: Session = Depends(get_db)):
    return Traces.create_trace(db, trace)