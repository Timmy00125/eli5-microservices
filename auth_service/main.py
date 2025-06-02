from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional


# Change relative imports to absolute imports
import crud
import schemas
import auth_utils
from database import SessionLocal, create_db_and_tables

# Create database tables if they don't exist
# In a production Render environment, you might run migrations separately
# or ensure your Dockerfile/build script handles this.
create_db_and_tables()

app = FastAPI(title="Auth Service")

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


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/auth/signup", response_model=schemas.User)
def signup_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    - **username**: Username for the new user.
    - **email**: Email for the new user.
    - **password**: Password for the new user.
    """
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    created_user = crud.create_user(db=db, user=user)
    # Exclude password from the response, even though User schema doesn't have it.
    # This is more for clarity if User schema were to change.
    # Use model_validate for robust mapping from the SQLAlchemy model to the Pydantic schema.
    # This requires schemas.User to have model_config = {"from_attributes": True} (Pydantic V2).
    return schemas.User.model_validate(created_user)


@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Log in a user and return a JWT access token.
    Uses OAuth2PasswordRequestForm, so expects 'username' (which we treat as email here for login) and 'password' in form data.
    """
    user = crud.get_user_by_email(
        db, email=form_data.username
    )  # form_data.username is used for email
    if not user or not auth_utils.verify_password(
        form_data.password, str(user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/login", response_model=schemas.Token)
def login_with_json(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Log in a user with JSON payload and return a JWT access token.
    Accepts JSON with 'email' and 'password' fields.
    """
    user = crud.get_user_by_email(db, email=user_login.email)
    if not user or not auth_utils.verify_password(
        user_login.password, str(user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Example of a protected route (optional, for testing token verification)


async def get_current_user(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    """Get current user from JWT token."""
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
    token_data = auth_utils.verify_token(token, credentials_exception)
    user = crud.get_user_by_email(db, email=token_data.get("sub"))
    if user is None:
        raise credentials_exception
    return user


@app.get("/auth/me", response_model=schemas.User)
async def read_users_me(current_user=Depends(get_current_user)):
    """Get current authenticated user information."""
    return schemas.User.model_validate(current_user)


# Health check endpoint
@app.get("/auth/health")
def health_check():
    """Health check endpoint for service discovery."""
    return {"status": "healthy", "service": "auth"}
