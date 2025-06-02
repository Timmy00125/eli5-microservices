from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
import os

import crud
import schemas
from database import SessionLocal, create_db_and_tables


# Create database tables
create_db_and_tables()

app = FastAPI(title="History Service")

# Configure CORS to allow local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend development
        "https://eli5-client.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration (should match the Auth service's SECRET_KEY and ALGORITHM)
SECRET_KEY = os.getenv(
    "SECRET_KEY", "your-secret-key"
)  # Ensure this is the SAME as in Auth Service
ALGORITHM = "HS256"


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user_from_token(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> schemas.TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if authorization is None:
        raise credentials_exception

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise credentials_exception

    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
        return schemas.TokenData(email=email, user_id=user_id)
    except JWTError:
        raise credentials_exception


@app.post("/history/", response_model=schemas.HistoryRecord)
def add_history_record(
    record: schemas.HistoryRecordCreate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user_from_token),
):
    """
    Add a new history record for the authenticated user.
    - **concept_details**: JSON object with details of the generated concept or activity.

    Requires Bearer token authentication.
    """
    if current_user.user_id is None:
        raise HTTPException(status_code=403, detail="User ID not found in token")
    return crud.create_history_record(
        db=db, user_id=current_user.user_id, record_data=record
    )


@app.get("/history/{user_id}", response_model=List[schemas.HistoryRecord])
def read_user_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(get_current_user_from_token),
):
    """
    Retrieve history records for a specific user.
    - **user_id**: The ID of the user whose history is to be retrieved.

    Requires Bearer token authentication.
    Ensures that the authenticated user can only access their own history or if they have admin rights (not implemented here).
    For simplicity, this example allows fetching if user_id in path matches user_id in token.
    """
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this history",
        )

    history_records = crud.get_history_records_by_user(db, user_id=user_id)
    return history_records


# Health check endpoint
@app.get("/history/health")
def health_check():
    """Health check endpoint for service discovery."""
    return {"status": "healthy", "service": "history"}
