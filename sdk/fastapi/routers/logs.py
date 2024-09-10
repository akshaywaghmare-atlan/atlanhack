from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from sdk.database import get_session
from sdk.schemas import Log
from sdk.interfaces.logs import Logs
from opentelemetry.proto.logs.v1.logs_pb2 import LogsData

router = APIRouter(
    prefix="/telemetry/v1/logs",
    tags=["logs"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=list[Log])
async def read_logs(skip: int = 0, limit: int = 100, keyword: str = "", session: Session = Depends(get_session)):
    return Logs.get_logs(session, skip, limit, keyword)


@router.post("", response_model=List[Log])
async def create_logs(request: Request, session: Session = Depends(get_session)):
    # Convert the request body to a protobuf message
    body = await request.body()
    log_message = LogsData()
    log_message.ParseFromString(body)
    return Logs.create_logs(session, log_message)
