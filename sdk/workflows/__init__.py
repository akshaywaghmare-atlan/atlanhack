from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Dict, Any


class WorkflowAuthInterface(ABC):
    def __init__(self, get_sql_alchemy_string_fn: Callable[[Dict[str, Any]], str],
                    get_sql_alchemy_connect_args_fn: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.get_sql_alchemy_string_fn = get_sql_alchemy_string_fn
        self.get_sql_alchemy_connect_args_fn = get_sql_alchemy_connect_args_fn

    @abstractmethod
    def test_auth(self, credential: Dict[str, Any]) -> bool:
        raise NotImplementedError


class WorkflowFetchMetadataInterface(ABC):
    @abstractmethod
    def fetch_metadata(self, credential: Dict[str, Any]):
        raise NotImplementedError


class WorkflowPreflightCheckInterface(ABC):
    @abstractmethod
    def preflight_check(self, credential: Dict[str, Any]):
        raise NotImplementedError


class WorkflowBuilderInterface(ABC):
    def __init__(self,
                 auth_interface: WorkflowAuthInterface=None,
                 fetch_metadata_interface: WorkflowFetchMetadataInterface=None,
                 preflight_check_interface: WorkflowPreflightCheckInterface=None
                 ):
        self.auth_interface = auth_interface
        self.fetch_metadata_interface = fetch_metadata_interface
        self.preflight_check_interface = preflight_check_interface
