import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuth } from '../App';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProfilePage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    // Parse fragment from URL
    const fragment = location.hash;
    if (fragment && fragment.includes('session_id=')) {
      const sessionId = fragment.split('session_id=')[1];
      if (sessionId) {
        handleGoogleAuth(sessionId);
      }
    } else {
      // No session ID found, redirect to login
      toast.error('Authentication failed - no session data received');
      navigate('/login');
    }
  }, [location, navigate]);

  const handleGoogleAuth = async (sessionId) => {
    try {
      toast.info('Processing Google authentication...');
      
      // Call backend to validate session and create user
      const response = await fetch(`${API}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for cookies
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Login successful, update auth context
        login(data.user, data.access_token);
        
        toast.success(`Welcome, ${data.user.name}! Signed in with Google.`);
        
        // Redirect based on user role
        if (data.user.role === 'admin') {
          navigate('/admin/dashboard');
        } else {
          navigate('/dashboard');
        }
      } else {
        toast.error(data.detail || 'Google authentication failed');
        navigate('/login');
      }
    } catch (error) {
      console.error('Google auth error:', error);
      toast.error('Google authentication failed - please try again');
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto"></div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Processing Authentication</h2>
          <p className="mt-2 text-gray-600">
            Please wait while we verify your Google account...
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;