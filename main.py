import logging
import uvicorn

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import multiprocessing
from fastapi import FastAPI
from app.worker import start_worker
from sdk import models
from sdk.routers import events, logs, metrics, traces
from app.routers import workflow, preflight
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sdk.database import engine


app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@app.on_event("startup")
def start_worker_process():
    models.Base.metadata.create_all(bind=engine)

    worker_process = multiprocessing.Process(target=start_worker)
    worker_process.start()


app.include_router(events.router)
app.include_router(logs.router)
app.include_router(metrics.router)
app.include_router(traces.router)
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


if __name__ == "__main__":
    FastAPIInstrumentor.instrument_app(app)
    uvicorn.run(app, host="0.0.0.0", port=8000)
