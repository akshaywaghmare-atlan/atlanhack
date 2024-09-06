from typing import Type

from sqlalchemy.orm import Session

from sdk.models import Event
from sdk.schemas import EventCreate

class Events:
    @staticmethod
    def get_event(db: Session, event_id: int) -> Type[Event]:
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_events(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Event]]:
        return db.query(Event).offset(skip).limit(limit).all()

    @staticmethod
    def create_event(db: Session, event: EventCreate) -> Event:
        db_event = Event(name=event.name, event_type=event.event_type, status=event.status,
                         application_name=event.application_name, attributes=event.attributes,
                         observed_timestamp=event.observed_timestamp)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
