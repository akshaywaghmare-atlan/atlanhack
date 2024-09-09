from datetime import datetime
from typing import Type

from sqlalchemy.orm import Session

from sdk.models import Trace
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData

class Traces:
    @staticmethod
    def get_trace(db: Session, trace_id: int) -> Type[Trace]:
        return db.query(Trace).filter(Trace.id == trace_id).first()

    @staticmethod
    def get_traces(db: Session, skip: int = 0, limit: int = 100) -> list[Type[Trace]]:
        return db.query(Trace).offset(skip).limit(limit).all()

    @staticmethod
    def create_traces(db: Session, traces_data: TracesData) -> list[Type[Trace]]:
        traces = []
        for resource_span in traces_data.resource_spans:
            resource_attributes = {}
            for resource_attribute in resource_span.resource.attributes:
                resource_attributes[resource_attribute.key] = resource_attribute.value.string_value

            for scope_span in resource_span.scope_spans:
                for span in scope_span.spans:
                    attributes = {}
                    for attribute in span.attributes:
                        attributes[attribute.key] = attribute.value.string_value

                    events = []
                    for event in span.events:
                        event_data = {
                            "name": event.name,
                            "timestamp_unix_nano": event.time_unix_nano
                        }
                        event_attributes = {}
                        for attribute in event.attributes:
                            event_attributes[attribute.key] = attribute.value.string_value
                        event_data["attributes"] = event_attributes
                        events.append(event_data)

                    db_trace = Trace(
                        resource_attributes=resource_attributes,
                        name=span.name,
                        start_time=datetime.utcfromtimestamp(span.start_time_unix_nano // 1000000000),
                        end_time=datetime.utcfromtimestamp(span.end_time_unix_nano // 1000000000),
                        trace_id=span.trace_id.hex(),
                        span_id=span.span_id.hex(),
                        parent_span_id=span.parent_span_id.hex(),
                        kind=span.kind.real,
                        attributes=attributes,
                        events=events
                    )
                    db.add(db_trace)
                    traces.append(db_trace)
        db.commit()

        for trace in traces:
            db.refresh(trace)
        return traces
