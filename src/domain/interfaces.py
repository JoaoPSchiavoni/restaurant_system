from abc import ABC, abstractmethod
from typing import List, Optional
from src.infrastructure.db.models import User, Order, OrderItem

class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass


class OrderRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    def get_all(self) -> List[Order]:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Order]:
        pass

    @abstractmethod
    def create(self, order: Order) -> Order:
        pass

    @abstractmethod
    def save(self, order: Order) -> Order:
        pass

    @abstractmethod
    def get_item_by_id(self, item_id: int) -> Optional[OrderItem]:
        pass

    @abstractmethod
    def delete_item(self, item: OrderItem) -> None:
        pass
