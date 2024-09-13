from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Dict, Any, Optional, Sequence
from temporalio.types import ClassType, CallableType
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import (
    SandboxedWorkflowRunner,
    SandboxRestrictions,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowAuthInterface(ABC):
    def __init__(
        self,
        get_sql_alchemy_string_fn: Callable[[Dict[str, Any]], str],
        get_sql_alchemy_connect_args_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ):
        self.get_sql_alchemy_string_fn = get_sql_alchemy_string_fn
        self.get_sql_alchemy_connect_args_fn = get_sql_alchemy_connect_args_fn

    @abstractmethod
    def test_auth(self, credential: Dict[str, Any]) -> bool:
        raise NotImplementedError


class WorkflowMetadataInterface(ABC):
    def __init__(
        self,
        get_sql_alchemy_string_fn: Callable[[Dict[str, Any]], str],
        get_sql_alchemy_connect_args_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ):
        self.get_sql_alchemy_string_fn = get_sql_alchemy_string_fn
        self.get_sql_alchemy_connect_args_fn = get_sql_alchemy_connect_args_fn

    @abstractmethod
    def fetch_metadata(self, credential: Dict[str, Any]):
        raise NotImplementedError


class WorkflowPreflightCheckInterface(ABC):
    def __init__(
        self,
        get_sql_alchemy_string_fn: Callable[[Dict[str, Any]], str],
        get_sql_alchemy_connect_args_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ):
        self.get_sql_alchemy_string_fn = get_sql_alchemy_string_fn
        self.get_sql_alchemy_connect_args_fn = get_sql_alchemy_connect_args_fn

    @abstractmethod
    def preflight_check(self, credential: Dict[str, Any]) -> bool:
        raise NotImplementedError


class WorkflowWorkerInterface(ABC):
    QUEUE_NAME: str = ""
    WORKFLOWS: Sequence[ClassType] = []
    ACTIVITIES: Sequence[CallableType] = []
    PASSTHROUGH_MODULES: Sequence[str] = []
    HOST: str = "localhost"
    PORT: str = "7233"
    NAMESPACE: str = "default"

    def __init__(
        self,
        get_sql_alchemy_string_fn: Callable,
        get_sql_alchemy_connect_args_fn: Callable,
    ):
        self.get_sql_alchemy_string_fn = get_sql_alchemy_string_fn
        self.get_sql_alchemy_connect_args_fn = get_sql_alchemy_connect_args_fn

    @abstractmethod
    async def run_workflow(self, workflow_args: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    async def run_worker(
        self,
    ) -> None:
        client = await Client.connect(
            f"{self.HOST}:{self.PORT}", namespace=self.NAMESPACE
        )

        worker = Worker(
            client,
            task_queue=self.QUEUE_NAME,
            workflows=self.WORKFLOWS,
            activities=self.ACTIVITIES,
            workflow_runner=SandboxedWorkflowRunner(
                restrictions=SandboxRestrictions.default.with_passthrough_modules(
                    *self.PASSTHROUGH_MODULES
                )
            ),
        )

        logger.info(f"Starting worker for queue: {self.QUEUE_NAME}")
        await worker.run()


class WorkflowBuilderInterface(ABC):
    def __init__(
        self,
        auth_interface: Optional[WorkflowAuthInterface] = None,
        metadata_interface: Optional[WorkflowMetadataInterface] = None,
        preflight_check_interface: Optional[WorkflowPreflightCheckInterface] = None,
        worker_interface: Optional[WorkflowWorkerInterface] = None,
    ):
        self.auth_interface = auth_interface
        self.metadata_interface = metadata_interface
        self.preflight_check_interface = preflight_check_interface
        self.worker_interface = worker_interface
