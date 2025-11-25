from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import get_session
from schemas import OrderSchema
from models import Order

order_router = APIRouter(prefix="/order", tags=["order"])

@order_router.get("/")
async def orders():
    return {"Message": "You have accessed the order route"}

@order_router.post("/order")
async def create_order(order_schema: OrderSchema, session: Session = Depends(get_session)):
    new_order = Order(user=order_schema.user_id)
    session.add(new_order)
    session.commit()
    return{"Message": f"Order created successfully {new_order.id}"}