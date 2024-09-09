import logging
import uvicorn

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from sdk import models
from sdk.routers import events, logs, metrics, traces
from sdk.database import engine


app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@app.on_event("startup")
async def startup():
    models.Base.metadata.create_all(bind=engine)

app.include_router(events.router)
app.include_router(logs.router)
app.include_router(metrics.router)
app.include_router(traces.router)


@app.get("/")
async def root():
    logger.info("Hi there, Mr. Pineapple!")
    return {"message": "Hello World"}


if __name__ == "__main__":
    FastAPIInstrumentor.instrument_app(app)
    uvicorn.run(app, host="0.0.0.0", port=8000)