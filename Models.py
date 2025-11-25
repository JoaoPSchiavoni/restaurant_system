from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
#from sqlalchemy_utils.types import ChoiceType

#cria a conexao do seu banco
db = create_engine("sqlite:///banco.db")

#cria a base do banco de dados
Base = declarative_base()



class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    email = Column("email", String, nullable=False, unique=True)
    password = Column("password", String, nullable=False)
    active = Column("active", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, name, email, password, active=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin


class Order(Base):
    __tablename__ = "orders"

    # ORDER_STATUS = (
    #    ("PENDENTE", "PENDENTE"),
    #    ("CANCELADO", "CANCELADO"),
    #    ("FINALIZADO", "FINALIZADO")
    # )
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String) 
    user_id = Column("user", ForeignKey("users.id"))
    price = Column("price", Float)
    # items = 

    def __init__(self, user, status="PENDENTE", price=0.0):
        self.user = user
        self.status = status
        self.price = price


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    amount = Column("amout", Integer)
    flavor = Column("flavor", String)
    size = Column("size", String)
    unit_price = Column("unit_price", Float)
    order = Column("order", ForeignKey("orders.id"))

    def __init__(self, amount, flavor, size, init_price, order):
        self.amount = amount
        self.flavor = flavor
        self.size = size
        self.init_price = init_price
        self.order = order
# executa a criacao dos metadados do banco (cria efetivamente o banco de. dados)