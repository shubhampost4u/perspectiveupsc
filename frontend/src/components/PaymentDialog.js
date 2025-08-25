import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { 
  CreditCard, 
  Smartphone, 
  Building, 
  Wallet, 
  Shield,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentDialog = ({ 
  isOpen, 
  onClose, 
  test, 
  user, 
  token, 
  onPaymentSuccess 
}) => {
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const loadRazorpay = () => {
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handlePayment = async () => {
    setLoading(true);
    
    try {
      // Load Razorpay script
      const scriptLoaded = await loadRazorpay();
      if (!scriptLoaded) {
        toast.error('Failed to load payment gateway');
        return;
      }

      // Create payment order
      const orderResponse = await axios.post(
        `${API}/tests/${test.id}/purchase`,
        {},
        axiosConfig
      );

      const { order_id, amount, currency, key_id, test_title, student_name, student_email } = orderResponse.data;

      // Razorpay options
      const options = {
        key: key_id,
        amount: amount,
        currency: currency,
        name: 'PerspectiveUPSC',
        description: `Payment for ${test_title}`,
        order_id: order_id,
        handler: async (response) => {
          setProcessing(true);
          try {
            // Verify payment
            await axios.post(`${API}/verify-payment`, {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            }, axiosConfig);

            toast.success('Payment successful! Test purchased successfully.');
            onPaymentSuccess();
            onClose();
          } catch (error) {
            console.error('Payment verification failed:', error);
            toast.error('Payment verification failed. Please contact support.');
          } finally {
            setProcessing(false);
          }
        },
        prefill: {
          name: student_name,
          email: student_email,
        },
        notes: {
          test_id: test.id,
          test_title: test_title
        },
        theme: {
          color: '#2563eb'
        },
        modal: {
          ondismiss: () => {
            setLoading(false);
            toast.info('Payment cancelled');
          }
        }
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();

    } catch (error) {
      console.error('Payment initiation failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to initiate payment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center">Complete Your Purchase</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Test Details */}
          <div className="text-center space-y-2">
            <h3 className="text-lg font-semibold text-gray-900">{test?.title}</h3>
            <p className="text-2xl font-bold text-blue-600">₹{test?.price}</p>
            <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{test?.duration_minutes} mins</span>
              </div>
              <div className="flex items-center space-x-1">
                <span>{test?.questions_count} questions</span>
              </div>
            </div>
          </div>

          {/* Payment Methods */}
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Supported Payment Methods:</h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center space-x-2 p-3 border rounded-lg bg-gray-50">
                <Smartphone className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium">UPI</span>
              </div>
              <div className="flex items-center space-x-2 p-3 border rounded-lg bg-gray-50">
                <CreditCard className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium">Cards</span>
              </div>
              <div className="flex items-center space-x-2 p-3 border rounded-lg bg-gray-50">
                <Building className="w-5 h-5 text-purple-600" />
                <span className="text-sm font-medium">Net Banking</span>
              </div>
              <div className="flex items-center space-x-2 p-3 border rounded-lg bg-gray-50">
                <Wallet className="w-5 h-5 text-orange-600" />
                <span className="text-sm font-medium">Wallets</span>
              </div>
            </div>
          </div>

          {/* Security Notice */}
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription className="text-sm">
              Your payment is secured by Razorpay with 256-bit SSL encryption. 
              We don't store your payment details.
            </AlertDescription>
          </Alert>

          {/* Processing State */}
          {processing && (
            <Alert>
              <Loader2 className="h-4 w-4 animate-spin" />
              <AlertDescription>
                Processing your payment... Please don't close this window.
              </AlertDescription>
            </Alert>
          )}

          {/* Payment Button */}
          <div className="space-y-3">
            <Button
              onClick={handlePayment}
              disabled={loading || processing}
              className="w-full h-12 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Initiating Payment...</span>
                </div>
              ) : processing ? (
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying Payment...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <CreditCard className="w-4 h-4" />
                  <span>Pay ₹{test?.price}</span>
                </div>
              )}
            </Button>
            
            <Button
              variant="outline"
              onClick={onClose}
              disabled={loading || processing}
              className="w-full"
            >
              Cancel
            </Button>
          </div>

          {/* Test Mode Notice */}
          <div className="text-center">
            <Badge variant="outline" className="text-xs text-gray-600">
              Test Mode - Use test cards for payment
            </Badge>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PaymentDialog;