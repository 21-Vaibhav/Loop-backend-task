from fastapi import FastAPI,Depends
from .models import StoreStatus, StoreHours, StoreTimezones, ReportStatus
from .database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from .generate_report import generate_reports_for_all_stores
from .database import get_db

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

@app.get("/generate_report")
def generate_report(db: Session = Depends(get_db)):
    generate_reports_for_all_stores(db)
    return {"message": "Report generation triggered successfully"}