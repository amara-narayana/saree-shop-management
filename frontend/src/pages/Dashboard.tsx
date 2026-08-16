import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { intelligenceService } from '../services/api';
import { DashboardStats, InventoryAging, DeadStockItem, ReorderRecommendation } from '../types';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [aging, setAging] = useState<InventoryAging[]>([]);
  const [deadStock, setDeadStock] = useState<DeadStockItem[]>([]);
  const [reorders, setReorders] = useState<ReorderRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsData, agingData, deadStockData, reorderData] = await Promise.all([
        intelligenceService.getDashboardSummary(),
        intelligenceService.getInventoryAging(),
        intelligenceService.getDeadStock(),
        intelligenceService.getReorderRecommendations(),
      ]);
      setStats(statsData);
      setAging(agingData);
      setDeadStock(deadStockData.slice(0, 5));
      setReorders(reorderData.slice(0, 5));
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Business Intelligence Overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Today's Sales"
          value={`₹${stats?.today_sales.toLocaleString() || '0'}`}
          icon="💰"
          color="from-green-500 to-emerald-600"
        />
        <StatCard
          title="Total Inventory Value"
          value={`₹${stats?.inventory_value.toLocaleString() || '0'}`}
          icon="📦"
          color="from-blue-500 to-indigo-600"
        />
        <StatCard
          title="Low Stock Items"
          value={stats?.low_stock_products.toString() || '0'}
          icon="⚠️"
          color="from-yellow-500 to-orange-600"
        />
        <StatCard
          title="Dead Stock"
          value={stats?.dead_stock_count.toString() || '0'}
          icon="🔴"
          color="from-red-500 to-pink-600"
        />
      </div>

      {/* Intelligence Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inventory Aging */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <span>📊</span> Inventory Aging Analysis
          </h2>
          <div className="space-y-3">
            {aging.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <span className="font-medium text-gray-700 dark:text-gray-300">{item.age_bucket}</span>
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">{item.count} items</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">₹{item.value.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Reorder Recommendations */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <span>🔔</span> Smart Reorder Recommendations
          </h2>
          <div className="space-y-3">
            {reorders.length > 0 ? (
              reorders.map((item) => (
                <div key={item.product_id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{item.product_name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{item.sku}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      item.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
                      item.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {item.priority}
                    </span>
                    <p className="text-xs mt-1 text-gray-600 dark:text-gray-400">
                      Order: {item.recommended_quantity} units
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 dark:text-gray-400 text-center py-4">No reorder recommendations</p>
            )}
          </div>
        </div>
      </div>

      {/* Dead Stock */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🔴</span> Dead Stock Alert
          </h2>
          <Link to="/inventory" className="text-sm text-purple-600 hover:text-purple-700 font-medium">
            View All →
          </Link>
        </div>
        {deadStock.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm font-medium text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                  <th className="pb-3">Product</th>
                  <th className="pb-3">SKU</th>
                  <th className="pb-3">Stock</th>
                  <th className="pb-3">Days Since Sale</th>
                  <th className="pb-3 text-right">Value at Risk</th>
                </tr>
              </thead>
              <tbody>
                {deadStock.map((item) => (
                  <tr key={item.product_id} className="border-b dark:border-gray-700 last:border-0">
                    <td className="py-3 text-gray-900 dark:text-white">{item.product_name}</td>
                    <td className="py-3 text-gray-600 dark:text-gray-400 font-mono text-sm">{item.sku}</td>
                    <td className="py-3 text-gray-600 dark:text-gray-400">{item.stock_quantity}</td>
                    <td className="py-3">
                      <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full text-xs font-medium">
                        {item.days_since_last_sale} days
                      </span>
                    </td>
                    <td className="py-3 text-right font-semibold text-red-600 dark:text-red-400">
                      ₹{item.inventory_value.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 dark:text-gray-400 text-center py-4">No dead stock detected</p>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string; value: string; icon: string; color: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <span className="text-3xl">{icon}</span>
        <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${color} opacity-20`}></div>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
    </div>
  );
}
