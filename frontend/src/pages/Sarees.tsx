import { useEffect, useState } from 'react';
import { sareeService } from '../services/api';
import { Saree } from '../types';

export default function Sarees() {
  const [sarees, setSarees] = useState<Saree[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    barcode: '',
    purchase_price: 0,
    selling_price: 0,
    stock_quantity: 0,
    reorder_level: 5,
  });

  useEffect(() => {
    loadSarees();
  }, []);

  const loadSarees = async () => {
    try {
      const data = await sareeService.getAll();
      setSarees(data.items || data);
    } catch (error) {
      console.error('Failed to load sarees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await sareeService.create(formData);
      setShowForm(false);
      loadSarees();
      setFormData({
        name: '',
        sku: '',
        barcode: '',
        purchase_price: 0,
        selling_price: 0,
        stock_quantity: 0,
        reorder_level: 5,
      });
    } catch (error) {
      console.error('Failed to create saree:', error);
      alert('Failed to create saree');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Saree Catalog</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          {showForm ? 'Cancel' : '+ Add Saree'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Add New Saree</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Saree Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="border rounded-lg px-4 py-2"
              required
            />
            <input
              type="text"
              placeholder="SKU"
              value={formData.sku}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              className="border rounded-lg px-4 py-2"
              required
            />
            <input
              type="text"
              placeholder="Barcode"
              value={formData.barcode}
              onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
              className="border rounded-lg px-4 py-2"
            />
            <input
              type="number"
              placeholder="Purchase Price"
              value={formData.purchase_price}
              onChange={(e) => setFormData({ ...formData, purchase_price: parseFloat(e.target.value) || 0 })}
              className="border rounded-lg px-4 py-2"
              required
            />
            <input
              type="number"
              placeholder="Selling Price"
              value={formData.selling_price}
              onChange={(e) => setFormData({ ...formData, selling_price: parseFloat(e.target.value) || 0 })}
              className="border rounded-lg px-4 py-2"
              required
            />
            <input
              type="number"
              placeholder="Stock Quantity"
              value={formData.stock_quantity}
              onChange={(e) => setFormData({ ...formData, stock_quantity: parseInt(e.target.value) || 0 })}
              className="border rounded-lg px-4 py-2"
              required
            />
            <input
              type="number"
              placeholder="Reorder Level"
              value={formData.reorder_level}
              onChange={(e) => setFormData({ ...formData, reorder_level: parseInt(e.target.value) || 5 })}
              className="border rounded-lg px-4 py-2"
            />
            <button
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg col-span-full"
            >
              Save Saree
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Barcode</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Purchase</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Selling</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Stock</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sarees.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                  No sarees found. Add your first saree!
                </td>
              </tr>
            ) : (
              sarees.map((saree) => (
                <tr key={saree.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-mono text-gray-900">{saree.sku}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{saree.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{saree.barcode || '-'}</td>
                  <td className="px-6 py-4 text-sm text-right text-gray-900">₹{saree.purchase_price.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-right font-medium text-gray-900">₹{saree.selling_price.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-right text-gray-900">{saree.stock_quantity}</td>
                  <td className="px-6 py-4 text-center">
                    {saree.stock_quantity <= saree.reorder_level ? (
                      <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">Low Stock</span>
                    ) : (
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">In Stock</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
