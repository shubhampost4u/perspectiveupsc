import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  ShoppingCart, 
  Trash2, 
  Plus, 
  Minus, 
  Tag,
  CreditCard,
  ArrowLeft,
  Gift
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../App';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Cart = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processingPayment, setProcessingPayment] = useState(false);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    if (user?.role !== 'student') {
      navigate('/login');
      return;
    }
    fetchCart();
  }, [user, navigate]);

  const fetchCart = async () => {
    try {
      const response = await axios.get(`${API}/cart`, axiosConfig);
      setCart(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
      toast.error('Failed to load cart');
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (testId) => {
    try {
      await axios.delete(`${API}/cart/remove/${testId}`, axiosConfig);
      toast.success('Test removed from cart');
      fetchCart(); // Refresh cart
    } catch (error) {
      console.error('Error removing from cart:', error);
      toast.error('Failed to remove test from cart');
    }
  };

  const clearCart = async () => {
    if (!window.confirm('Are you sure you want to clear your entire cart?')) {
      return;
    }

    try {
      await axios.delete(`${API}/cart/clear`, axiosConfig);
      toast.success('Cart cleared');
      fetchCart(); // Refresh cart
    } catch (error) {
      console.error('Error clearing cart:', error);
      toast.error('Failed to clear cart');
    }
  };

  const handleCheckout = async () => {
    if (!cart || cart.items.length === 0) {
      toast.error('Your cart is empty');
      return;
    }

    setProcessingPayment(true);
    try {
      // Create Razorpay order
      const response = await axios.post(`${API}/cart/checkout`, {}, axiosConfig);
      
      const options = {
        key: process.env.REACT_APP_RAZORPAY_KEY_ID || 'rzp_test_R9g6dBU2gHpJuC',
        amount: response.data.amount * 100,
        currency: response.data.currency,
        name: 'PerspectiveUPSC',
        description: `Bundle Purchase: ${response.data.test_count} tests`,
        order_id: response.data.order_id,
        handler: async function (razorpayResponse) {
          try {
            // Verify payment
            await axios.post(`${API}/cart/verify-payment`, {
              razorpay_order_id: razorpayResponse.razorpay_order_id,
              razorpay_payment_id: razorpayResponse.razorpay_payment_id,
              razorpay_signature: razorpayResponse.razorpay_signature
            }, axiosConfig);

            toast.success(`Bundle purchased successfully! You saved ₹${response.data.savings}!`);
            fetchCart(); // This should now show empty cart
            navigate('/dashboard');
          } catch (error) {
            console.error('Payment verification error:', error);
            toast.error('Payment verification failed');
          }
        },
        prefill: {
          name: user.name,
          email: user.email
        },
        theme: {
          color: '#4F46E5'
        },
        modal: {
          ondismiss: function() {
            setProcessingPayment(false);
          }
        }
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error('Failed to initiate checkout');
      setProcessingPayment(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your cart...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/student/dashboard')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <ShoppingCart className="w-8 h-8 mr-3 text-indigo-600" />
                Shopping Cart
              </h1>
              <p className="text-gray-600 mt-1">
                {cart?.items?.length || 0} test{(cart?.items?.length || 0) !== 1 ? 's' : ''} in your cart
              </p>
            </div>
          </div>
          
          {cart?.items && cart.items.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearCart}
              className="text-red-600 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear Cart
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart?.items && cart.items.length > 0 ? (
              cart.items.map((item) => (
                <Card key={item.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {item.test_title}
                        </h3>
                        <div className="flex items-center space-x-4">
                          <Badge variant="secondary" className="bg-green-100 text-green-800">
                            ₹{item.test_price}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            Added {new Date(item.added_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeFromCart(item.test_id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <ShoppingCart className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Your cart is empty</h3>
                  <p className="text-gray-600 mb-6">
                    Browse tests and add them to your cart to get started.
                  </p>
                  <Button onClick={() => navigate('/student/dashboard')}>
                    Browse Tests
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Tag className="w-5 h-5 mr-2" />
                  Order Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {cart && cart.items && cart.items.length > 0 ? (
                  <>
                    <div className="flex justify-between text-sm">
                      <span>Subtotal ({cart.items.length} test{cart.items.length !== 1 ? 's' : ''})</span>
                      <span>₹{cart.subtotal}</span>
                    </div>
                    
                    {cart.discount > 0 && (
                      <div className="flex justify-between text-sm text-green-600">
                        <span className="flex items-center">
                          <Gift className="w-4 h-4 mr-1" />
                          Bundle Discount
                        </span>
                        <span>-₹{cart.discount}</span>
                      </div>
                    )}
                    
                    <div className="border-t pt-4">
                      <div className="flex justify-between font-semibold text-lg">
                        <span>Total</span>
                        <span className="text-indigo-600">₹{cart.total}</span>
                      </div>
                      
                      {cart.savings > 0 && (
                        <p className="text-sm text-green-600 mt-2 font-medium">
                          You save ₹{cart.savings}!
                        </p>
                      )}
                    </div>
                    
                    <div className="bg-indigo-50 p-4 rounded-lg">
                      <p className="text-sm text-indigo-800 font-medium">
                        {cart.bundle_info}
                      </p>
                    </div>
                    
                    <Button
                      className="w-full"
                      onClick={handleCheckout}
                      disabled={processingPayment}
                    >
                      {processingPayment ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Processing...
                        </div>
                      ) : (
                        <>
                          <CreditCard className="w-4 h-4 mr-2" />
                          Checkout (₹{cart.total})
                        </>
                      )}
                    </Button>
                  </>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <p>Add tests to see pricing</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;