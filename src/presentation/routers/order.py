from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.dependencies import get_order_use_case, validate_token
from src.presentation.schemas import OrderItemSchema, ResponseOrderSchema
from src.domain.use_cases import OrderUseCase
from src.infrastructure.db.models import User

order_router = APIRouter(prefix="/order", tags=["order"], dependencies=[Depends(validate_token)])

@order_router.get("/", response_model=List[ResponseOrderSchema])
async def list_orders(
    order_use_case: OrderUseCase = Depends(get_order_use_case), 
    user: User = Depends(validate_token)
):
    """
    Retrieve a list of orders.
    """
    return order_use_case.list_orders(user)

@order_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_use_case: OrderUseCase = Depends(get_order_use_case), 
    current_user: User = Depends(validate_token)
):
    """
    Initiate a new order.
    """
    order = order_use_case.create_order(current_user.id)
    return {"Message": f"Order created successfully {order.id}"}

@order_router.get("/{order_id}", response_model=ResponseOrderSchema)
async def get_order_by_id(
    order_id: int,
    order_use_case: OrderUseCase = Depends(get_order_use_case),
    user: User = Depends(validate_token)
):
    """
    Retrieve detailed information about a specific order.
    """
    try:
        return order_use_case.get_order(order_id, user)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@order_router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int, 
    order_use_case: OrderUseCase = Depends(get_order_use_case), 
    user: User = Depends(validate_token)
):
    """
    Cancel an existing order.
    """
    try:
        order = order_use_case.cancel_order(order_id, user)
        return {
            "message": f"Order nº {order.id} was successfully cancelled.",
            "order": order
        }
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@order_router.post("/{order_id}/items", status_code=status.HTTP_201_CREATED)
async def add_order_item(
    order_id: int, 
    order_item_schema: OrderItemSchema, 
    order_use_case: OrderUseCase = Depends(get_order_use_case), 
    user: User = Depends(validate_token)
):
    """
    Add a new item to a specific order.
    """
    try:
        order = order_use_case.add_item(
            order_id=order_id,
            amount=order_item_schema.amount,
            flavor=order_item_schema.flavor,
            size=order_item_schema.size,
            unit_price=order_item_schema.unit_price,
            user=user
        )
        return {
            "message": "Item added successfully",
            "order": order
        }
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@order_router.delete("/items/{item_id}")
async def delete_order_item(
    item_id: int, 
    order_use_case: OrderUseCase = Depends(get_order_use_case),
    user: User = Depends(validate_token)
):
    """
    Remove a specific item from an order.
    """
    try:
        order = order_use_case.delete_item(item_id, user)
        return {
            "message": "Item deleted successfully",
            "order": order
        }
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@order_router.post("/{order_id}/finish", response_model=List[OrderItemSchema])
async def finalise_order(
    order_id: int,
    order_use_case: OrderUseCase = Depends(get_order_use_case),
    user: User = Depends(validate_token)
):
    """
    Finalize an order.
    """
    try:
        return order_use_case.finalize_order(order_id, user)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
