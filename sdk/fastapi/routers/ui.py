from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import APIRouter

router = APIRouter(
    prefix="",
    tags=["ui"],
    responses={404: {"description": "Not found"}},
)

router.mount(
    "/ui", StaticFiles(directory="frontend/.output/public", html=True), name="static"
)


@router.get("/ui")
async def ui():
    return FileResponse("frontend/.output/public/index.html")
