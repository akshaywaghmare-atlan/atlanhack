from datetime import datetime

from pydantic import BaseModel


class EventBase(BaseModel):
    name: str
    event_type: str
    status: str
    application_name: str
    attributes: str
    observed_timestamp: datetime


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
