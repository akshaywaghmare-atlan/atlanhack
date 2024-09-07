from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sdk import models
from sdk.routers import events, logs
from sdk.database import engine


app = FastAPI()

app.mount("/", StaticFiles(directory="frontend/.output/public", html=True), name="static")

@app.on_event("startup")
async def startup():
    models.Base.metadata.create_all(bind=engine)

app.include_router(events.router)
app.include_router(logs.router)


@app.get("/")
async def ui():
    return FileResponse("frontend/.output/public/index.html")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    return {"status": "ok"}