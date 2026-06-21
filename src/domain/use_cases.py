from datetime import timedelta
from typing import List, Optional, Union
from src.domain.interfaces import UserRepositoryInterface, OrderRepositoryInterface
from src.infrastructure.db.models import User, Order, OrderItem
from src.infrastructure.security import hash_password, verify_password, create_access_token
from src.config import settings

class AuthUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def register_user(self, name: str, email: str, password: str, active: bool = True, admin: bool = False) -> User:
        """
        Registers a new user after checking if the email already exists.
        """
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("A user with this email already exists")
        
        hashed = hash_password(password)
        new_user = User(name=name, email=email, password=hashed, active=active, admin=admin)
        return self.user_repo.create(new_user)

    def authenticate(self, email: str, password: str) -> Union[User, bool]:
        """
        Verifies credentials against hashed password.
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user

    def generate_tokens(self, user_id: int) -> dict:
        """
        Generates access and refresh tokens.
        """
        access_token = create_access_token(user_id)
        refresh_token = create_access_token(user_id, expires_delta=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }

    def generate_single_token(self, user_id: int) -> dict:
        """
        Generates a single access token.
        """
        access_token = create_access_token(user_id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }


class OrderUseCase:
    def __init__(self, order_repo: OrderRepositoryInterface):
        self.order_repo = order_repo

    def list_orders(self, user: User) -> List[Order]:
        """
        List orders depending on user privileges.
        """
        if user.admin:
            return self.order_repo.get_all()
        return self.order_repo.get_by_user_id(user.id)

    def create_order(self, user_id: int) -> Order:
        """
        Creates a new, empty order.
        """
        new_order = Order(user_id=user_id)
        return self.order_repo.create(new_order)

    def get_order(self, order_id: int, user: User) -> Order:
        """
        Gets an order by ID and verifies permissions.
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise LookupError("Order not found")
        
        if not user.admin and user.id != order.user_id:
            raise PermissionError("Forbidden: You do not have access to this resource.")
        
        return order

    def cancel_order(self, order_id: int, user: User) -> Order:
        """
        Cancels an order.
        """
        order = self.get_order(order_id, user)
        order.status = "CANCELED"
        return self.order_repo.save(order)

    def add_item(self, order_id: int, amount: int, flavor: str, size: str, unit_price: float, user: User) -> Order:
        """
        Appends an item to the order and updates its total price.
        """
        order = self.get_order(order_id, user)
        
        new_item = OrderItem(amount=amount, flavor=flavor, size=size, init_price=unit_price, order=order_id)
        order.items.append(new_item)
        order.sum_price()
        
        return self.order_repo.save(order)

    def delete_item(self, item_id: int, user: User) -> Order:
        """
        Removes an item from an order and updates the total price.
        """
        item = self.order_repo.get_item_by_id(item_id)
        if not item:
            raise LookupError("Item not found")
        
        order = self.get_order(item.order_id, user)
        self.order_repo.delete_item(item)
        order.sum_price()
        
        return self.order_repo.save(order)

    def finalize_order(self, order_id: int, user: User) -> List[OrderItem]:
        """
        Finalizes an order.
        """
        order = self.get_order(order_id, user)
        
        if order.status == "CANCELED":
            raise ValueError("Cannot finish a canceled order.")
        
        if order.status == "FINISHED":
            raise ValueError("The order was already finalized.")
        
        order.status = "FINISHED"
        self.order_repo.save(order)
        return order.items
