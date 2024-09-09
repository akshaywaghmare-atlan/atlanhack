from typing import Type

from sqlalchemy.orm import Session

from sdk.models import Trace
from sdk.schemas import TraceCreate

class Traces:
    @staticmethod
    def get_trace(db: Session, trace_id: int) -> Type[Trace]:
        return db.query(Trace).filter(Trace.id == trace_id).first()

    @staticmethod
    def get_traces(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Trace]]:
        return db.query(Trace).offset(skip).limit(limit).all()

    @staticmethod
    def create_trace(db: Session, trace: TraceCreate) -> Trace:
        db_trace = Trace(name=trace.name, event_type=trace.event_type, status=trace.status,
                         application_name=trace.application_name, attributes=trace.attributes,
                         observed_timestamp=trace.observed_timestamp)
        db.add(db_trace)
        db.commit()
        db.refresh(db_trace)
        return db_trace

