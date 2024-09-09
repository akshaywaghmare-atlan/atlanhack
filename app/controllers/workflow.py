import uuid
from temporalio.client import Client, WorkflowFailureError
import logging
from fastapi import APIRouter

from app.platform import get_platform
from app.workflow.workflow import ExtractionWorkflow
from app.models.workflow import WorkflowConfig, WorkflowRequestPayload
from app.const import TABLE_COMPANION_SQL, COLUMN_COMPANION_SQL, EXTRA_COMPANION_SQL

from fastapi import APIRouter
from app.const import METADATA_EXTRACTION_TASK_QUEUE

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
    responses={404: {"description": "Not found"}},
)


@router.post("/start", response_model=dict)
async def start_workflow(payload: WorkflowRequestPayload):
    client = await Client.connect("localhost:7233")

    workflow_id = str(uuid.uuid4())
    platform = get_platform()
    credential_config = payload.credentials.get_credential_config()
    credential_guid = platform.store_credentials(credential_config)

    config = WorkflowConfig(
        workflowId=workflow_id,
        credentialsGUID=credential_guid,
        includeFilterStr=payload.metadata.include_filter,
        excludeFilterStr=payload.metadata.exclude_filter,
        outputType="json",
        outputPrefix="/tmp/output",
        verbose=True,
        useSourceSchemaFiltering=True,
        tableCompanionSQL=TABLE_COMPANION_SQL,
        columnCompanionSQL=COLUMN_COMPANION_SQL,
        extraCompanionSQLs=EXTRA_COMPANION_SQL,
    )

    try:
        handle = await client.start_workflow(
            ExtractionWorkflow.extract_metadata,
            config,
            id=workflow_id,
            task_queue=METADATA_EXTRACTION_TASK_QUEUE
        )
        logger.info(f"Workflow started: {handle.id}")
    except WorkflowFailureError as e:
        logger.error(f"Workflow failure: {e}")
        raise e

    return {"message": "Workflow started", "workflow_id": handle.id}