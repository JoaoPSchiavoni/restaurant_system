from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_session, validate_token
from schemas import OrderSchema, OrderItemSchema, ResponseOrderSchema
from models import Order, User, OrderItem
from typing import List

# Defined prefix as /order. All routes follow RESTful conventions.
order_router = APIRouter(prefix="/order", tags=["order"], dependencies=[Depends(validate_token)])

@order_router.get("/", response_model=List[ResponseOrderSchema])
async def list_orders(session: Session = Depends(get_session), 
                      user: User = Depends(validate_token)):
    """
    Retrieve a list of orders.

    This endpoint returns order data based on the authenticated user's role:
    - **Administrators**: Retrieve all orders currently in the database.
    - **Standard Users**: Retrieve only the orders associated with their account.

    Returns:
        List[Order]: A list of order objects.
    """
    if user.admin:
        orders = session.query(Order).all()
    else:
        orders = session.query(Order).filter(Order.user_id == user.id).all()
    
    return orders

@order_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order( session: Session = Depends(get_session), 
                       current_user: User = Depends(validate_token)):
    """
    Initiate a new order.

    Creates a new, empty order record linked to the currently authenticated user.
    Items must be added to the order subsequently via the items endpoint.

    Returns:
        dict: A confirmation message containing the new Order ID.
    """
    new_order = Order(user_id=current_user.id)
    session.add(new_order)
    session.commit()
    return {"Message": f"Order created successfully {new_order.id}"}

@order_router.get("/{order_id}", response_model=ResponseOrderSchema)
async def get_order_by_id(order_id: int,
                          session: Session = Depends(get_session),
                          user: User = Depends(validate_token)):
    """
    Retrieve detailed information about a specific order.

    Fetches the order details by its unique identifier.

    Raises:
        HTTPException (404): If the order does not exist.
        HTTPException (403): If the user is not an admin and does not own the order.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this resource.")

    return order

@order_router.post("/{order_id}/cancel")
async def cancel_order(order_id: int, 
                       session: Session = Depends(get_session), 
                       user: User = Depends(validate_token)):
    """
    Cancel an existing order.

    Updates the status of the specified order to 'CANCELED'.
    Only the order owner or an administrator can perform this action.

    Raises:
        HTTPException (404): If the order ID is invalid.
        HTTPException (403): If the user lacks permission to modify this order.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to modify this order.")
        
    order.status = "CANCELED"
    session.commit()
    
    return {
        "message": f"Order nº {order.id} was successfully cancelled.",
        "order": order
    }

@order_router.post("/{order_id}/items", status_code=status.HTTP_201_CREATED)
async def add_order_item(order_id: int, 
                         order_item_schema: OrderItemSchema, 
                         session: Session = Depends(get_session), 
                         user: User = Depends(validate_token)):
    """
    Add a new line item to a specific order.

    This operation appends a product (item) to the order and automatically updates
    the total price calculation.

    Args:
        order_id (int): The unique identifier of the target order.
        order_item_schema (OrderItemSchema): The payload containing item details (flavor, size, amount).

    Raises:
        HTTPException (404): If the order is not found.
        HTTPException (403): If the user lacks permission to modify this order.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found!")
    
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to perform this operation.")
    
    new_item = OrderItem(order_item_schema.amount, 
                         order_item_schema.flavor, 
                         order_item_schema.size, 
                         order_item_schema.unit_price, 
                         order_id)
    
    order.items.append(new_item)
    order.sum_price() 
    session.add(new_item)
    session.commit()
    session.refresh(order)
    
    return {
        "message": "Item added successfully",
        "order": order
    }

@order_router.delete("/items/{item_id}")
async def delete_order_item(item_id: int, 
                            session: Session = Depends(get_session),
                            user: User = Depends(validate_token)):
    """
    Remove a line item from an order.

    Deletes a specific item based on its ID and recalculates the order's total price.

    Raises:
        HTTPException (404): If the item does not exist.
        HTTPException (403): If the user does not own the order associated with the item.
    """
    order_item = session.query(OrderItem).filter(OrderItem.id == item_id).first()
    
    if not order_item:
        raise HTTPException(status_code=404, detail="Item not found")

    order = session.query(Order).filter(Order.id == order_item.order_id).first()

    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to perform this operation.")
    
    session.delete(order_item)
    order.sum_price()
    session.commit()
    
    return {
        "message": "Item deleted successfully",
        "order": order
    }

@order_router.post("/{order_id}/finish", response_model=List[OrderItemSchema])
async def finalise_order(order_id: int,
                         session: Session = Depends(get_session),
                         user: User = Depends(validate_token)):
    """
    Finalize an order.

    Marks the order status as 'FINISHED', indicating it is ready for processing.
    
    Constraints:
        - Cannot finalize an order that has already been 'CANCELED'.

    Raises:
        HTTPException (404): If the order is not found.
        HTTPException (403): If the user lacks permission.
        HTTPException (400): If trying to finalize a canceled order.
        
    Returns:
        List[OrderItem]: A list containing all items in the finalized order.
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to perform this operation.")
    
    if order.status == "CANCELED":
        raise HTTPException(status_code=400, detail="Cannot finish a canceled order.")
    
    if order.status == "FINISHED":
        raise HTTPException(status_code=400, detail="The order was already finalized.")
    order.status = "FINISHED"
    session.commit()
    
    return order.items