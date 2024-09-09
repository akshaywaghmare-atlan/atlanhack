from typing import Type

from sqlalchemy.orm import Session

from sdk.models import Metric
from sdk.schemas import MetricCreate

class Metrics:
    @staticmethod
    def get_metric(db: Session, metric_id: int) -> Type[Metric]:
        return db.query(Metric).filter(Metric.id == metric_id).first()

    @staticmethod
    def get_metrics(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Metric]]:
        return db.query(Metric).offset(skip).limit(limit).all()

    @staticmethod
    def create_metric(db: Session, log: MetricCreate) -> Metric:
        db_metric = Metric(name=log.name, event_type=log.event_type, status=log.status,
                     application_name=log.application_name, attributes=log.attributes,
                     observed_timestamp=log.observed_timestamp)
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric