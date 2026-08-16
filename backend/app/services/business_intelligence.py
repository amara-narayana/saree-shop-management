"""Business Intelligence Services for V2 Features"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.saree_models import (
    Saree, Inventory, StockTransaction, Sale, SaleItem, 
    Customer, Supplier, Expense, Coupon, AuditLog
)


class InventoryAgingService:
    """Service for inventory aging analysis"""
    
    @staticmethod
    def get_aging_buckets(db: Session) -> Dict[str, float]:
        """
        Calculate inventory value by age buckets
        Returns: { '0-30': value, '31-60': value, '61-90': value, '91-180': value, '180+': value }
        """
        now = datetime.utcnow()
        buckets = {
            '0-30': 0.0,
            '31-60': 0.0,
            '61-90': 0.0,
            '91-180': 0.0,
            '180+': 0.0
        }
        
        inventory_items = db.query(Inventory).join(Saree).filter(
            Inventory.quantity > 0,
            Saree.is_active == True
        ).all()
        
        for inv in inventory_items:
            if not inv.first_received_date:
                continue
                
            age_days = (now - inv.first_received_date).days
            value = float(inv.average_cost or inv.saree.purchase_price) * inv.quantity
            
            if age_days <= 30:
                buckets['0-30'] += value
            elif age_days <= 60:
                buckets['31-60'] += value
            elif age_days <= 90:
                buckets['61-90'] += value
            elif age_days <= 180:
                buckets['91-180'] += value
            else:
                buckets['180+'] += value
        
        return buckets
    
    @staticmethod
    def get_dead_stock(db: Session, days_threshold: int = 90) -> List[Dict[str, Any]]:
        """
        Identify dead stock - items not sold in threshold days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        dead_stock = db.query(Inventory, Saree).join(Saree).filter(
            Inventory.quantity > 0,
            or_(
                Inventory.last_sold_date < cutoff_date,
                Inventory.last_sold_date == None
            ),
            Saree.is_active == True
        ).all()
        
        results = []
        for inv, saree in dead_stock:
            days_since_sale = None
            if inv.last_sold_date:
                days_since_sale = (datetime.utcnow() - inv.last_sold_date).days
            
            results.append({
                'saree_id': saree.id,
                'sku': saree.sku,
                'name': saree.name,
                'quantity': inv.quantity,
                'inventory_value': float(inv.average_cost or saree.purchase_price) * inv.quantity,
                'days_since_last_sale': days_since_sale,
                'age_days': inv.age_days,
                'status': 'DEAD_STOCK' if days_since_sale is None or days_since_sale > 180 else 'SLOW'
            })
        
        return sorted(results, key=lambda x: x['inventory_value'], reverse=True)
    
    @staticmethod
    def get_slow_moving_items(db: Session, days: int = 90) -> List[Dict[str, Any]]:
        """Identify slow-moving inventory based on sales velocity"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all active inventory with stock
        inventory_items = db.query(Inventory, Saree).join(Saree).filter(
            Inventory.quantity > 0,
            Saree.is_active == True
        ).all()
        
        results = []
        for inv, saree in inventory_items:
            # Count sales in period
            sales_count = db.query(func.sum(SaleItem.quantity)).join(Sale).filter(
                SaleItem.saree_id == saree.id,
                Sale.created_at >= cutoff_date,
                Sale.sale_status == 'COMPLETED'
            ).scalar() or 0
            
            if sales_count == 0 and inv.quantity > 0:
                velocity = 0
            else:
                velocity = sales_count / days  # units per day
            
            results.append({
                'saree_id': saree.id,
                'sku': saree.sku,
                'name': saree.name,
                'current_stock': inv.quantity,
                'sold_in_period': sales_count,
                'sales_velocity': round(velocity, 2),
                'inventory_value': float(inv.average_cost or saree.purchase_price) * inv.quantity
            })
        
        # Filter for slow movers (velocity < 0.5 units/day or no sales)
        slow_movers = [item for item in results if item['sales_velocity'] < 0.5]
        return sorted(slow_movers, key=lambda x: x['inventory_value'], reverse=True)


class DemandForecastingService:
    """AI-powered demand forecasting service"""
    
    @staticmethod
    def calculate_average_daily_demand(db: Session, saree_id: int, days: int = 90) -> float:
        """Calculate average daily sales for a product"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total_sold = db.query(func.sum(SaleItem.quantity)).join(Sale).filter(
            SaleItem.saree_id == saree_id,
            Sale.created_at >= cutoff_date,
            Sale.sale_status == 'COMPLETED'
        ).scalar() or 0
        
        return total_sold / days if days > 0 else 0
    
    @staticmethod
    def forecast_demand(db: Session, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Forecast demand for next N days using historical data
        Simple implementation - can be enhanced with ML models
        """
        # Group by category
        categories = db.query(Saree.category_id, func.count(Saree.id)).filter(
            Saree.is_active == True
        ).group_by(Saree.category_id).all()
        
        forecast = {
            'total_forecast': 0,
            'by_category': [],
            'recommendations': []
        }
        
        for category_id, product_count in categories:
            # Get all sarees in category
            sarees = db.query(Saree).filter(
                Saree.category_id == category_id,
                Saree.is_active == True
            ).all()
            
            category_demand = 0
            for saree in sarees:
                daily_demand = DemandForecastingService.calculate_average_daily_demand(
                    db, saree.id, days=90
                )
                
                # Apply seasonality factor (simplified)
                # In production, use proper time-series analysis
                seasonality_factor = 1.0  # Could adjust based on month/festivals
                
                predicted_demand = daily_demand * days_ahead * seasonality_factor
                category_demand += predicted_demand
            
            forecast['by_category'].append({
                'category_id': category_id,
                'predicted_units': round(category_demand, 1)
            })
            forecast['total_forecast'] += category_demand
        
        forecast['total_forecast'] = round(forecast['total_forecast'], 1)
        return forecast
    
    @staticmethod
    def get_seasonal_trends(db: Session) -> Dict[str, Any]:
        """Analyze seasonal sales patterns"""
        # Group sales by month for last 12 months
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        
        monthly_sales = db.query(
            func.extract('month', Sale.created_at).label('month'),
            func.sum(SaleItem.quantity).label('total_quantity')
        ).join(SaleItem).filter(
            Sale.created_at >= twelve_months_ago,
            Sale.sale_status == 'COMPLETED'
        ).group_by(
            func.extract('month', Sale.created_at)
        ).all()
        
        trends = {}
        for month, qty in monthly_sales:
            month_name = datetime(2000, int(month), 1).strftime('%B')
            trends[month_name] = qty or 0
        
        return {
            'monthly_trends': trends,
            'peak_months': sorted(trends.items(), key=lambda x: x[1], reverse=True)[:3],
            'low_months': sorted(trends.items(), key=lambda x: x[1])[:3]
        }


class SmartReorderService:
    """Smart reorder point calculation engine"""
    
    @staticmethod
    def calculate_reorder_point(
        avg_daily_demand: float,
        lead_time_days: int,
        safety_stock: int
    ) -> int:
        """
        Reorder Point = Average Daily Demand × Lead Time + Safety Stock
        """
        return int(avg_daily_demand * lead_time_days + safety_stock)
    
    @staticmethod
    def get_reorder_recommendations(db: Session) -> List[Dict[str, Any]]:
        """
        Generate smart reorder recommendations
        """
        inventory_items = db.query(Inventory, Saree).join(Saree).filter(
            Saree.is_active == True,
            Inventory.quantity > 0
        ).all()
        
        recommendations = []
        
        for inv, saree in inventory_items:
            # Calculate average daily demand
            avg_daily_demand = DemandForecastingService.calculate_average_daily_demand(
                db, saree.id, days=90
            )
            
            # Get supplier lead time (default 7 days if unknown)
            lead_time_days = 7
            # In production, would fetch from supplier performance data
            
            # Safety stock = 5 days of demand (configurable)
            safety_stock = int(avg_daily_demand * 5)
            
            # Calculate reorder point
            reorder_point = SmartReorderService.calculate_reorder_point(
                avg_daily_demand, lead_time_days, safety_stock
            )
            
            current_stock = inv.available_quantity
            
            if current_stock <= reorder_point:
                # Calculate recommended order quantity
                # Order up to 30 days of stock
                target_stock = int(avg_daily_demand * 30)
                recommended_qty = max(0, target_stock - current_stock)
                
                recommendations.append({
                    'saree_id': saree.id,
                    'sku': saree.sku,
                    'name': saree.name,
                    'current_stock': current_stock,
                    'reorder_point': reorder_point,
                    'recommended_quantity': recommended_qty,
                    'estimated_cost': float(saree.purchase_price) * recommended_qty,
                    'urgency': 'HIGH' if current_stock < safety_stock else 'MEDIUM',
                    'reason': f"Stock ({current_stock}) at/below reorder point ({reorder_point})"
                })
        
        return sorted(recommendations, key=lambda x: x['urgency'] == 'HIGH', reverse=True)


class ProfitIntelligenceService:
    """Profit analytics and intelligence service"""
    
    @staticmethod
    def calculate_product_profitability(db: Session, saree_id: int) -> Dict[str, Any]:
        """Calculate profitability metrics for a specific product"""
        saree = db.query(Saree).filter(Saree.id == saree_id).first()
        if not saree:
            return None
        
        # Get sales data for last 90 days
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        sales_data = db.query(
            func.sum(SaleItem.quantity).label('total_sold'),
            func.sum(SaleItem.subtotal).label('total_revenue'),
            func.avg(SaleItem.unit_price).label('avg_selling_price')
        ).join(Sale).filter(
            SaleItem.saree_id == saree_id,
            Sale.created_at >= ninety_days_ago,
            Sale.sale_status == 'COMPLETED'
        ).first()
        
        total_sold = sales_data.total_sold or 0
        total_revenue = float(sales_data.total_revenue or 0)
        avg_price = float(sales_data.avg_selling_price or 0)
        
        total_cost = float(saree.purchase_price) * total_sold
        gross_profit = total_revenue - total_cost
        margin_percent = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'saree_id': saree.id,
            'sku': saree.sku,
            'name': saree.name,
            'units_sold_90d': total_sold,
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'gross_profit': round(gross_profit, 2),
            'profit_margin_percent': round(margin_percent, 2),
            'average_selling_price': round(avg_price, 2),
            'purchase_price': float(saree.purchase_price)
        }
    
    @staticmethod
    def get_profitability_matrix(db: Session) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create product profitability matrix
        Quadrants: Stars (High Profit, High Sales), Winners (Low Profit, High Sales),
                   Dead (Low Profit, Low Sales), Question Marks (High Profit, Low Sales)
        """
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        # Get all active products with sales
        sarees = db.query(Saree).filter(Saree.is_active == True).all()
        
        matrix = {
            'stars': [],  # High profit, high sales
            'winners': [],  # Low profit, high sales
            'dead': [],  # Low profit, low sales
            'question_marks': []  # High profit, low sales
        }
        
        # Calculate median values for segmentation
        all_metrics = []
        for saree in sarees:
            metrics = ProfitIntelligenceService.calculate_product_profitability(db, saree.id)
            if metrics and metrics['units_sold_90d'] > 0:
                all_metrics.append(metrics)
        
        if not all_metrics:
            return matrix
        
        median_profit = sorted([m['gross_profit'] for m in all_metrics])[len(all_metrics)//2]
        median_sales = sorted([m['units_sold_90d'] for m in all_metrics])[len(all_metrics)//2]
        
        for metrics in all_metrics:
            is_high_profit = metrics['gross_profit'] > median_profit
            is_high_sales = metrics['units_sold_90d'] > median_sales
            
            if is_high_profit and is_high_sales:
                matrix['stars'].append(metrics)
            elif not is_high_profit and is_high_sales:
                matrix['winners'].append(metrics)
            elif not is_high_profit and not is_high_sales:
                matrix['dead'].append(metrics)
            else:  # is_high_profit and not is_high_sales
                matrix['question_marks'].append(metrics)
        
        return matrix
    
    @staticmethod
    def get_smart_discount_recommendations(db: Session) -> List[Dict[str, Any]]:
        """
        Recommend discounts based on inventory age, margin, and sales velocity
        """
        aging_service = InventoryAgingService()
        dead_stock = aging_service.get_dead_stock(db, days_threshold=90)
        
        recommendations = []
        for item in dead_stock:
            saree = db.query(Saree).filter(Saree.id == item['saree_id']).first()
            if not saree:
                continue
            
            # Calculate current margin
            margin = float(saree.selling_price - saree.purchase_price)
            margin_percent = (margin / float(saree.selling_price) * 100) if saree.selling_price > 0 else 0
            
            # Recommend discount based on age and margin
            age_days = item['age_days']
            
            if age_days > 180:
                # Very old stock - aggressive discount
                recommended_discount = min(25, margin_percent * 0.8)  # Max 25% or 80% of margin
            elif age_days > 120:
                recommended_discount = min(20, margin_percent * 0.7)
            elif age_days > 90:
                recommended_discount = min(15, margin_percent * 0.6)
            else:
                recommended_discount = min(10, margin_percent * 0.5)
            
            recommendations.append({
                'saree_id': item['saree_id'],
                'sku': item['sku'],
                'name': item['name'],
                'current_price': float(saree.selling_price),
                'age_days': age_days,
                'current_margin_percent': round(margin_percent, 2),
                'recommended_discount_percent': round(recommended_discount, 1),
                'discounted_price': round(float(saree.selling_price) * (1 - recommended_discount/100), 2),
                'estimated_new_margin_percent': round(margin_percent - recommended_discount, 2)
            })
        
        return sorted(recommendations, key=lambda x: x['age_days'], reverse=True)


class CustomerIntelligenceService:
    """Customer analytics and RFM analysis"""
    
    @staticmethod
    def calculate_rfm_score(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Calculate RFM (Recency, Frequency, Monetary) score for a customer
        Scores range from 1-5 for each dimension
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        now = datetime.utcnow()
        
        # Recency: Days since last purchase
        last_purchase = db.query(Sale).filter(
            Sale.customer_id == customer_id,
            Sale.sale_status == 'COMPLETED'
        ).order_by(Sale.created_at.desc()).first()
        
        days_since_purchase = (now - last_purchase.created_at).days if last_purchase else 999
        
        # Frequency: Number of purchases in last year
        one_year_ago = now - timedelta(days=365)
        purchase_count = db.query(func.count(Sale.id)).filter(
            Sale.customer_id == customer_id,
            Sale.created_at >= one_year_ago,
            Sale.sale_status == 'COMPLETED'
        ).scalar() or 0
        
        # Monetary: Total spending in last year
        total_spending = db.query(func.sum(Sale.final_amount)).filter(
            Sale.customer_id == customer_id,
            Sale.created_at >= one_year_ago,
            Sale.sale_status == 'COMPLETED'
        ).scalar() or 0
        
        # Score each dimension (1-5)
        recency_score = min(5, max(1, 6 - (days_since_purchase // 30)))  # 5 if <30 days, 1 if >150 days
        frequency_score = min(5, max(1, purchase_count // 2))  # 5 if 10+ purchases
        monetary_score = min(5, max(1, int(total_spending) // 10000))  # 5 if 50k+ spending
        
        rfm_total = recency_score + frequency_score + monetary_score
        
        # Determine segment
        if rfm_total >= 13:
            segment = 'VIP'
        elif rfm_total >= 10:
            segment = 'Loyal'
        elif rfm_total >= 7:
            segment = 'Potential Loyalist'
        elif rfm_total >= 4:
            segment = 'New Customer'
        else:
            segment = 'At Risk'
        
        return {
            'customer_id': customer_id,
            'customer_name': customer.name,
            'recency_score': recency_score,
            'frequency_score': frequency_score,
            'monetary_score': monetary_score,
            'rfm_total': rfm_total,
            'segment': segment,
            'days_since_purchase': days_since_purchase if days_since_purchase < 999 else None,
            'purchases_last_year': purchase_count,
            'spending_last_year': float(total_spending)
        }
    
    @staticmethod
    def get_customer_segments(db: Session) -> Dict[str, List[Dict[str, Any]]]:
        """Get all customers segmented by RFM analysis"""
        customers = db.query(Customer).all()
        
        segments = {
            'VIP': [],
            'Loyal': [],
            'Potential Loyalist': [],
            'New Customer': [],
            'At Risk': [],
            'Lost Customer': []
        }
        
        for customer in customers:
            rfm_data = CustomerIntelligenceService.calculate_rfm_score(db, customer.id)
            if rfm_data:
                segment = rfm_data['segment']
                segments[segment].append(rfm_data)
        
        return segments
    
    @staticmethod
    def get_customer_preferences(db: Session, customer_id: int) -> Dict[str, Any]:
        """Analyze customer preferences based on purchase history"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        # Get all purchases
        purchases = db.query(SaleItem, Saree).join(Saree).join(Sale).filter(
            Sale.customer_id == customer_id,
            Sale.sale_status == 'COMPLETED'
        ).all()
        
        if not purchases:
            return {
                'favorite_fabric': None,
                'favorite_color': None,
                'favorite_brand': None,
                'avg_order_value': 0,
                'preferred_price_range': None
            }
        
        # Count preferences
        fabric_counts = {}
        color_counts = {}
        brand_counts = {}
        prices = []
        
        for sale_item, saree in purchases:
            if saree.fabric_id:
                fabric_counts[saree.fabric_id] = fabric_counts.get(saree.fabric_id, 0) + 1
            if saree.color_id:
                color_counts[saree.color_id] = color_counts.get(saree.color_id, 0) + 1
            if saree.brand_id:
                brand_counts[saree.brand_id] = brand_counts.get(saree.brand_id, 0) + 1
            prices.append(float(sale_item.unit_price))
        
        # Get most common
        favorite_fabric_id = max(fabric_counts, key=fabric_counts.get) if fabric_counts else None
        favorite_color_id = max(color_counts, key=color_counts.get) if color_counts else None
        favorite_brand_id = max(brand_counts, key=brand_counts.get) if brand_counts else None
        
        avg_price = sum(prices) / len(prices) if prices else 0
        
        return {
            'favorite_fabric_id': favorite_fabric_id,
            'favorite_color_id': favorite_color_id,
            'favorite_brand_id': favorite_brand_id,
            'avg_order_value': round(avg_price, 2),
            'preferred_price_range': 'Budget' if avg_price < 5000 else 'Mid-Range' if avg_price < 15000 else 'Premium',
            'total_purchases': len(purchases)
        }


class SupplierPerformanceService:
    """Supplier performance analytics"""
    
    @staticmethod
    def update_supplier_metrics(db: Session, supplier_id: int):
        """Update supplier performance metrics based on historical data"""
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return
        
        # In production, would calculate from purchase orders and receipts
        # This is a placeholder for the logic
        pass
    
    @staticmethod
    def get_supplier_scorecard(db: Session) -> List[Dict[str, Any]]:
        """Get performance scorecard for all suppliers"""
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
        
        scorecards = []
        for supplier in suppliers:
            score = supplier.performance_score or 0
            
            if score >= 90:
                rating = 'Excellent'
            elif score >= 75:
                rating = 'Good'
            elif score >= 60:
                rating = 'Average'
            else:
                rating = 'Needs Improvement'
            
            scorecards.append({
                'supplier_id': supplier.id,
                'name': supplier.name,
                'performance_score': score,
                'rating': rating,
                'avg_lead_time_days': supplier.avg_lead_time_days,
                'on_time_delivery_rate': supplier.on_time_delivery_rate,
                'defect_rate': supplier.defect_rate
            })
        
        return sorted(scorecards, key=lambda x: x['performance_score'], reverse=True)
