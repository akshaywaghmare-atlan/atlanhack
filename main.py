from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import multiprocessing
from fastapi import FastAPI
from app.worker import start_worker
from sdk import models
from sdk.routers import events, logs
from app.routers import workflow, preflight
from sdk.database import engine


app = FastAPI()

@app.on_event("startup")
def start_worker_process():
    models.Base.metadata.create_all(bind=engine)

    worker_process = multiprocessing.Process(target=start_worker)
    worker_process.start()


app.include_router(events.router)
app.include_router(logs.router)
app.include_router(workflow.router)
app.include_router(preflight.router)


app.mount("/", StaticFiles(directory="frontend/.output/public", html=True), name="static")
@app.get("/")
async def ui():
    return FileResponse("frontend/.output/public/index.html")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    return {"status": "ok"}