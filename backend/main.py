from fastapi import FastAPI
from app import api, models
from app.database import engine
from app.logging_config import setup_logging

setup_logging()

app = FastAPI()

from app.database import SessionLocal

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Populate static data if the tables are empty
        if db.query(models.Region).count() == 0:
            crud.populate_regions(db)
        if db.query(models.Category).count() == 0:
            crud.populate_categories(db)
    finally:
        db.close()

app.include_router(api.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the EVE Profit Analyzer AI"}