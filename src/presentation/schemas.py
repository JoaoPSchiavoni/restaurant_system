from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class SchemaUser(BaseModel):
    name: str
    email: str
    password: str
    active: Optional[bool] = True
    admin: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class OrderSchema(BaseModel):
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class LoginSchema(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class OrderItemSchema(BaseModel):
    id: Optional[int] = None
    amount: int
    flavor: str
    size: str
    unit_price: float
    
    model_config = ConfigDict(from_attributes=True)

class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    price: float
    items: List[OrderItemSchema]

    model_config = ConfigDict(from_attributes=True)
