from fastapi import APIRouter
from app.api.v1.endpoints import auth, sarees, inventory, sales, suppliers, customers, dashboard
from app.api.v1.business_intelligence import router as bi_router

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(sarees.router)
api_router.include_router(inventory.router)
api_router.include_router(sales.router)
api_router.include_router(suppliers.router)
api_router.include_router(customers.router)
api_router.include_router(dashboard.router)
api_router.include_router(bi_router)  # V2 Business Intelligence routes
