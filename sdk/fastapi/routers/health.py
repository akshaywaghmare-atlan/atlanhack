from fastapi import APIRouter

router = APIRouter(
    prefix="/system",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    return {"status": "ok"}
