"""SQLAlchemy models for Saree Inventory System V2"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, Float, 
    DateTime, Date, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Brand(Base):
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    sarees = relationship("Saree", back_populates="brand")


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    
    children = relationship("Category", backref="parent", remote_side=[id])
    sarees = relationship("Saree", back_populates="category")


class Fabric(Base):
    __tablename__ = 'fabrics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    sarees = relationship("Saree", back_populates="fabric")


class Color(Base):
    __tablename__ = 'colors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    hex_code = Column(String)
    
    sarees = relationship("Saree", back_populates="color")


class Design(Base):
    __tablename__ = 'designs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    sarees = relationship("Saree", back_populates="design")


class Saree(Base):
    __tablename__ = 'sarees'
    
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, nullable=False)
    barcode = Column(String, unique=True)
    name = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    fabric_id = Column(Integer, ForeignKey('fabrics.id'))
    color_id = Column(Integer, ForeignKey('colors.id'))
    design_id = Column(Integer, ForeignKey('designs.id'))
    purchase_price = Column(Numeric(12, 2), nullable=False)
    selling_price = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0)
    description = Column(Text)
    image_url = Column(String)
    reorder_level = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # V2 Advanced Attributes
    weave_type = Column(String)
    border_type = Column(String)
    blouse_included = Column(Boolean, default=False)
    length_meters = Column(Numeric(5, 2))
    weight_grams = Column(Integer)
    occasion = Column(String)
    season = Column(String)
    region_origin = Column(String)
    loom_type = Column(String)  # Handloom/Powerloom
    designer = Column(String)
    collection_name = Column(String)
    batch_number = Column(String)
    lot_number = Column(String)
    
    # Relationships
    brand = relationship("Brand", back_populates="sarees")
    category = relationship("Category", back_populates="sarees")
    fabric = relationship("Fabric", back_populates="sarees")
    color = relationship("Color", back_populates="sarees")
    design = relationship("Design", back_populates="sarees")
    inventory = relationship("Inventory", back_populates="saree", uselist=False)
    stock_transactions = relationship("StockTransaction", back_populates="saree")
    sale_items = relationship("SaleItem", back_populates="saree")
    return_items = relationship("ReturnItem", back_populates="saree")


class Inventory(Base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    saree_id = Column(Integer, ForeignKey('sarees.id'), nullable=False)
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    first_received_date = Column(DateTime)
    last_sold_date = Column(DateTime)
    average_cost = Column(Numeric(12, 2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    saree = relationship("Saree", back_populates="inventory")
    
    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
    
    @property
    def age_days(self):
        if self.first_received_date:
            return (datetime.utcnow() - self.first_received_date).days
        return 0
    
    @property
    def days_since_last_sale(self):
        if self.last_sold_date:
            return (datetime.utcnow() - self.last_sold_date).days
        return None


class StockTransaction(Base):
    __tablename__ = 'stock_transactions'
    
    id = Column(Integer, primary_key=True)
    saree_id = Column(Integer, ForeignKey('sarees.id'), nullable=False)
    transaction_type = Column(String, nullable=False)  # PURCHASE, SALE, RETURN, ADJUSTMENT
    quantity_change = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reference_type = Column(String)  # PURCHASE_ORDER, SALE, RETURN
    reference_id = Column(Integer)
    reason = Column(String)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    saree = relationship("Saree", back_populates="stock_transactions")


class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    gst_number = Column(String)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # V2 Performance Metrics
    avg_lead_time_days = Column(Float)
    on_time_delivery_rate = Column(Float)  # Percentage 0-100
    defect_rate = Column(Float)  # Percentage 0-100
    performance_score = Column(Float)  # Score 0-100


class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    city = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # V2 Loyalty Fields
    loyalty_points = Column(Integer, default=0)
    membership_tier = Column(String, default='REGULAR')  # REGULAR, SILVER, GOLD, PLATINUM
    date_of_birth = Column(Date)
    anniversary_date = Column(Date)
    preferred_fabric = Column(String)
    preferred_color = Column(String)
    
    sales = relationship("Sale", back_populates="customer")
    returns = relationship("Return", back_populates="customer")
    
    @property
    def rfm_score(self):
        """Calculate RFM score for customer segmentation"""
        # This would be calculated based on purchase history
        # Recency, Frequency, Monetary
        return None
    
    @property
    def customer_segment(self):
        """Determine customer segment based on behavior"""
        if self.membership_tier == 'PLATINUM':
            return 'VIP'
        elif self.membership_tier == 'GOLD':
            return 'Loyal'
        elif self.loyalty_points > 1000:
            return 'Potential Loyalist'
        else:
            return 'Regular'


class Coupon(Base):
    __tablename__ = 'coupons'
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    discount_type = Column(String, nullable=False)  # PERCENTAGE, FIXED
    value = Column(Numeric(10, 2), nullable=False)
    min_purchase_amount = Column(Numeric(12, 2))
    max_discount_amount = Column(Numeric(12, 2))
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    applicable_categories = Column(ARRAY(String))
    applicable_products = Column(ARRAY(Integer))
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True


class ExpenseCategory(Base):
    __tablename__ = 'expense_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    expenses = relationship("Expense", back_populates="category")


class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('expense_categories.id'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String)
    payment_method = Column(String)
    receipt_image = Column(String)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    category = relationship("ExpenseCategory", back_populates="expenses")


class CashRegisterSession(Base):
    __tablename__ = 'cash_register_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    opening_amount = Column(Numeric(12, 2), nullable=False)
    closing_amount = Column(Numeric(12, 2))
    expected_amount = Column(Numeric(12, 2))
    variance = Column(Numeric(12, 2))
    status = Column(String, default='OPEN')  # OPEN, CLOSED
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime)
    notes = Column(String)


class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    sale_number = Column(String, unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    total_amount = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    final_amount = Column(Numeric(12, 2), nullable=False)
    payment_status = Column(String, default='PENDING')
    sale_status = Column(String, default='COMPLETED')
    coupon_code = Column(String)
    coupon_discount = Column(Numeric(12, 2), default=0)
    total_cost_basis = Column(Numeric(12, 2))
    gross_profit = Column(Numeric(12, 2))
    profit_margin_percent = Column(Numeric(5, 2))
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale")
    returns = relationship("Return", back_populates="sale")
    
    def calculate_profit(self):
        """Calculate gross profit and margin"""
        if self.total_cost_basis and self.final_amount:
            self.gross_profit = self.final_amount - self.total_cost_basis
            self.profit_margin_percent = (self.gross_profit / self.final_amount * 100) if self.final_amount > 0 else 0


class SaleItem(Base):
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    saree_id = Column(Integer, ForeignKey('sarees.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    cost_price = Column(Numeric(12, 2))
    discount = Column(Numeric(12, 2), default=0)
    tax = Column(Numeric(12, 2), default=0)
    subtotal = Column(Numeric(12, 2), nullable=False)
    
    sale = relationship("Sale", back_populates="items")
    saree = relationship("Saree", back_populates="sale_items")
    return_items = relationship("ReturnItem", back_populates="sale_item")


class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, default='INR')
    method = Column(String, nullable=False)  # CASH, UPI, CARD, BANK_TRANSFER, ONLINE
    status = Column(String, default='PENDING')
    provider = Column(String)
    provider_transaction_id = Column(String)
    reference_id = Column(String)
    payment_metadata = Column(JSONB)  # Renamed from metadata to avoid conflict
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    sale = relationship("Sale", back_populates="payments")


class Return(Base):
    __tablename__ = 'returns'
    
    id = Column(Integer, primary_key=True)
    return_number = Column(String, unique=True, nullable=False)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    total_refund_amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default='PENDING')
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    sale = relationship("Sale", back_populates="returns")
    customer = relationship("Customer", back_populates="returns")
    items = relationship("ReturnItem", back_populates="return", cascade="all, delete-orphan")


class ReturnItem(Base):
    __tablename__ = 'return_items'
    
    id = Column(Integer, primary_key=True)
    return_id = Column(Integer, ForeignKey('returns.id'), nullable=False)
    sale_item_id = Column(Integer, ForeignKey('sale_items.id'), nullable=False)
    saree_id = Column(Integer, ForeignKey('sarees.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    condition = Column(String, nullable=False)  # RESELLABLE, DAMAGED
    refund_amount = Column(Numeric(12, 2), nullable=False)
    
    return_obj = relationship("Return", back_populates="items", foreign_keys=[return_id])
    sale_item = relationship("SaleItem", back_populates="return_items")
    saree = relationship("Saree", back_populates="return_items")


class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    role = relationship("Role", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="audit_logs")


# Indexes
Index('ix_sarees_sku', Saree.sku)
Index('ix_sarees_barcode', Saree.barcode)
Index('ix_sarees_weave_type', Saree.weave_type)
Index('ix_sarees_occasion', Saree.occasion)
Index('ix_sarees_loom_type', Saree.loom_type)
Index('ix_inventory_saree_id', Inventory.saree_id)
Index('ix_inventory_last_sold', Inventory.last_sold_date)
Index('ix_inventory_first_received', Inventory.first_received_date)
Index('ix_stock_transactions_saree_id', StockTransaction.saree_id)
Index('ix_stock_transactions_type', StockTransaction.transaction_type)
Index('ix_customers_phone', Customer.phone)
Index('ix_coupons_code', Coupon.code)
Index('ix_expenses_date', Expense.date)
Index('ix_sales_sale_number', Sale.sale_number)
Index('ix_sales_created_at', Sale.created_at)
Index('ix_sale_items_sale_id', SaleItem.sale_id)
Index('ix_sale_items_saree_id', SaleItem.saree_id)
Index('ix_payments_sale_id', Payment.sale_id)
Index('ix_returns_return_number', Return.return_number)
Index('ix_audit_logs_user_id', AuditLog.user_id)
Index('ix_audit_logs_entity', AuditLog.entity_type, AuditLog.entity_id)
Index('ix_audit_logs_created_at', AuditLog.created_at)
