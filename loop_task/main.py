from fastapi import FastAPI
from .models import StoreStatus, StoreHours, StoreTimezones, ReportStatus
from .database import SessionLocal, engine, Base
from sqlalchemy.orm import Session

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Example endpoint for fetching store status
@app.get("/store_status/{store_id}")
def get_store_status(store_id: str):
    db: Session = SessionLocal()
    store_status = db.query(StoreStatus).filter(StoreStatus.store_id == store_id).first()
    return store_status
