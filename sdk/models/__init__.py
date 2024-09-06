from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from sdk.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    application_name = Column(String, nullable=False)
    attributes = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    observed_timestamp = Column(DateTime, nullable=False, default=datetime.now)
