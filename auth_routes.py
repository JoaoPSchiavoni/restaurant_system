from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from dependencies import get_session, validate_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import SchemaUser, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, Union

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(user_id: int, token_duration: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    """
    Generate a JSON Web Token (JWT).

    Args:
        user_id (int): The unique identifier of the user (subject of the token).
        token_duration (timedelta): The lifespan of the token. Defaults to global configuration.

    Returns:
        str: The encoded JWT string.
    """
    expire_data = datetime.now(timezone.utc) + token_duration
    dict_info = {"sub": str(user_id),
                 "exp": expire_data}
    encoded_jwt = jwt.encode(dict_info, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str, session: Session) -> Union[User, bool]:
    """
    Verify user credentials against the database.

    Args:
        email (str): The user's email address.
        password (str): The raw password input.
        session (Session): The database session.

    Returns:
        User: The user instance if credentials are valid.
        bool: False if the user is not found or password does not match.
    """
    user = session.query(User).filter(User.email==email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user


@auth_router.get("/")
async def home():
    """
    Authentication Health Check.

    Simple endpoint to verify if the auth route is accessible.
    """
    return {"Message": "You have accessed the auth route", "auth": False}

@auth_router.post("/create_account", status_code=status.HTTP_201_CREATED)
async def create_account(schema_user: SchemaUser, session: Session = Depends(get_session)):
    """
    Register a new user account.

    Checks if the email is already in use. If not, hashes the password
    (truncating to 72 bytes for bcrypt compatibility) and persists the user.

    Args:
        schema_user (SchemaUser): The payload containing user registration details.
        session (Session): Database session.

    Raises:
        HTTPException (400): If a user with the provided email already exists.

    Returns:
        dict: Success message upon registration.
    """
    user = session.query(User).filter(User.email==schema_user.email).first()
    if user:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
        
    else:
        # Note: Bcrypt has a limit of 72 bytes. We truncate to ensure stability.
        hash_password = bcrypt_context.hash(schema_user.password[:72])
        new_user = User(schema_user.name, schema_user.email, hash_password, schema_user.active, schema_user.admin)
        session.add(new_user)
        session.commit()
        return {"message": f"User successfully registered {schema_user.email}"}
    

@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)):
    """
    Authenticate a user via JSON payload.

    Validates email and password. Returns both an access token (short-lived)
    and a refresh token (long-lived).

    Args:
        login_schema (LoginSchema): The payload containing email and password.
        session (Session): Database session.

    Raises:
        HTTPException (400): If authentication fails (invalid credentials).

    Returns:
        dict: JSON containing access_token, refresh_token, and token_type.
    """
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found or invalid credentials")
    else:
        access_token = create_token(user.id)
        refresh_token = create_token(user.id, token_duration=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
            }
    
@auth_router.post("/login-form")
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Authenticate a user via OAuth2 Form (Swagger UI compatible).

    This endpoint is primarily used by the interactive API documentation (Swagger UI)
    to obtain an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing 'username' (email) and 'password'.
        session (Session): Database session.

    Raises:
        HTTPException (400): If authentication fails.

    Returns:
        dict: JSON containing access_token and token_type.
    """
    
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found or invalid credentials")
    else:
        access_token = create_token(user.id)    
        return {
            "access_token": access_token,
            "token_type": "Bearer"
            }
    
@auth_router.get("/refresh")
async def use_refresh_token(user: User = Depends(validate_token)):
    """
    Issue a new access token for an authenticated user.

    Uses the current valid token (or refresh logic) to generate a fresh access token,
    extending the user's session without requiring re-login credentials.

    Args:
        user (User): The authenticated user (extracted from the current token).

    Returns:
        dict: JSON containing the new access_token.
    """
    access_token = create_token(user.id)
    return {
            "access_token": access_token,
            "token_type": "Bearer"
            }