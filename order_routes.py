from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_session, validate_token
from schemas import OrderSchema
from models import Order, User

order_router = APIRouter(prefix="/order", tags=["order"], dependencies=[Depends(validate_token)])

@order_router.get("/")
async def orders():
    return {"Message": "You have accessed the order route"}

@order_router.post("/order")
async def create_order(order_schema: OrderSchema, session: Session = Depends(get_session), current_user: User = Depends(validate_token)):
    new_order = Order(user_id=current_user.id)
    session.add(new_order)
    session.commit()
    return{"Message": f"Order created successfully {new_order.id}"}

@order_router.post("/order/cancel/{order_id}")
async def cancel_order(order_id: int, session: Session = Depends(get_session), user: User = Depends(validate_token)):
    order = session.query(Order).filter(Order.id==order_id).first()
    if not order:
        raise HTTPException(status_code=400,detail="Order not found")
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to make this modification")
    order.status = "CANCELED"
    session.commit()
    return {
        "message":f"Order nº {order.id} was successfully cancelled.",
        "order": order
    }