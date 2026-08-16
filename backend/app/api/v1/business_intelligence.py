"""API Routes for Business Intelligence V2 Features"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.database import get_db
from app.services.business_intelligence import (
    InventoryAgingService,
    DemandForecastingService,
    SmartReorderService,
    ProfitIntelligenceService,
    CustomerIntelligenceService,
    SupplierPerformanceService
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/v2/intelligence", tags=["Business Intelligence V2"])


# ==================== Inventory Aging ====================

@router.get("/inventory/aging")
def get_inventory_aging(db: Session = Depends(get_db)):
    """Get inventory aging buckets"""
    return InventoryAgingService.get_aging_buckets(db)


@router.get("/inventory/dead-stock")
def get_dead_stock(days_threshold: int = 90, db: Session = Depends(get_db)):
    """Identify dead stock items"""
    return InventoryAgingService.get_dead_stock(db, days_threshold)


@router.get("/inventory/slow-moving")
def get_slow_moving_items(days: int = 90, db: Session = Depends(get_db)):
    """Get slow-moving inventory"""
    return InventoryAgingService.get_slow_moving_items(db, days)


# ==================== Demand Forecasting ====================

@router.get("/forecast/demand")
def forecast_demand(days_ahead: int = 30, db: Session = Depends(get_db)):
    """Get demand forecast for next N days"""
    return DemandForecastingService.forecast_demand(db, days_ahead)


@router.get("/forecast/seasonal-trends")
def get_seasonal_trends(db: Session = Depends(get_db)):
    """Analyze seasonal sales patterns"""
    return DemandForecastingService.get_seasonal_trends(db)


@router.get("/forecast/product/{saree_id}")
def forecast_product_demand(saree_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get demand forecast for specific product"""
    avg_daily = DemandForecastingService.calculate_average_daily_demand(db, saree_id, days=90)
    return {
        'saree_id': saree_id,
        'avg_daily_demand': round(avg_daily, 2),
        'forecasted_demand': round(avg_daily * days, 1),
        'forecast_period_days': days
    }


# ==================== Smart Reorder ====================

@router.get("/reorder/recommendations")
def get_reorder_recommendations(db: Session = Depends(get_db)):
    """Get smart reorder recommendations"""
    return SmartReorderService.get_reorder_recommendations(db)


class ReorderPointCalculation(BaseModel):
    avg_daily_demand: float
    lead_time_days: int
    safety_stock: int


@router.post("/reorder/calculate-point")
def calculate_reorder_point(data: ReorderPointCalculation):
    """Calculate reorder point manually"""
    point = SmartReorderService.calculate_reorder_point(
        data.avg_daily_demand,
        data.lead_time_days,
        data.safety_stock
    )
    return {
        'reorder_point': point,
        'formula': f"{data.avg_daily_demand} × {data.lead_time_days} + {data.safety_stock}"
    }


# ==================== Profit Intelligence ====================

@router.get("/profit/product/{saree_id}")
def get_product_profitability(saree_id: int, db: Session = Depends(get_db)):
    """Get profitability metrics for a product"""
    metrics = ProfitIntelligenceService.calculate_product_profitability(db, saree_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Product not found")
    return metrics


@router.get("/profit/matrix")
def get_profitability_matrix(db: Session = Depends(get_db)):
    """Get product profitability matrix (Stars, Winners, Dead, Question Marks)"""
    return ProfitIntelligenceService.get_profitability_matrix(db)


@router.get("/profit/discount-recommendations")
def get_discount_recommendations(db: Session = Depends(get_db)):
    """Get smart discount recommendations for slow-moving stock"""
    return ProfitIntelligenceService.get_smart_discount_recommendations(db)


# ==================== Customer Intelligence ====================

@router.get("/customers/{customer_id}/rfm")
def get_customer_rfm(customer_id: int, db: Session = Depends(get_db)):
    """Get RFM score and segment for a customer"""
    rfm_data = CustomerIntelligenceService.calculate_rfm_score(db, customer_id)
    if not rfm_data:
        raise HTTPException(status_code=404, detail="Customer not found")
    return rfm_data


@router.get("/customers/segments")
def get_customer_segments(db: Session = Depends(get_db)):
    """Get all customers segmented by RFM analysis"""
    return CustomerIntelligenceService.get_customer_segments(db)


@router.get("/customers/{customer_id}/preferences")
def get_customer_preferences(customer_id: int, db: Session = Depends(get_db)):
    """Analyze customer preferences based on purchase history"""
    prefs = CustomerIntelligenceService.get_customer_preferences(db, customer_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Customer not found")
    return prefs


# ==================== Supplier Performance ====================

@router.get("/suppliers/scorecard")
def get_supplier_scorecard(db: Session = Depends(get_db)):
    """Get performance scorecard for all suppliers"""
    return SupplierPerformanceService.get_supplier_scorecard(db)


# ==================== Dashboard Summary ====================

@router.get("/dashboard/summary")
def get_bi_dashboard_summary(db: Session = Depends(get_db)):
    """Get comprehensive BI dashboard summary"""
    
    # Inventory aging
    aging = InventoryAgingService.get_aging_buckets(db)
    dead_stock = InventoryAgingService.get_dead_stock(db, days_threshold=90)
    
    # Demand forecast
    forecast = DemandForecastingService.forecast_demand(db, days_ahead=30)
    
    # Reorder recommendations
    reorder_recs = SmartReorderService.get_reorder_recommendations(db)
    
    # Profitability
    profit_matrix = ProfitIntelligenceService.get_profitability_matrix(db)
    discount_recs = ProfitIntelligenceService.get_smart_discount_recommendations(db)
    
    # Customer segments
    customer_segments = CustomerIntelligenceService.get_customer_segments(db)
    
    # Supplier scorecard
    supplier_scorecard = SupplierPerformanceService.get_supplier_scorecard(db)
    
    return {
        'inventory_health': {
            'aging_buckets': aging,
            'dead_stock_count': len(dead_stock),
            'dead_stock_value': sum(item['inventory_value'] for item in dead_stock),
            'high_risk_aging': aging.get('180+', 0)
        },
        'demand_forecast': {
            'next_30_days': forecast['total_forecast'],
            'by_category': forecast['by_category']
        },
        'reorder_alerts': {
            'total_recommendations': len(reorder_recs),
            'high_urgency': len([r for r in reorder_recs if r['urgency'] == 'HIGH']),
            'estimated_investment': sum(r['estimated_cost'] for r in reorder_recs)
        },
        'profitability': {
            'stars_count': len(profit_matrix.get('stars', [])),
            'winners_count': len(profit_matrix.get('winners', [])),
            'dead_count': len(profit_matrix.get('dead', [])),
            'question_marks_count': len(profit_matrix.get('question_marks', [])),
            'discount_opportunities': len(discount_recs)
        },
        'customer_insights': {
            'vip_count': len(customer_segments.get('VIP', [])),
            'loyal_count': len(customer_segments.get('Loyal', [])),
            'at_risk_count': len(customer_segments.get('At Risk', []))
        },
        'supplier_performance': {
            'excellent_count': len([s for s in supplier_scorecard if s['rating'] == 'Excellent']),
            'needs_improvement_count': len([s for s in supplier_scorecard if s['rating'] == 'Needs Improvement']),
            'average_score': sum(s['performance_score'] for s in supplier_scorecard) / len(supplier_scorecard) if supplier_scorecard else 0
        }
    }
