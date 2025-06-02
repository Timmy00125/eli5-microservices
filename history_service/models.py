from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.sql import func  # For auto-generating timestamp
from database import Base


class HistoryRecord(Base):
    __tablename__ = "history_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, index=True, nullable=False
    )  # Assuming user_id comes from JWT
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    data = Column(
        JSON, nullable=False
    )  # To store concept_details or other activity logs
