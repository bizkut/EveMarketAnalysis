from fastapi import FastAPI
from app import api, models
from app.database import engine
from app.logging_config import setup_logging

setup_logging()

app = FastAPI()

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)

app.include_router(api.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the EVE Profit Analyzer AI"}