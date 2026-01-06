from fastapi import APIRouter, Depends, HTTPException
from models import User
from dependencies import get_session, validate_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import SchemaUser, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(user_id, token_duration = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    expire_data = datetime.now(timezone.utc) + token_duration
    dict_info = {"sub": str(user_id),
                 "exp": expire_data}
    encoded_jwt = jwt.encode(dict_info, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def authenticate_user(email, password, session):
    user = session.query(User).filter(User.email==email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user


@auth_router.get("/")
async def home():
    '''Rota padrao de autenticacao do sistema'''
    return {"Message": "You gave accessed the auth route", "auth": False}

@auth_router.post("/create_account")
async def create_account(schema_user: SchemaUser,session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email==schema_user.email).first()
    if user:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
        
    else:
        # debug: inspeciona o valor recebido antes do hash
        print("DEBUG password repr:", repr(schema_user.password))
        print("DEBUG type:", type(schema_user.password))
        try:
            b = schema_user.password.encode("utf-8")
            print("DEBUG bytes len:", len(b))
        except Exception as e:
            print("DEBUG encode error:", e)
        # truncar como fallback (mantém compatibilidade)
        hash_password = bcrypt_context.hash(schema_user.password[:72])
        new_user = User(schema_user.name, schema_user.email, hash_password, schema_user.active, schema_user.admin)
        session.add(new_user)
        session.commit()
        return {"message": f"User successfully registered {schema_user.email}"}
    

@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)):
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found or invalid credentials")
    else:
        access_token = create_token(user.id)
        refresh_token = create_token(user.id, token_duration=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
            }
    
@auth_router.post("/login-form")
async def login_form(form_data:OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found or invalid credentials")
    else:
        access_token = create_token(user.id)    
        return {
            "access_token": access_token,
            "token_type": "Bearer"
            }
    
@auth_router.get("/refresh")
async def use_refresh_token(user: User = Depends(validate_token) ):
    access_token = create_token(user.id)
    return {
            "access_token": access_token,
            "token_type": "Bearer"
            }

