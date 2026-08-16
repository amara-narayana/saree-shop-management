# Saree Inventory & Logistics Management System - V2

## Business Intelligence Upgrade

This V2 upgrade transforms the system from a simple inventory+POS toward **intelligent retail operations**.

### 🎯 New V2 Features

#### 1. Advanced Saree Attributes
- Weave type, border type, loom type (handloom/powerloom)
- Length, weight, occasion, season
- Region of origin, designer, collection name
- Batch and lot numbers for traceability

#### 2. Inventory Aging Analysis
```
0-30 days     → Fresh stock
31-60 days    → Normal
61-90 days    → Attention needed
91-180 days   → Slow moving
180+ days     → ⚠️ Dead stock risk
```

#### 3. Dead Stock Detection
Automatically identifies products that haven't sold in 90+ days with:
- Days since last sale
- Inventory value at risk
- Status classification (DEAD_STOCK or SLOW)

#### 4. AI Demand Forecasting
- 7/30/90 day demand forecasts
- Category-level forecasting
- Seasonal trend analysis
- Average daily demand calculations

#### 5. Smart Reorder Engine
```
Reorder Point = Avg Daily Demand × Lead Time + Safety Stock
```
Provides actionable recommendations:
- What to order
- How much to order
- Urgency level (HIGH/MEDIUM)
- Estimated investment required

#### 6. Profit Intelligence
- Per-product profitability metrics
- Gross profit and margin calculations
- Product profitability matrix:
  - ⭐ Stars (High Profit, High Sales)
  - 🔥 Winners (Low Profit, High Sales)
  - ❌ Dead (Low Profit, Low Sales)
  - ❓ Question Marks (High Profit, Low Sales)

#### 7. Smart Discount Recommendations
AI-powered discount suggestions based on:
- Inventory age
- Current margin
- Sales velocity

Example: "Product unsold for 147 days → Recommended discount: 12-15%"

#### 8. Customer RFM Analysis
Segment customers using Recency, Frequency, Monetary scoring:
- VIP (score 13-15)
- Loyal (score 10-12)
- Potential Loyalist (score 7-9)
- New Customer (score 4-6)
- At Risk (score <4)

#### 9. Customer Preferences
Track and analyze:
- Favorite fabrics
- Preferred colors
- Favorite brands
- Average order value
- Price range preferences

#### 10. Supplier Performance Scorecard
Rate suppliers on:
- Average lead time
- On-time delivery rate
- Defect rate
- Overall performance score (0-100)

#### 11. Loyalty Program
- Points accumulation (₹100 = 1 point)
- Membership tiers (REGULAR, SILVER, GOLD, PLATINUM)
- Customer birthday/anniversary tracking
- Preferred fabric/color tracking

#### 12. Coupon Engine
Support for:
- Percentage or fixed discounts
- Minimum purchase requirements
- Maximum discount caps
- Validity periods
- Usage limits
- Category/product-specific coupons

#### 13. Expense Management
- Expense categories (Rent, Electricity, Salary, etc.)
- Payment method tracking
- Receipt image storage
- Date-based reporting

#### 14. Cash Register Sessions
- Opening/closing amounts
- Expected vs actual cash
- Variance tracking
- Session notes

---

## API Endpoints - V2

### Business Intelligence

```
GET /api/v2/intelligence/inventory/aging
    → Inventory aging buckets

GET /api/v2/intelligence/inventory/dead-stock?days_threshold=90
    → Dead stock items

GET /api/v2/intelligence/inventory/slow-moving?days=90
    → Slow-moving inventory

GET /api/v2/intelligence/forecast/demand?days_ahead=30
    → Demand forecast

GET /api/v2/intelligence/forecast/seasonal-trends
    → Seasonal sales patterns

GET /api/v2/intelligence/forecast/product/{saree_id}
    → Product-specific forecast

GET /api/v2/intelligence/reorder/recommendations
    → Smart reorder recommendations

POST /api/v2/intelligence/reorder/calculate-point
    → Manual reorder point calculation

GET /api/v2/intelligence/profit/product/{saree_id}
    → Product profitability metrics

GET /api/v2/intelligence/profit/matrix
    → Profitability matrix (Stars/Winners/Dead/Question Marks)

GET /api/v2/intelligence/profit/discount-recommendations
    → Smart discount suggestions

GET /api/v2/intelligence/customers/{customer_id}/rfm
    → Customer RFM score

GET /api/v2/intelligence/customers/segments
    → All customer segments

GET /api/v2/intelligence/customers/{customer_id}/preferences
    → Customer preference analysis

GET /api/v2/intelligence/suppliers/scorecard
    → Supplier performance scorecard

GET /api/v2/intelligence/dashboard/summary
    → Comprehensive BI dashboard summary
```

