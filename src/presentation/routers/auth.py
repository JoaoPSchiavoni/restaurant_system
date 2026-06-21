from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.dependencies import get_auth_use_case, validate_token
from src.presentation.schemas import SchemaUser, LoginSchema
from src.domain.use_cases import AuthUseCase
from src.infrastructure.db.models import User

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    """
    Authentication Health Check.
    Simple endpoint to verify if the auth route is accessible.
    """
    return {"Message": "You have accessed the auth route", "auth": False}

@auth_router.post("/create_account", status_code=status.HTTP_201_CREATED)
async def create_account(
    schema_user: SchemaUser, 
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """
    Register a new user account.
    """
    try:
        auth_use_case.register_user(
            name=schema_user.name,
            email=schema_user.email,
            password=schema_user.password,
            active=schema_user.active,
            admin=schema_user.admin
        )
        return {"message": f"User successfully registered {schema_user.email}"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@auth_router.post("/login")
async def login(
    login_schema: LoginSchema, 
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """
    Authenticate a user via JSON payload.
    """
    user = auth_use_case.authenticate(login_schema.email, login_schema.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User not found or invalid credentials"
        )
    return auth_use_case.generate_tokens(user.id)

@auth_router.post("/login-form")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """
    Authenticate a user via OAuth2 Form (Swagger UI compatible).
    """
    user = auth_use_case.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User not found or invalid credentials"
        )
    return auth_use_case.generate_single_token(user.id)

@auth_router.get("/refresh")
async def use_refresh_token(
    user: User = Depends(validate_token),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """
    Issue a new access token for an authenticated user.
    """
    return auth_use_case.generate_single_token(user.id)
