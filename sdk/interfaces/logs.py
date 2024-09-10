from datetime import datetime
from typing import Type

from sqlalchemy.orm import Session

from sdk.models import Log
from opentelemetry.proto.logs.v1.logs_pb2 import LogsData


class Logs:
    @staticmethod
    def get_log(db: Session, event_id: int) -> Type[Log]:
        return db.query(Log).filter(Log.id == event_id).first()

    @staticmethod
    def get_logs(db: Session, skip: int = 0, limit: int = 100, keyword: str = "") -> list[Type[Log]]:
        return db.query(Log).filter(Log.body.contains(keyword)).offset(skip).limit(limit).all()

    @staticmethod
    def create_logs(db: Session, logs_data: LogsData) -> list[Log]:
        logs = []
        for resource_log in logs_data.resource_logs:
            resource_attributes = {}
            for resource_attribute in resource_log.resource.attributes:
                resource_attributes[resource_attribute.key] = resource_attribute.value.string_value

            for scope_log in resource_log.scope_logs:
                for log in scope_log.log_records:
                    log_attributes = {}
                    for attribute in log.attributes:
                        log_attributes[attribute.key] = attribute.value.string_value

                    db_log = Log(
                        resource_attributes=resource_attributes,
                        scope_name=scope_log.scope.name,
                        severity=log.severity_text,
                        severity_number=log.severity_number.real,
                        observed_timestamp=datetime.utcfromtimestamp(log.observed_time_unix_nano // 1000000000),
                        timestamp=datetime.utcfromtimestamp(log.time_unix_nano // 1000000000),
                        body=log.body.string_value,
                        trace_id=log.trace_id.hex(),
                        span_id=log.span_id.hex(),
                        attributes=log_attributes
                    )
                    db.add(db_log)
                    logs.append(db_log)
        db.commit()

        for log in logs:
            db.refresh(log)
        return logs
