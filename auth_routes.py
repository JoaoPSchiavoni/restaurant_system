from fastapi import APIRouter
from models import User, db
from sqlalchemy.orm import sessionmaker
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    '''Rota padrao de autenticacao do sistema'''
    return {"Message": "You gave accessed the auth route", "auth": False}

@auth_router.post("/create_account")
async def criar_conta(email: str, password: str, name: str):
    Session = sessionmaker(bind=db)
    session = Session()
    user = session.query(User).filter(User.email==email).first()
    if user:
        # ja existe um usuario com esse email
        return {"message": "A user with this email already exists"}

    else:
        new_user = User(name, email, password)
        session.add(new_user)
        session.commit()
        return {"message": "User successfully registered"}