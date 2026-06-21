from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.repositories import SQLAlchemyUserRepository, SQLAlchemyOrderRepository
from src.domain.use_cases import AuthUseCase, OrderUseCase
from src.infrastructure.security import decode_access_token
from src.infrastructure.db.models import User

# Define the OAuth2 security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")

def get_session():
    """
    Dependency to obtain database session.
    Kept for backward compatibility with legacy router injections.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_user_repository(session: Session = Depends(get_session)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)

def get_order_repository(session: Session = Depends(get_session)) -> SQLAlchemyOrderRepository:
    return SQLAlchemyOrderRepository(session)

def get_auth_use_case(user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)) -> AuthUseCase:
    return AuthUseCase(user_repo)

def get_order_use_case(order_repo: SQLAlchemyOrderRepository = Depends(get_order_repository)) -> OrderUseCase:
    return OrderUseCase(order_repo)

def validate_token(
    token: str = Depends(oauth2_scheme),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> User:
    """
    Validate the authorization token and return the current user.
    """
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied, check token validity"
        )
    
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Aceess declined!!"
        )
    return user
