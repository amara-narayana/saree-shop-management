from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
# Don't auto-create tables on import - use migrations instead
# from app.db.database import engine, Base
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Saree Inventory & Logistics Management System API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "docs": "/docs",
        "v2_features": [
            "Advanced Saree Attributes",
            "Inventory Aging Analysis",
            "Dead Stock Detection",
            "Demand Forecasting",
            "Smart Reorder Recommendations",
            "Profit Intelligence",
            "Customer RFM Segmentation",
            "Supplier Performance Scorecard",
            "Loyalty Program",
            "Coupon Engine",
            "Expense Management",
            "Cash Register Sessions"
        ]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
