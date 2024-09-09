from abc import ABC, abstractmethod
from typing import Optional
from app.models.credentials import CredentialConfig


class PlatformInterface(ABC):
    @abstractmethod
    def store_credentials(self, guid: str, config: CredentialConfig) -> str:
        pass

    @abstractmethod
    def extract_credentials(self, guid: str) -> Optional[CredentialConfig]:
        pass

    @abstractmethod
    def push_to_object_store(self, output_config: dict) -> None:
        pass

