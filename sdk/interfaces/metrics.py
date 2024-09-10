from typing import Type, List

from google.protobuf.json_format import MessageToJson, MessageToDict
from sqlalchemy.orm import Session

from sdk.models import Metric
from opentelemetry.proto.metrics.v1.metrics_pb2 import MetricsData

class Metrics:
    @staticmethod
    def get_metric(db: Session, metric_id: int) -> Type[Metric]:
        return db.query(Metric).filter(Metric.id == metric_id).first()

    @staticmethod
    def get_metrics(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Metric]]:
        return db.query(Metric).offset(skip).limit(limit).all()

    @staticmethod
    def create_metrics(db: Session, metrics_data: MetricsData) -> List[Metric]:
        metrics = []
        for resource_metric in metrics_data.resource_metrics:
            resource_attributes = {}
            for resource_attribute in resource_metric.resource.attributes:
                resource_attributes[resource_attribute.key] = resource_attribute.value.string_value

            for scope_metric in resource_metric.scope_metrics:
                for metric in scope_metric.metrics:
                    data_points = {}
                    for data_point in metric.gauge.data_points:
                        data_points['gauge'] = MessageToDict(data_point)

                    for data_point in metric.sum.data_points:
                        data_points['sum'] = MessageToDict(data_point)

                    for data_point in metric.histogram.data_points:
                        data_points['histogram'] = MessageToDict(data_point)

                    db_metric = Metric(
                        resource_attributes=resource_attributes,
                        scope_name=scope_metric.scope.name,
                        name=metric.name,
                        description=metric.description,
                        unit=metric.unit,
                        data_points=data_points
                    )
                    db.add(db_metric)
                    metrics.append(db_metric)

        db.commit()
        for metric in metrics:
            db.refresh(metric)
        return metrics