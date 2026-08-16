"""Unit tests for V2 Business Intelligence features"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.saree_models import Base, Saree, Inventory, Customer, Sale, SaleItem
# Import only the services we need for testing to avoid ARRAY issues with SQLite
from app.services.business_intelligence import (
    InventoryAgingService,
    DemandForecastingService,
    SmartReorderService,
    ProfitIntelligenceService,
    CustomerIntelligenceService
)

# Test database setup - use PostgreSQL-compatible types workaround
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Only create tables needed for specific tests
    Base.metadata.create_all(bind=engine, tables=[
        Saree.__table__,
        Inventory.__table__
    ])
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


class TestInventoryAgingService:
    """Tests for inventory aging analysis"""
    
    def test_get_aging_buckets_empty(self, db_session):
        """Test aging buckets with no inventory"""
        result = InventoryAgingService.get_aging_buckets(db_session)
        assert result == {'0-30': 0.0, '31-60': 0.0, '61-90': 0.0, '91-180': 0.0, '180+': 0.0}
    
    def test_get_dead_stock_empty(self, db_session):
        """Test dead stock with no inventory"""
        result = InventoryAgingService.get_dead_stock(db_session)
        assert result == []


class TestDemandForecastingService:
    """Tests for demand forecasting"""
    
    def test_calculate_average_daily_demand_no_sales(self, db_session):
        """Test demand calculation with no sales data"""
        # Create a saree
        saree = Saree(
            sku="TEST-001",
            name="Test Saree",
            purchase_price=5000,
            selling_price=8000
        )
        db_session.add(saree)
        db_session.commit()
        
        demand = DemandForecastingService.calculate_average_daily_demand(db_session, saree.id)
        assert demand == 0.0
    
    def test_forecast_demand_structure(self, db_session):
        """Test forecast returns correct structure"""
        result = DemandForecastingService.forecast_demand(db_session, days_ahead=30)
        assert 'total_forecast' in result
        assert 'by_category' in result
        assert 'recommendations' in result


class TestSmartReorderService:
    """Tests for smart reorder calculations"""
    
    def test_calculate_reorder_point(self):
        """Test reorder point formula"""
        # ROP = avg_daily_demand × lead_time + safety_stock
        rop = SmartReorderService.calculate_reorder_point(
            avg_daily_demand=4.0,
            lead_time_days=7,
            safety_stock=10
        )
        assert rop == 38  # 4 × 7 + 10 = 38
    
    def test_get_reorder_recommendations_empty(self, db_session):
        """Test recommendations with no inventory"""
        result = SmartReorderService.get_reorder_recommendations(db_session)
        assert result == []


class TestProfitIntelligenceService:
    """Tests for profit intelligence"""
    
    def test_profitability_matrix_structure(self, db_session):
        """Test profitability matrix returns correct structure"""
        matrix = ProfitIntelligenceService.get_profitability_matrix(db_session)
        assert 'stars' in matrix
        assert 'winners' in matrix
        assert 'dead' in matrix
        assert 'question_marks' in matrix
    
    def test_discount_recommendations_empty(self, db_session):
        """Test discount recommendations with no dead stock"""
        result = ProfitIntelligenceService.get_smart_discount_recommendations(db_session)
        assert result == []


class TestCustomerIntelligenceService:
    """Tests for customer RFM analysis"""
    
    def test_rfm_score_nonexistent_customer(self, db_session):
        """Test RFM for non-existent customer"""
        result = CustomerIntelligenceService.calculate_rfm_score(db_session, 999)
        assert result is None
    
    def test_customer_segments_structure(self, db_session):
        """Test customer segments returns correct structure"""
        segments = CustomerIntelligenceService.get_customer_segments(db_session)
        assert 'VIP' in segments
        assert 'Loyal' in segments
        assert 'Potential Loyalist' in segments
        assert 'New Customer' in segments
        assert 'At Risk' in segments


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_bi_workflow(self, db_session):
        """Test complete BI analysis workflow"""
        # Create test data
        saree = Saree(
            sku="SAR-TEST-001",
            name="Test Silk Saree",
            purchase_price=5000,
            selling_price=8000,
            is_active=True
        )
        db_session.add(saree)
        db_session.commit()
        
        inventory = Inventory(
            saree_id=saree.id,
            quantity=10,
            average_cost=5000,
            first_received_date=datetime.utcnow() - timedelta(days=45)
        )
        db_session.add(inventory)
        db_session.commit()
        
        # Test aging
        aging = InventoryAgingService.get_aging_buckets(db_session)
        assert aging['31-60'] > 0  # Should be in 31-60 bucket
        
        # Test reorder
        recommendations = SmartReorderService.get_reorder_recommendations(db_session)
        # May or may not have recommendations based on demand
        
        # Test profitability
        matrix = ProfitIntelligenceService.get_profitability_matrix(db_session)
        # Matrix should be structured even with minimal data
        
        print("✓ Complete BI workflow test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
