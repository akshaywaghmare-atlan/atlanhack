import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.interfaces.workflow import Workflow
from app.models.response import BaseResponse
from app.models.workflow import WorkflowRequestPayload

from fastapi import APIRouter

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
    responses={404: {"description": "Not found"}},
)

@router.post("/start", response_model=BaseResponse)
async def start_workflow(payload: WorkflowRequestPayload):
    try:
        workflow_details = await Workflow.run(payload)
        return BaseResponse(
            success=True,
            message="Workflow started",
            data=workflow_details
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Failed to start workflow",
                "error": str(e)
            }
        )
