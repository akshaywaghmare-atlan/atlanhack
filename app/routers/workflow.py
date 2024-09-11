import logging
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from app.interfaces.workflow import Workflow
from app.dto.response import BaseResponse
from app.dto.workflow import WorkflowRequestPayload

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
            success=True, message="Workflow started", data=workflow_details
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Failed to start workflow",
                "error": str(e),
            },
        )
