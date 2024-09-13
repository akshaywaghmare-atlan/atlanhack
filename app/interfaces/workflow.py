from typing import Dict, Any
import uuid

from temporalio import activity, workflow
from temporalio.client import Client, WorkflowFailureError, WorkflowHandle
import logging
from sdk.interfaces.platform import Platform
from app.workflow.workflow import ExtractionWorkflow
from app.dto.workflow import WorkflowConfig, WorkflowRequestPayload

from app.const import METADATA_EXTRACTION_TASK_QUEUE
from sdk.logging import get_logger

logger = get_logger(__name__)


class Workflow:
    @staticmethod
    async def run(payload: WorkflowRequestPayload) -> Dict[str, Any]:
        client: Client = await Client.connect("localhost:7233")
        workflow_id = str(uuid.uuid4())
        credential_config = payload.credentials.get_credential_config()
        credential_guid = Platform.store_credentials(credential_config)

        workflow.logger.setLevel(logging.DEBUG)
        activity.logger.setLevel(logging.DEBUG)

        config = WorkflowConfig(
            workflowId=workflow_id,
            credentialsGUID=credential_guid,
            includeFilterStr=payload.metadata.include_filter,
            excludeFilterStr=payload.metadata.exclude_filter,
            tempTableRegexStr=payload.metadata.temp_table_regex,
            outputType="JSON",
            outputPrefix="/tmp/output",
            verbose=True,
        )

        try:
            handle: WorkflowHandle[Any, Any] = await client.start_workflow(  # pyright: ignore[reportUnknownMemberType]
                ExtractionWorkflow.run,
                config,
                id=workflow_id,
                task_queue=METADATA_EXTRACTION_TASK_QUEUE,
            )
            logger.info(f"Workflow started: {handle.id} {handle.result_run_id}")
            return {
                "message": "Workflow started",
                "workflow_id": handle.id,
                "run_id": handle.result_run_id,
            }

        except WorkflowFailureError as e:
            logger.error(f"Workflow failure: {e}")
            raise e

    @staticmethod
    def schedule():
        pass
