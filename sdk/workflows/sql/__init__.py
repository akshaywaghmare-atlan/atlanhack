import logging

from sdk.workflows import WorkflowBuilderInterface, WorkflowMetadataInterface, \
    WorkflowPreflightCheckInterface, WorkflowAuthInterface
from abc import ABC, abstractmethod
from typing import Dict, Any

from sdk.workflows.sql.auth import SQLWorkflowAuthInterface
from sdk.workflows.sql.metadata import SQLWorkflowMetadataInterface

logger = logging.getLogger(__name__)


class SQLWorkflowBuilderInterface(WorkflowBuilderInterface, ABC):
    @abstractmethod
    def get_sqlalchemy_connection_string(self, credentials: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get_sqlalchemy_connect_args(
            self, credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass

    def __init__(self,
                 auth_interface: WorkflowAuthInterface = None,
                 metadata_interface: WorkflowMetadataInterface = None,
                 preflight_check_interface: WorkflowPreflightCheckInterface = None
                 ):
        if not auth_interface:
            auth_interface = SQLWorkflowAuthInterface(
                self.get_sqlalchemy_connection_string,
                self.get_sqlalchemy_connect_args,
            )

        if not metadata_interface:
            metadata_interface = SQLWorkflowMetadataInterface(
                self.get_sqlalchemy_connection_string,
                self.get_sqlalchemy_connect_args,
            )

        if not preflight_check_interface:
            preflight_check_interface = SQLWorkflowMetadataInterface(
                self.get_sqlalchemy_connection_string,
                self.get_sqlalchemy_connect_args,
            )

        super().__init__(auth_interface, metadata_interface, preflight_check_interface)