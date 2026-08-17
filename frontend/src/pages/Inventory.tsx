import { useEffect, useState } from 'react';
import { intelligenceService, sareeService } from '../services/api';
import { Saree, InventoryAging, DeadStockItem, ReorderRecommendation } from '../types';

export default function Inventory() {
  const [sarees, setSarees] = useState<Saree[]>([]);
  const [aging, setAging] = useState<InventoryAging[]>([]);
  const [deadStock, setDeadStock] = useState<DeadStockItem[]>([]);
  const [reorders, setReorders] = useState<ReorderRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'aging' | 'deadstock' | 'reorder'>('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [sareesData, agingData, deadStockData, reorderData] = await Promise.all([
        sareeService.getAll(),
        intelligenceService.getInventoryAging().catch(() => []),
        intelligenceService.getDeadStock().catch(() => []),
        intelligenceService.getReorderRecommendations().catch(() => []),
      ]);
      setSarees(sareesData.items || sareesData);
      setAging(agingData);
      setDeadStock(deadStockData);
      setReorders(reorderData);
    } catch (error) {
      console.error('Failed to load inventory data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  const totalValue = sarees.reduce((sum, s) => sum + (s.purchase_price * s.stock_quantity), 0);
  const lowStockCount = sarees.filter(s => s.stock_quantity <= s.reorder_level).length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'aging', label: 'Inventory Aging' },
            { id: 'deadstock', label: 'Dead Stock' },
            { id: 'reorder', label: 'Reorder Alerts' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <p className="text-sm text-gray-600">Total Products</p>
              <p className="text-3xl font-bold text-gray-900">{sarees.length}</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <p className="text-sm text-gray-600">Inventory Value</p>
              <p className="text-3xl font-bold text-gray-900">₹{totalValue.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <p className="text-sm text-gray-600">Low Stock Items</p>
              <p className="text-3xl font-bold text-red-600">{lowStockCount}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 border-b">
              <h2 className="text-lg font-semibold">All Products</h2>
            </div>
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Stock</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Value</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {sarees.map((saree) => (
                  <tr key={saree.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-mono">{saree.sku}</td>
                    <td className="px-6 py-4 text-sm font-medium">{saree.name}</td>
                    <td className="px-6 py-4 text-sm text-right">{saree.stock_quantity}</td>
                    <td className="px-6 py-4 text-sm text-right">₹{(saree.purchase_price * saree.stock_quantity).toLocaleString()}</td>
                    <td className="px-6 py-4 text-center">
                      {saree.stock_quantity === 0 ? (
                        <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs">Out of Stock</span>
                      ) : saree.stock_quantity <= saree.reorder_level ? (
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs">Low Stock</span>
                      ) : (
                        <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">In Stock</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Aging Tab */}
      {activeTab === 'aging' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Inventory Aging Analysis</h2>
          {aging.length > 0 ? (
            <div className="space-y-4">
              {aging.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{item.age_bucket}</p>
                    <p className="text-sm text-gray-500">{item.count} items</p>
                  </div>
                  <p className="text-lg font-semibold">₹{item.value.toLocaleString()}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No aging data available. Make some sales to see analysis.</p>
          )}
        </div>
      )}

      {/* Dead Stock Tab */}
      {activeTab === 'deadstock' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-red-600">Dead Stock Alert</h2>
          {deadStock.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Stock</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Days No Sale</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Value at Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {deadStock.map((item, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 text-sm">{item.product_name}</td>
                    <td className="px-6 py-4 text-sm font-mono">{item.sku}</td>
                    <td className="px-6 py-4 text-sm text-right">{item.stock_quantity}</td>
                    <td className="px-6 py-4 text-sm text-right">
                      <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs">{item.days_since_last_sale} days</span>
                    </td>
                    <td className="px-6 py-4 text-sm text-right font-semibold text-red-600">₹{item.inventory_value.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-500 text-center py-8">No dead stock detected. Great job!</p>
          )}
        </div>
      )}

      {/* Reorder Tab */}
      {activeTab === 'reorder' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-orange-600">Smart Reorder Recommendations</h2>
          {reorders.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Current</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Reorder Point</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Order Qty</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Priority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reorders.map((item) => (
                  <tr key={item.product_id}>
                    <td className="px-6 py-4 text-sm">{item.product_name}</td>
                    <td className="px-6 py-4 text-sm font-mono">{item.sku}</td>
                    <td className="px-6 py-4 text-sm text-right">{item.current_stock}</td>
                    <td className="px-6 py-4 text-sm text-right">{item.reorder_point}</td>
                    <td className="px-6 py-4 text-sm text-right font-medium">{item.recommended_quantity}</td>
                    <td className="px-6 py-4 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        item.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
                        item.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {item.priority}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-500 text-center py-8">No reorder recommendations at this time.</p>
          )}
        </div>
      )}
    </div>
  );
}
