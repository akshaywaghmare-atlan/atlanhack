from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.interfaces.preflight import Preflight
from app.dto.credentials import CredentialPayload

from app.dto.preflight import PreflightPayload
from app.dto.response import BaseResponse

router = APIRouter(
    prefix="/preflight",
    tags=["preflight"],
    responses={404: {"description": "Not found"}},
)


@router.post("/test-authentication", response_model=BaseResponse)
async def test_authentication(payload: CredentialPayload):
    try:
        result = Preflight.test_authentication(payload.get_credential_config())
        return BaseResponse(
            success=True, message="Authentication test successful", data=result
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Failed to test authentication",
                "error": str(e),
            },
        )


@router.post("/fetch-metadata", response_model=BaseResponse)
async def fetch_metatdata(payload: CredentialPayload):
    try:
        result = Preflight.fetch_metadata(payload.get_credential_config())
        return BaseResponse(
            success=True, message="Metadata fetched successfully", data=result
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Failed to fetch metadata",
                "error": str(e),
            },
        )


@router.post("/check", response_model=BaseResponse)
async def check(payload: PreflightPayload):
    try:
        result = Preflight.check(payload)
        return BaseResponse(
            success=True, message="Preflight check successful", data=result
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Preflight check failed",
                "error": str(e),
            },
        )
