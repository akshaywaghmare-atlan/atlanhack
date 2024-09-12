from fastapi import FastAPI, APIRouter, HTTPException
from abc import ABC, abstractmethod

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from sdk import models
from sdk.database import get_engine
from sdk.fastapi.routers import events, logs, metrics, traces, health
from sdk.workflows import WorkflowBuilderInterface


class AtlanApplicationBuilder(ABC):

    def __init__(self, workflow_builder_interface: WorkflowBuilderInterface = None):
        self.workflow_builder_interface = workflow_builder_interface

    @abstractmethod
    def add_telemetry_routes(self):
        raise NotImplementedError

    @abstractmethod
    def add_event_routes(self):
        raise NotImplementedError

    def on_api_service_start(self) -> None:
        models.Base.metadata.create_all(bind=get_engine())

    @staticmethod
    def on_api_service_stop() -> None:
        models.Base.metadata.drop_all(bind=get_engine())

    @abstractmethod
    def add_workflows_router(self):
        raise NotImplementedError


class FastAPIApplicationBuilder(AtlanApplicationBuilder):
    workflows_router = APIRouter(
        prefix="/workflows",
        tags=["workflows"],
        responses={404: {"description": "Not found"}},
    )

    def __init__(self, app: FastAPI, workflow_builder_interface: WorkflowBuilderInterface=None):
        self.app = app
        self.app.include_router(health.router)
        super().__init__(workflow_builder_interface)

    def add_telemetry_routes(self) -> None:
        self.app.include_router(logs.router)
        self.app.include_router(metrics.router)
        self.app.include_router(traces.router)

    def add_event_routes(self) -> None:
        self.app.include_router(events.router)

    def on_api_service_start(self) -> None:
        super().on_api_service_start()
        FastAPIInstrumentor.instrument_app(self.app)

    async def test_auth(self, credential: dict):
        if not self.workflow_builder_interface or not self.workflow_builder_interface.auth_interface:
            raise HTTPException(status_code=500, detail="Auth interface not implemented")
        try:
            return self.workflow_builder_interface.auth_interface.test_auth(credential)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def fetch_metadata(self, credential: dict):
        if not self.workflow_builder_interface or not self.workflow_builder_interface.metadata_interface:
            raise HTTPException(status_code=500, detail="Metadata interface not implemented")
        try:
            return {
                'rows': self.workflow_builder_interface.metadata_interface.fetch_metadata(credential)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def add_workflows_router(self):
        self.workflows_router.add_api_route(
            path="/test-auth",
            endpoint=self.test_auth,
            methods=["POST"],
            response_model=bool,
        )

        self.workflows_router.add_api_route(
            path="/fetch-metadata",
            endpoint=self.fetch_metadata,
            methods=["POST"],
            response_model=dict,
        )

        self.app.include_router(self.workflows_router)
