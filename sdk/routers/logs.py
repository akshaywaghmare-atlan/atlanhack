from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sdk.database import SessionLocal
from sdk.schemas import Log, LogCreate
from sdk.interfaces.logs import Logs


router = APIRouter(
    prefix="/v1/logs",
    tags=["logs"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[Log])
async def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Logs.get_logs(db, skip, limit)


@router.post("/", response_model=Log)
async def create_item(log: LogCreate, db: Session = Depends(get_db)):
    return Logs.create_log(db, log)