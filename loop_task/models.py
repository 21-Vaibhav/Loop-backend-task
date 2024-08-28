from sqlalchemy import Column,Integer,String, Time, TIMESTAMP
from .database import Base

class StoreStatus(Base):
    __tablename__ = 'store_status'

    store_id = Column(String, primary_key=True, index=True)
    timestamp_utc = Column(TIMESTAMP)
    status = Column(String)

class StoreHours(Base):
    __tablename__ = 'store_hours'

    store_id = Column(String, primary_key=True, index=True)
    day_of_week = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)

class StoreTimezones(Base):
    __tablename__ = 'store_timezones'

    store_id = Column(String, primary_key=True, index=True)
    timezone_str = Column(String)

class ReportStatus(Base):
    __tablename__ = 'report_status'

    report_id = Column(String, primary_key=True, index=True)
    status = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
