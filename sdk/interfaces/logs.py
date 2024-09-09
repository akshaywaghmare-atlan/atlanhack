from typing import Type

from sqlalchemy.orm import Session

from sdk.models import Log
from opentelemetry.proto.logs.v1.logs_pb2 import LogsData


class Logs:
    @staticmethod
    def get_log(db: Session, event_id: int) -> Type[Log]:
        return db.query(Log).filter(Log.id == event_id).first()

    @staticmethod
    def get_logs(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Log]]:
        return db.query(Log).offset(skip).limit(limit).all()

    @staticmethod
    def create_logs(db: Session, logs_data: LogsData) -> list[Type[Log]]:
        logs = []
        for resource_log in logs_data.resource_logs:
            resource_attributes = {}
            for resource_attribute in resource_log.resource.attributes:
                resource_attributes[resource_attribute.key] = resource_attribute.value

            for scope_log in resource_log.scope_logs:
                for log in scope_log.log_records:
                    db_log = Log(
                        resource_attributes=log.resource.attributes,
                        scope_name=scope_log.name,
                        serverity=log.severity_text,
                        serverity_number=log.severity_number.real,
                        observed_timestamp=log.time_unix_nano,
                        body=log.body,
                        trace_id=log.trace_id,
                        span_id=log.span_id
                    )
                    db.add(db_log)
                    logs.append(db_log)
        db.commit()

        for log in logs:
            db.refresh(log)
        return logs
