from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.interfaces import UserRepositoryInterface, OrderRepositoryInterface
from src.infrastructure.db.models import User, Order, OrderItem

class SQLAlchemyUserRepository(UserRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user


class SQLAlchemyOrderRepository(OrderRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.session.query(Order).filter(Order.id == order_id).first()

    def get_all(self) -> List[Order]:
        return self.session.query(Order).all()

    def get_by_user_id(self, user_id: int) -> List[Order]:
        return self.session.query(Order).filter(Order.user_id == user_id).all()

    def create(self, order: Order) -> Order:
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def save(self, order: Order) -> Order:
        self.session.commit()
        self.session.refresh(order)
        return order

    def get_item_by_id(self, item_id: int) -> Optional[OrderItem]:
        return self.session.query(OrderItem).filter(OrderItem.id == item_id).first()

    def delete_item(self, item: OrderItem) -> None:
        self.session.delete(item)
        self.session.commit()
