from fastapi import APIRouter, HTTPException
from app.common.utils import connect_to_db
from app.interfaces.preflight import Preflight
from app.models.credentials import CredentialPayload

from app.models.preflight import PreflightPayload

router = APIRouter(
    prefix="/preflight",
    tags=["preflight"],
    responses={404: {"description": "Not found"}},
)

@router.post("/test-authentication")
async def test_authentication(payload: CredentialPayload):
    try:
        result = Preflight.test_authentication(payload.get_credential_config())
        return {
            "success": True,
            "results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": "An unexpected error occurred during authentication test.",
            "message": str(e),
            "errorCode": "INTERNAL_SERVER_ERROR"
        })

@router.post("/fetch-metadata")
async def fetch_metatdata(payload: CredentialPayload):
    try:
        result = Preflight.fetch_metadata(payload.get_credential_config())
        return {
            "success": True,
            "results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": "An unexpected error occurred while fetching metadata.",
            "message": str(e),
            "errorCode": "INTERNAL_SERVER_ERROR"
        })


@router.post("/check")
async def check(payload: PreflightPayload):
    try:
        result = Preflight.check(payload)
        return {
            "success": True,
            "results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "errorCode": "INTERNAL_SERVER_ERROR"
        })