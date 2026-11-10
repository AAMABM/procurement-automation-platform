from fastapi import APIRouter

from app.api.v1 import auth, health, users, vendors, requisitions, purchase_orders

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(vendors.router)
api_router.include_router(requisitions.router)
api_router.include_router(purchase_orders.router)