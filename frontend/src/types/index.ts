export interface Saree {
  id: number;
  sku: string;
  barcode: string;
  name: string;
  brand_id?: number;
  category_id?: number;
  fabric_id?: number;
  color_id?: number;
  design_id?: number;
  purchase_price: number;
  selling_price: number;
  stock_quantity: number;
  reorder_level: number;
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'ADMIN' | 'MANAGER' | 'STAFF';
}

export interface Sale {
  id: number;
  sale_number: string;
  customer_id?: number;
  total_amount: number;
  discount: number;
  tax: number;
  payment_status: 'PENDING' | 'PAID' | 'PARTIALLY_PAID' | 'REFUNDED';
  sale_status: 'COMPLETED' | 'CANCELLED' | 'RETURNED';
  created_at: string;
}

export interface InventoryAging {
  age_bucket: string;
  count: number;
  value: number;
}

export interface DeadStockItem {
  product_id: number;
  product_name: string;
  sku: string;
  stock_quantity: number;
  days_since_last_sale: number;
  inventory_value: number;
}

export interface ReorderRecommendation {
  product_id: number;
  product_name: string;
  sku: string;
  current_stock: number;
  reorder_point: number;
  recommended_quantity: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface CustomerRFM {
  customer_id: number;
  customer_name: string;
  recency_score: number;
  frequency_score: number;
  monetary_score: number;
  rfm_score: number;
  segment: 'VIP' | 'LOYAL' | 'NEW' | 'AT_RISK' | 'LOST';
}

export interface DashboardStats {
  today_sales: number;
  total_sales: number;
  inventory_count: number;
  inventory_value: number;
  low_stock_products: number;
  dead_stock_count: number;
  pending_purchases: number;
  customer_count: number;
}
