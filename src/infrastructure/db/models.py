from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.db.database import Base
from typing import List

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)

    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __init__(self, name: str, email: str, password: str, active: bool = True, admin: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    price: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")

    def __init__(self, user_id: int, status: str = "PENDING", price: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.status = status
        self.price = price

    def sum_price(self):
        self.price = sum(item.unit_price * item.amount for item in self.items)

class OrderItem(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(Integer)
    flavor: Mapped[str] = mapped_column(String)
    size: Mapped[str] = mapped_column(String)
    unit_price: Mapped[float] = mapped_column(Float)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    order: Mapped["Order"] = relationship(back_populates="items")

    def __init__(self, amount: int, flavor: str, size: str, init_price: float, order: int, **kwargs):
        super().__init__(**kwargs)
        self.amount = amount
        self.flavor = flavor
        self.size = size
        self.unit_price = init_price
        self.order_id = order
