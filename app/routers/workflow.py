import logging
from fastapi import APIRouter

from app.interfaces.workflow import Workflow
from app.models.workflow import WorkflowRequestPayload

from fastapi import APIRouter

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
    responses={404: {"description": "Not found"}},
)

@router.post("/start", response_model=dict)
async def start_workflow(payload: WorkflowRequestPayload):
    try:
        workflow_details = await Workflow.run(payload)
        return {
            "success": True,
            "message": "Workflow started",
            "details": workflow_details
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
