from fastapi import FastAPI
from src.presentation.routers.auth import auth_router
from src.presentation.routers.order import order_router

app = FastAPI(
    title="Restaurant System API",
    description="Refactored RESTful API for restaurant management using Clean Architecture.",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(order_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Restaurant System API", "docs": "/docs"}
