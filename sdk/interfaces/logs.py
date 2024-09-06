from typing import Type

from sqlalchemy.orm import Session

from sdk.models import Log
from sdk.schemas import LogCreate

class Logs:
    @staticmethod
    def get_log(db: Session, event_id: int) -> Type[Log]:
        return db.query(Log).filter(Log.id == event_id).first()

    @staticmethod
    def get_logs(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Log]]:
        return db.query(Log).offset(skip).limit(limit).all()

    @staticmethod
    def create_log(db: Session, log: LogCreate) -> Log:
        db_log = Log(name=log.name, event_type=log.event_type, status=log.status,
                     application_name=log.application_name, attributes=log.attributes,
                     observed_timestamp=log.observed_timestamp)
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

