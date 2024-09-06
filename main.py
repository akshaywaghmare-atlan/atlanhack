from fastapi import FastAPI
from sdk import models
from sdk.routers import events, logs
from sdk.database import engine


app = FastAPI()

@app.on_event("startup")
async def startup():
    models.Base.metadata.create_all(bind=engine)

app.include_router(events.router)
app.include_router(logs.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}