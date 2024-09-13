import time
from datetime import datetime
from typing import List, Optional, Sequence, Type

from google.protobuf.json_format import MessageToDict
from sqlalchemy.orm import Session

from sdk.models import Metric
from opentelemetry.proto.metrics.v1.metrics_pb2 import MetricsData


class Metrics:
    @staticmethod
    def get_metric(session: Session, metric_id: int) -> Optional[Metric]:
        return session.query(Metric).filter(Metric.id == metric_id).first()

    @staticmethod
    def get_metrics(
        session: Session, from_timestamp: int = 0, to_timestamp: Optional[int] = None
    ) -> list[Type[Metric]]:
        if to_timestamp is None:
            to_timestamp = int(time.time())
        return (
            session.query(Metric)
            .filter(
                Metric.observed_timestamp >= datetime.fromtimestamp(from_timestamp),
                Metric.observed_timestamp <= datetime.fromtimestamp(to_timestamp),
            )
            .all()
        )

    @staticmethod
    def create_metrics(session: Session, metrics_data: MetricsData) -> List[Metric]:
        metrics: List[Metric] = []
        for resource_metric in metrics_data.resource_metrics:
            resource_attributes = {}
            for resource_attribute in resource_metric.resource.attributes:
                resource_attributes[resource_attribute.key] = (
                    resource_attribute.value.string_value
                )

            for scope_metric in resource_metric.scope_metrics:
                for metric in scope_metric.metrics:
                    data_points = {}
                    for data_point in metric.gauge.data_points:
                        data_points["gauge"] = MessageToDict(data_point)

                    for data_point in metric.sum.data_points:
                        data_points["sum"] = MessageToDict(data_point)

                    for data_point in metric.histogram.data_points:
                        data_points["histogram"] = MessageToDict(data_point)

                    db_metric = Metric(
                        resource_attributes=resource_attributes,
                        scope_name=scope_metric.scope.name,
                        name=metric.name,
                        description=metric.description,
                        unit=metric.unit,
                        data_points=data_points,
                    )
                    session.add(db_metric)
                    metrics.append(db_metric)

        session.commit()
        for metric in metrics:
            session.refresh(metric)
        return metrics
