from fastapi import APIRouter, Depends, HTTPException
from models import User
from dependencies import get_session
from main import bcrypt_context
from schemas import SchemaUser, LoginSchema
from sqlalchemy.orm import Session
auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(user_id):
    token = f"h6MDWu8p1Bhku6jgI2Byr{user_id}"
    return token

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
    user = session.query(User).filter(User.email==login_schema.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    else:
        access_token = create_token(user.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
            }