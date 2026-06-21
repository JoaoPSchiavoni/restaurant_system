import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from src.config import settings

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Truncates to 72 bytes to maintain compatibility with standard bcrypt limitations.
    """
    pw_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hashed password.
    """
    try:
        pw_bytes = password[:72].encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hashed_bytes)
    except Exception:
        # Fallback in case hash format is invalid or has legacy passlib schemes
        return False

def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """
    Generate a JWT access token for a user.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> int | None:
    """
    Decode and validate a JWT access token.
    Returns the user_id (sub) if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except (jwt.PyJWTError, ValueError):
        return None
