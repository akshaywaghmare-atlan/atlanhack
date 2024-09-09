from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from google.protobuf.json_format import MessageToDict
from urllib3 import request

from sdk.database import SessionLocal
from sdk.schemas import Trace
from sdk.interfaces.traces import Traces
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData


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


@router.get("", response_model=list[Trace])
async def read_traces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Traces.get_traces(db, skip, limit)


@router.post("", response_model=List[Trace])
async def create_trace(trace: Request, db: Session = Depends(get_db)):
    # Convert the request body to a protobuf message
    body = await trace.body()
    trace_message = TracesData()
    trace_message.ParseFromString(body)
    traces = Traces.create_traces(db, trace_message)
    return traces