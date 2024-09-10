import logging
import multiprocessing
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI
from sdk import FastAPIApplicationBuilder
from app.routers import workflow, preflight
from app.worker import start_worker


app = FastAPI(title="Postgres App")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@app.on_event("startup")
def start_worker_process():
    # starts a temporal worker process
    worker_process = multiprocessing.Process(target=start_worker)
    worker_process.start()


app.include_router(workflow.router)
app.include_router(preflight.router)


if __name__ == "__main__":
    atlan_app_builder = FastAPIApplicationBuilder(app)
    atlan_app_builder.on_api_service_start()
    atlan_app_builder.add_telemetry_routes()
    atlan_app_builder.add_event_routes()

    # always mount the frontend at the end
    app.mount(
        "/", StaticFiles(directory="frontend/.output/public", html=True), name="static"
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
