from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_session, validate_token
from schemas import OrderSchema, OrderItemSchema, ResponseOrderSchema
from models import Order, User, OrderItem
from typing import List

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

@order_router.get("/list")
async def order_list(session: Session = Depends(get_session), user: User = Depends(validate_token)):
    if not user.admin:
        raise HTTPException(status_code=401, detail="You do not have permission to perform this operation.")
    else:
        orders = session.query(Order).all()
        return{
            "orders": orders
        }
    
@order_router.post("/order/add-item/{order_id}")
async def add_order_item(order_id: int, 
                         order_item_schema: OrderItemSchema, 
                         session: Session = Depends(get_session), 
                         user: User = Depends(validate_token)):
    
    order = session.query(Order).filter(Order.id==order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found!")
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to perform this operation.")
    
    new_item = OrderItem(order_item_schema.amount, 
                           order_item_schema.flavor, 
                           order_item_schema.size, 
                           order_item_schema.init_price, 
                           order_id)
    
    order.items.append(new_item)
    
    order.sum_price()
    session.add(new_item)
    session.commit()
    session.refresh(order)
    return{
        "message": "Order created successfully",
        "item_id": new_item.id,
        "quantity_items_order": len(order.items),
        "order": order
    }

@order_router.post("/order/delete-item/{item_id}")
async def delete_order_item_by_id(order_item_id: int, 
                                  session: Session = Depends(get_session),
                                  user: User = Depends(validate_token)):
    
    order_item = session.query(OrderItem).filter(OrderItem.id==order_item_id).first()
    order = session.query(Order).filter(Order.id==order_item.order_id).first()

    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to perform this operation.")
    if not order_item:
        raise HTTPException(status_code=400, detail="Item in order not found")
    
    session.delete(order_item)
    order.sum_price()
    session.commit()
    return {
        "message": "Item delete successfully",
        "quantity_items_order": len(order.items),
        "order": order
    }

@order_router.get("/order/list-order/{order_id}", response_model=ResponseOrderSchema)
async def get_order_by_id(order_id: int,
                          session: Session = Depends(get_session),
                          user: User = Depends(validate_token)):
    
    order = session.query(Order).filter(Order.id==order_id).first()
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to perform this operation.")
    
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")

    return order

@order_router.post("/order/finished/{order_id}")
async def finalise_order(order_id: int,
                         session: Session = Depends(get_session),
                         user: User = Depends(validate_token)):
    
    order = session.query(Order).filter(Order.id==order_id).first()

    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to perform this operation.")
    
    if not order:
        raise HTTPException(status_code=400, detail="Order not found.")
    
    if order.status == "CANCELED":
        raise HTTPException(status_code=401, detail="You do not have permission to perform this operation.")
    else:
        order.status = "FINISHED"
        session.commit()
        return {
            "message":f"Order nº {order.id} was successfully finished.",
            "order": order
        }

@order_router.get("order/list-user-orders/", response_model=List[ResponseOrderSchema])
async def list_user_orders(
                           session: Session = Depends(get_session),
                           user: User = Depends(validate_token)):
   
    orders = session.query(Order).filter(Order.user_id == user.id).all()

    return orders
    

