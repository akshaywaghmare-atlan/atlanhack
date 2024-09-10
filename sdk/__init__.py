from fastapi import FastAPI
from abc import ABC, abstractmethod

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from sdk import models
from sdk.database import get_engine
from sdk.fastapi.routers import events, logs, metrics, traces


class AtlanApplicationBuilder(ABC):
    @abstractmethod
    def add_telemetry_routes(self):
        pass

    @abstractmethod
    def add_event_routes(self):
        pass

    @staticmethod
    def on_api_service_start() -> None:
        models.Base.metadata.create_all(bind=get_engine())

    @staticmethod
    def on_api_service_stop() -> None:
        models.Base.metadata.drop_all(bind=get_engine())


class FastAPIApplicationBuilder(AtlanApplicationBuilder):
    def __init__(self, app: FastAPI):
        self.app = app

    def add_telemetry_routes(self) -> None:
        self.app.include_router(logs.router)
        self.app.include_router(metrics.router)
        self.app.include_router(traces.router)

    def add_event_routes(self) -> None:
        self.app.include_router(events.router)

    def on_api_service_start(self) -> None:
        super().on_api_service_start()
        FastAPIInstrumentor.instrument_app(self.app)

