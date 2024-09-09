import uuid
from dapr.clients import DaprClient
from typing import Optional
from app.models.credentials import CredentialConfig
from app.const import STATE_STORE_NAME, OBJECT_STORE_NAME, OBJECT_CREATE_OPERATION
import os
import logging
from app.platform.interface import PlatformInterface

logger = logging.getLogger(__name__)

# FIXME: Make dapr platform available to workflow activities by dependency injection
class DaprPlatform(PlatformInterface):
    def __init__(self):
        self.client = DaprClient()

    def store_credentials(self, config: CredentialConfig) -> str:
        """
        Store credentials in the state store using the credentialConfig format.
        
        :param guid: The unique identifier for the credentials.
        :param config: The CredentialConfig object containing the credentials.
        """
        try:
            credential_guid = f"credential_{str(uuid.uuid4())}"
            self.client.save_state(
                store_name=STATE_STORE_NAME,
                key=credential_guid,
                value=config.model_dump_json()
            )
            return credential_guid
        except Exception as e:
            raise Exception(f"Failed to store credentials: {str(e)}")

    def extract_credentials(self, credential_guid: str) -> Optional[CredentialConfig]:
        """
        Extract credentials from the state store using the credential GUID.
        
        :param credential_guid: The unique identifier for the credentials.
        :return: CredentialConfig object if found, None otherwise.
        """
        try:
            state = self.client.get_state(
                store_name=STATE_STORE_NAME,
                key=credential_guid
            )
            if state.data:
                return CredentialConfig.model_validate_json(state.data)
            return None
        except Exception as e:
            raise Exception(f"Failed to extract credentials: {str(e)}")

    def push_to_object_store(self, output_config: dict) -> None:
        """
        Push files from a directory to the object store.

        :param output_config: The path to the directory containing files to push.
        """
        output_prefix = output_config["output_prefix"]
        output_path = output_config["output_path"]
        for root, _, files in os.walk(output_path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                relative_path = os.path.relpath(file_path, output_prefix)
                metadata = {
                    'key': relative_path,
                    'fileName': relative_path
                }
                
                self.client.invoke_binding(
                    binding_name=OBJECT_STORE_NAME,
                    operation=OBJECT_CREATE_OPERATION,
                    data=file_content,
                    binding_metadata=metadata
                )
                
        logger.info(f"Pushed data from {output_path} to object store")