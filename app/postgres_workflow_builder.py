from typing import Dict, Any, List
from app.const import METADATA_EXTRACTION_TASK_QUEUE
from app.dto.credentials import CredentialPayload
from app.dto.preflight import PreflightPayload
from app.interfaces.preflight import Preflight
from app.workflow.activities import ExtractionActivities
from app.workflow.workflow import ExtractionWorkflow
from sdk.workflows.sql import SQLWorkflowBuilderInterface, SQLWorkflowMetadataInterface

from sdk.workflows.sql.preflight_check import SQLWorkflowPreflightCheckInterface
from sdk.workflows.sql.worker import SQLWorkflowWorkerInterface


class PostgresWorkflowMetadata(SQLWorkflowMetadataInterface):
    METADATA_SQL = """
        SELECT
            CATALOG_NAME as DATABASE_NAME,
            SCHEMA_NAME as SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
    """

    def fetch_metadata(self, credential: Dict[str, Any]) -> List[Dict[str, Any]]:
        basic_credentials = CredentialPayload(**credential).get_credential_config()
        return Preflight.fetch_metadata(basic_credentials)


class PostgresWorkflowPreflight(SQLWorkflowPreflightCheckInterface):
    METADATA_SQL = """
        SELECT
            CATALOG_NAME as DATABASE_NAME,
            SCHEMA_NAME as SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
    """

    def preflight_check(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        # credential, form_data = form_data.get("credential"), form_data.get("formData")
        return Preflight.check(PreflightPayload(**form_data))


class PostgresWorkflowWorker(SQLWorkflowWorkerInterface):
    QUEUE_NAME = METADATA_EXTRACTION_TASK_QUEUE
    WORKFLOWS = [ExtractionWorkflow]
    ACTIVITIES = [
        ExtractionActivities.create_output_directory,
        ExtractionActivities.extract_metadata,
        ExtractionActivities.push_results_to_object_store,
    ]
    PASSTHROUGH_MODULES = ["sdk"]


class PostgresWorkflowBuilder(SQLWorkflowBuilderInterface):
    def get_sqlalchemy_connection_string(self, credentials: Dict[str, Any]) -> str:
        return f"postgresql+psycopg2://{credentials['username']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/{credentials['database']}"

    def get_sqlalchemy_connect_args(
        self, credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {}

    def __init__(self):
        # Preflight check
        preflight_check = PostgresWorkflowPreflight(
            self.get_sqlalchemy_connection_string,
            self.get_sqlalchemy_connect_args,
        )

        # Metadata interface
        metadata_interface = PostgresWorkflowMetadata(
            self.get_sqlalchemy_connection_string,
            self.get_sqlalchemy_connect_args,
        )

        # Worker interface
        worker_interface = PostgresWorkflowWorker(
            self.get_sqlalchemy_connection_string,
            self.get_sqlalchemy_connect_args,
        )

        super().__init__(
            metadata_interface=metadata_interface,
            preflight_check_interface=preflight_check,
            worker_interface=worker_interface,
        )
