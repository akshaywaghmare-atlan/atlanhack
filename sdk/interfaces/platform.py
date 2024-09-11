import uuid
from dapr.clients import DaprClient
from sdk.dto.credentials import BasicCredential
from sdk.const import STATE_STORE_NAME, OBJECT_STORE_NAME, OBJECT_CREATE_OPERATION
import os
import logging

logger = logging.getLogger(__name__)


class Platform:
    @staticmethod
    def store_credentials(config: BasicCredential) -> str:
        """
        Store credentials in the state store using the BasicCredential format.

        :param config: The BasicCredential object containing the credentials.
        """
        try:
            client = DaprClient()
            credential_guid = f"credential_{str(uuid.uuid4())}"
            client.save_state(
                store_name=STATE_STORE_NAME,
                key=credential_guid,
                value=config.model_dump_json(),
            )
            return credential_guid
        except Exception as e:
            raise Exception(f"Failed to store credentials: {str(e)}")

    @staticmethod
    def extract_credentials(credential_guid: str) -> BasicCredential:
        """
        Extract credentials from the state store using the credential GUID.

        :param credential_guid: The unique identifier for the credentials.
        :return: BasicCredential object if found, None otherwise.
        """
        try:
            client = DaprClient()
            state = client.get_state(store_name=STATE_STORE_NAME, key=credential_guid)
            if state.data:
                return BasicCredential.model_validate_json(state.data)
            else:
                raise Exception(f"Credentials not found for GUID: {credential_guid}")
        except Exception as e:
            raise Exception(f"Failed to extract credentials: {str(e)}")

    @staticmethod
    def push_to_object_store(output_prefix: str, output_path: str) -> None:
        """
        Push files from a directory to the object store.

        :param output_config: The path to the directory containing files to push.
        """
        client = DaprClient()
        for root, _, files in os.walk(output_path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "rb") as f:
                    file_content = f.read()

                relative_path = os.path.relpath(file_path, output_prefix)
                metadata = {"key": relative_path, "fileName": relative_path}

                client.invoke_binding(
                    binding_name=OBJECT_STORE_NAME,
                    operation=OBJECT_CREATE_OPERATION,
                    data=file_content,
                    binding_metadata=metadata,
                )

        logger.info(f"Pushed data from {output_path} to object store")
