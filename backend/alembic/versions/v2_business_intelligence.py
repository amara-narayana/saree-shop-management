"""Add advanced saree attributes, inventory aging, and loyalty features

Revision ID: v2_business_intelligence
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'v2_business_intelligence'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create all V1 tables first (simplified for this migration)
    
    # 1. Enhanced Sarees table with advanced attributes
    op.create_table('sarees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(), unique=True, nullable=False),
        sa.Column('barcode', sa.String(), unique=True, nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('fabric_id', sa.Integer(), nullable=True),
        sa.Column('color_id', sa.Integer(), nullable=True),
        sa.Column('design_id', sa.Integer(), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('selling_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), default=0),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('reorder_level', sa.Integer(), default=5),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        # V2 Advanced Attributes
        sa.Column('weave_type', sa.String(), nullable=True),
        sa.Column('border_type', sa.String(), nullable=True),
        sa.Column('blouse_included', sa.Boolean(), default=False),
        sa.Column('length_meters', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('weight_grams', sa.Integer(), nullable=True),
        sa.Column('occasion', sa.String(), nullable=True),
        sa.Column('season', sa.String(), nullable=True),
        sa.Column('region_origin', sa.String(), nullable=True),
        sa.Column('loom_type', sa.String(), nullable=True),
        sa.Column('designer', sa.String(), nullable=True),
        sa.Column('collection_name', sa.String(), nullable=True),
        sa.Column('batch_number', sa.String(), nullable=True),
        sa.Column('lot_number', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sarees_sku', 'sarees', ['sku'])
    op.create_index('ix_sarees_barcode', 'sarees', ['barcode'])
    op.create_index('ix_sarees_weave_type', 'sarees', ['weave_type'])
    op.create_index('ix_sarees_occasion', 'sarees', ['occasion'])
    op.create_index('ix_sarees_loom_type', 'sarees', ['loom_type'])

    # Supporting tables
    op.create_table('brands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('fabrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('colors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('hex_code', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('designs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Inventory with Aging and Cost Tracking
    op.create_table('inventory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('saree_id', sa.Integer(), sa.ForeignKey('sarees.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), default=0),
        sa.Column('reserved_quantity', sa.Integer(), default=0),
        sa.Column('first_received_date', sa.DateTime(), nullable=True),
        sa.Column('last_sold_date', sa.DateTime(), nullable=True),
        sa.Column('average_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_inventory_saree_id', 'inventory', ['saree_id'])
    op.create_index('ix_inventory_last_sold', 'inventory', ['last_sold_date'])
    op.create_index('ix_inventory_first_received', 'inventory', ['first_received_date'])

    # 3. Stock Transactions
    op.create_table('stock_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('saree_id', sa.Integer(), sa.ForeignKey('sarees.id'), nullable=False),
        sa.Column('transaction_type', sa.String(), nullable=False),
        sa.Column('quantity_change', sa.Integer(), nullable=False),
        sa.Column('quantity_before', sa.Integer(), nullable=False),
        sa.Column('quantity_after', sa.Integer(), nullable=False),
        sa.Column('reference_type', sa.String(), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stock_transactions_saree_id', 'stock_transactions', ['saree_id'])
    op.create_index('ix_stock_transactions_type', 'stock_transactions', ['transaction_type'])

    # 4. Suppliers with Performance Metrics
    op.create_table('suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('gst_number', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        # V2 Performance Metrics
        sa.Column('avg_lead_time_days', sa.Float(), nullable=True),
        sa.Column('on_time_delivery_rate', sa.Float(), nullable=True),
        sa.Column('defect_rate', sa.Float(), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Customers with Loyalty Program
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        # V2 Loyalty Fields
        sa.Column('loyalty_points', sa.Integer(), default=0),
        sa.Column('membership_tier', sa.String(), default='REGULAR'),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('anniversary_date', sa.Date(), nullable=True),
        sa.Column('preferred_fabric', sa.String(), nullable=True),
        sa.Column('preferred_color', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_customers_phone', 'customers', ['phone'])

    # 6. Coupons Table
    op.create_table('coupons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), unique=True, nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('discount_type', sa.String(), nullable=False),
        sa.Column('value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_purchase_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('max_discount_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('applicable_categories', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('applicable_products', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_coupons_code', 'coupons', ['code'])

    # 7. Expense Categories and Expenses
    op.create_table('expense_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('expense_categories.id'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('receipt_image', sa.String(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_expenses_date', 'expenses', ['date'])

    # 8. Cash Register Sessions
    op.create_table('cash_register_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('opening_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('closing_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('expected_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('variance', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.String(), default='OPEN'),
        sa.Column('opened_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Sales with Profit Calculation
    op.create_table('sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sale_number', sa.String(), unique=True, nullable=False),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(precision=12, scale=2), default=0),
        sa.Column('tax_amount', sa.Numeric(precision=12, scale=2), default=0),
        sa.Column('final_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_status', sa.String(), default='PENDING'),
        sa.Column('sale_status', sa.String(), default='COMPLETED'),
        sa.Column('coupon_code', sa.String(), nullable=True),
        sa.Column('coupon_discount', sa.Numeric(precision=12, scale=2), default=0),
        sa.Column('total_cost_basis', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('gross_profit', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('profit_margin_percent', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sales_sale_number', 'sales', ['sale_number'])
    op.create_index('ix_sales_created_at', 'sales', ['created_at'])

    # 10. Sale Items
    op.create_table('sale_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id'), nullable=False),
        sa.Column('saree_id', sa.Integer(), sa.ForeignKey('sarees.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('cost_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('discount', sa.Numeric(precision=12, scale=2), default=0),
        sa.Column('tax', sa.Numeric(precision=12, scale=2), default=0),
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sale_items_sale_id', 'sale_items', ['sale_id'])
    op.create_index('ix_sale_items_saree_id', 'sale_items', ['saree_id'])

    # 11. Payments
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sa.String(), default='INR'),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('status', sa.String(), default='PENDING'),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('provider_transaction_id', sa.String(), nullable=True),
        sa.Column('reference_id', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payments_sale_id', 'payments', ['sale_id'])

    # 12. Returns
    op.create_table('returns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('return_number', sa.String(), unique=True, nullable=False),
        sa.Column('sale_id', sa.Integer(), sa.ForeignKey('sales.id'), nullable=False),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=True),
        sa.Column('total_refund_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('status', sa.String(), default='PENDING'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_returns_return_number', 'returns', ['return_number'])

    # 13. Return Items
    op.create_table('return_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('return_id', sa.Integer(), sa.ForeignKey('returns.id'), nullable=False),
        sa.Column('sale_item_id', sa.Integer(), sa.ForeignKey('sale_items.id'), nullable=False),
        sa.Column('saree_id', sa.Integer(), sa.ForeignKey('sarees.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('condition', sa.String(), nullable=False),
        sa.Column('refund_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. Users and Roles
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), unique=True, nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), unique=True, nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. Audit Logs
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('return_items')
    op.drop_table('returns')
    op.drop_table('payments')
    op.drop_table('sale_items')
    op.drop_table('sales')
    op.drop_table('cash_register_sessions')
    op.drop_table('expenses')
    op.drop_table('expense_categories')
    op.drop_table('coupons')
    op.drop_table('customers')
    op.drop_table('suppliers')
    op.drop_table('stock_transactions')
    op.drop_table('inventory')
    op.drop_table('designs')
    op.drop_table('colors')
    op.drop_table('fabrics')
    op.drop_table('categories')
    op.drop_table('brands')
    op.drop_table('sarees')