---

## Database Schema Changes

### Enhanced Sarees Table
```sql
weave_type VARCHAR
border_type VARCHAR
blouse_included BOOLEAN
length_meters NUMERIC(5,2)
weight_grams INTEGER
occasion VARCHAR
season VARCHAR
region_origin VARCHAR
loom_type VARCHAR  -- Handloom/Powerloom
designer VARCHAR
collection_name VARCHAR
batch_number VARCHAR
lot_number VARCHAR
```

### Enhanced Inventory Table
```sql
first_received_date TIMESTAMP
last_sold_date TIMESTAMP
average_cost NUMERIC(12,2)
reserved_quantity INTEGER
```

### Enhanced Customers Table
```sql
loyalty_points INTEGER DEFAULT 0
membership_tier VARCHAR DEFAULT 'REGULAR'
date_of_birth DATE
anniversary_date DATE
preferred_fabric VARCHAR
preferred_color VARCHAR
```

### New Tables
- `coupons` - Coupon management
- `expense_categories` - Expense categorization
- `expenses` - Expense tracking
- `cash_register_sessions` - Cash management

### Enhanced Sales Table
```sql
coupon_code VARCHAR
coupon_discount NUMERIC(12,2)
total_cost_basis NUMERIC(12,2)
gross_profit NUMERIC(12,2)
profit_margin_percent NUMERIC(5,2)
```

### Enhanced Suppliers Table
```sql
avg_lead_time_days FLOAT
on_time_delivery_rate FLOAT  -- Percentage 0-100
defect_rate FLOAT  -- Percentage 0-100
performance_score FLOAT  -- Score 0-100
```

---

## Running the Application

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ (for frontend)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend runs at: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: http://localhost:5173

---

## Testing

```bash
cd backend

# Run all tests
pytest

# Run V2 BI tests specifically
pytest tests/test_v2_business_intelligence.py -v

# Run with coverage
pytest --cov=app tests/
```

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/saree_inventory

# JWT Authentication
SECRET_KEY=your-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Payment (for future integration)
PAYMENT_PROVIDER=test
PAYMENT_MODE=test
PAYMENT_API_KEY=test_api_key
PAYMENT_API_SECRET=test_api_secret
PAYMENT_WEBHOOK_SECRET=test_webhook_secret

# Application
APP_NAME="Saree Inventory Management System"
DEBUG=True
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

---

## Migration Guide

### From V1 to V2

1. **Backup your database**
   ```bash
   pg_dump saree_inventory > backup_v1.sql
   ```

2. **Run new migrations**
   ```bash
   alembic upgrade head
   ```

3. **Update existing data** (optional)
   - Populate new saree attributes
   - Calculate initial loyalty points
   - Set supplier performance metrics

4. **Test thoroughly** before deploying to production

---

## Key Formulas Used

### Reorder Point
```
ROP = Average Daily Demand × Lead Time (days) + Safety Stock
```

### Safety Stock (recommended)
```
Safety Stock = Average Daily Demand × 5 days
```

### RFM Scoring
```
Recency Score: 1-5 (5 = purchased within 30 days)
Frequency Score: 1-5 (5 = 10+ purchases/year)
Monetary Score: 1-5 (5 = ₹50,000+ spending/year)

Total RFM = R + F + M (3-15)
```

### Profit Margin
```
Gross Profit = Revenue - Cost of Goods Sold
Profit Margin % = (Gross Profit / Revenue) × 100
```

### Inventory Age
```
Age (days) = Today - First Received Date
```

---

## Production Deployment Considerations

### Security
- Change all default secrets
- Use HTTPS/TLS
- Implement rate limiting
- Enable audit logging
- Regular security updates

### Performance
- Index frequently queried columns
- Implement caching for BI queries
- Use connection pooling
- Consider read replicas for analytics

### Monitoring
- Track API response times
- Monitor database query performance
- Set up alerts for dead stock
- Track system health metrics

### Backup Strategy
- Daily automated backups
- Weekly full backups
- Monthly backup verification
- Off-site backup storage

---

## Roadmap - Future V3 Features

- Multi-branch management
- Inter-branch stock transfers
- Central warehouse support
- Reservation system
- Barcode/QR code generation
- WhatsApp integration
- Mobile app for staff
- Customer portal
- Online ordering
- AI business copilot (natural language queries)
- Image-based product search
- Offline POS capability

---

## Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review test files for usage examples
3. Check application logs for errors

---

**Version:** 2.0.0  
**Last Updated:** 2024  
**License:** Proprietary
