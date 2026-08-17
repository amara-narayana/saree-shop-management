import { useEffect, useState } from 'react';
import { sareeService, saleService } from '../services/api';
import { Saree } from '../types';

interface CartItem extends Saree {
  quantity: number;
}

export default function POS() {
  const [sarees, setSarees] = useState<Saree[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [discount, setDiscount] = useState(0);
  const [showSuccess, setShowSuccess] = useState(false);

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

  const addToCart = (saree: Saree) => {
    if (saree.stock_quantity === 0) return;
    
    setCart(prev => {
      const existing = prev.find(item => item.id === saree.id);
      if (existing) {
        if (existing.quantity >= saree.stock_quantity) return prev;
        return prev.map(item => 
          item.id === saree.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { ...saree, quantity: 1 }];
    });
  };

  const removeFromCart = (id: number) => {
    setCart(prev => prev.filter(item => item.id !== id));
  };

  const updateQuantity = (id: number, delta: number) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQty = Math.max(1, Math.min(item.stock_quantity, item.quantity + delta));
        return { ...item, quantity: newQty };
      }
      return item;
    }));
  };

  const subtotal = cart.reduce((sum, item) => sum + (item.selling_price * item.quantity), 0);
  const total = Math.max(0, subtotal - discount);

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    
    setProcessing(true);
    try {
      const saleData = {
        items: cart.map(item => ({
          saree_id: item.id,
          quantity: item.quantity,
          selling_price: item.selling_price,
        })),
        customer_name: customerName || 'Walk-in Customer',
        discount: discount,
        payment_method: 'CASH',
      };
      
      await saleService.create(saleData);
      setShowSuccess(true);
      setCart([]);
      setCustomerName('');
      setDiscount(0);
      loadSarees();
      
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to create sale:', error);
      alert('Failed to process sale');
    } finally {
      setProcessing(false);
    }
  };

  const filteredSarees = sarees.filter(s => 
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.barcode?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-140px)]">
      {/* Products */}
      <div className="flex-1 flex flex-col">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search by name, SKU, or barcode..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500"
          />
        </div>
        
        <div className="flex-1 overflow-y-auto grid grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSarees.map((saree) => (
            <button
              key={saree.id}
              onClick={() => addToCart(saree)}
              disabled={saree.stock_quantity === 0}
              className={`p-4 rounded-xl border-2 text-left transition-all ${
                saree.stock_quantity === 0
                  ? 'border-gray-200 bg-gray-100 opacity-50 cursor-not-allowed'
                  : 'border-gray-200 hover:border-purple-500 hover:shadow-lg'
              }`}
            >
              <p className="font-medium text-sm mb-1">{saree.name}</p>
              <p className="text-xs text-gray-500 mb-2">{saree.sku}</p>
              <div className="flex justify-between items-center">
                <span className="font-bold text-purple-600">₹{saree.selling_price.toLocaleString()}</span>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  saree.stock_quantity === 0 ? 'bg-red-100 text-red-700' :
                  saree.stock_quantity <= saree.reorder_level ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {saree.stock_quantity === 0 ? 'Out' : `${saree.stock_quantity} left`}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Cart */}
      <div className="w-96 bg-white rounded-xl shadow-lg flex flex-col">
        <div className="p-4 border-b">
          <h2 className="text-xl font-bold">Current Sale</h2>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {cart.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Cart is empty</p>
          ) : (
            cart.map((item) => (
              <div key={item.id} className="flex justify-between items-start p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-sm">{item.name}</p>
                  <p className="text-xs text-gray-500">{item.sku}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <button
                      onClick={() => updateQuantity(item.id, -1)}
                      className="w-6 h-6 rounded bg-gray-200 hover:bg-gray-300"
                    >-</button>
                    <span className="text-sm font-medium">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, 1)}
                      className="w-6 h-6 rounded bg-gray-200 hover:bg-gray-300"
                    >+</button>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">₹{(item.selling_price * item.quantity).toLocaleString()}</p>
                  <button
                    onClick={() => removeFromCart(item.id)}
                    className="text-xs text-red-600 hover:text-red-700 mt-1"
                  >Remove</button>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="p-4 border-t space-y-3">
          <input
            type="text"
            placeholder="Customer Name (optional)"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg text-sm"
          />
          
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Discount:</label>
            <input
              type="number"
              value={discount}
              onChange={(e) => setDiscount(parseFloat(e.target.value) || 0)}
              className="w-24 px-3 py-2 border rounded-lg text-sm"
              min="0"
              max={subtotal}
            />
          </div>

          <div className="flex justify-between items-center pt-3 border-t">
            <span className="text-gray-600">Subtotal:</span>
            <span className="font-medium">₹{subtotal.toLocaleString()}</span>
          </div>
          
          <div className="flex justify-between items-center text-lg font-bold">
            <span>Total:</span>
            <span className="text-purple-600">₹{total.toLocaleString()}</span>
          </div>

          <button
            onClick={handleCheckout}
            disabled={cart.length === 0 || processing}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {processing ? 'Processing...' : 'Complete Sale'}
          </button>
        </div>
      </div>

      {/* Success Toast */}
      {showSuccess && (
        <div className="fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg animate-pulse">
          ✓ Sale completed successfully!
        </div>
      )}
    </div>
  );
}
