from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sdk.database import SessionLocal
from sdk.schemas import Event, EventCreate
from sdk.interfaces.events import Events


router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[Event])
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return Events.get_events(db)


@router.get("/{event_id}", response_model=Event)
async def read_item(event_id: int, db: Session = Depends(get_db)):
    db_event = Events.get_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@router.post("/", response_model=EventCreate)
async def create_item(event: EventCreate, db: Session = Depends(get_db)):
    return Events.create_event(db, event)