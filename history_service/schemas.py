from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


# Pydantic model for creating a history record (request body)
class HistoryRecordCreate(BaseModel):
    # user_id will be extracted from JWT, not directly from request body for POST
    concept_details: Any  # Flexible JSON structure


# Pydantic model for representing a history record in responses
class HistoryRecord(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    data: Any

    class Config:
        from_attributes = True  # To allow direct creation from SQLAlchemy model


# For JWT token data (similar to Auth service, but only what's needed)
class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
