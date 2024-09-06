from fastapi import FastAPI
from sdk import models
from sdk.routers import events
from sdk.database import engine


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(events.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}