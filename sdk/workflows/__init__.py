from abc import ABC, abstractmethod
from typing import Dict, Any


class WorkflowBuilderInterface(ABC):
    @abstractmethod
    def test_auth(self, credential: Dict[str, Any]):
        pass
