import logging
import uvicorn

import multiprocessing
from fastapi import FastAPI
from app.worker import start_worker
from sdk import FastAPIApplicationBuilder
from app.routers import workflow, preflight


app = FastAPI(title="Postgres App")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@app.on_event("startup")
def start_worker_process():
    atlan_app_builder.on_api_service_start()

    # starts a temporal worker process
    worker_process = multiprocessing.Process(target=start_worker)
    worker_process.start()

app.include_router(workflow.router)
app.include_router(preflight.router)


# app.mount("/", StaticFiles(directory="frontend/.output/public", html=True), name="static")
# @app.get("/")
# async def ui():
#     return FileResponse("frontend/.output/public/index.html")

@app.get("/health")
async def health():
    logger.info("Health check")
    return {"status": "ok"}


if __name__ == "__main__":
    atlan_app_builder = FastAPIApplicationBuilder(app)
    atlan_app_builder.add_telemetry_routes()
    atlan_app_builder.add_event_routes()

    uvicorn.run(app, host="0.0.0.0", port=8000)