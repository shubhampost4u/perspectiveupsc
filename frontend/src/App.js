import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage";
import ForgotPassword from "./components/ForgotPassword";
import AdminDashboard from "./components/AdminDashboard";
import StudentDashboard from "./components/StudentDashboard";
import TestTaking from "./components/TestTaking";
import { Toaster } from "./components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = (token, user) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    setToken(token);
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!token,
    isAdmin: user?.role === 'admin',
    isStudent: user?.role === 'student'
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isAdmin } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Public Route (redirect if already logged in)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isAdmin } = useAuth();

  if (isAuthenticated) {
    return <Navigate to={isAdmin ? "/admin" : "/dashboard"} replace />;
  }

  return children;
};

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            } />
            <Route path="/register" element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            } />
            
            <Route path="/forgot-password" element={
              <PublicRoute>
                <ForgotPassword />
              </PublicRoute>
            } />

            {/* Protected Routes */}
            <Route path="/admin" element={
              <ProtectedRoute requireAdmin={true}>
                <AdminDashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <StudentDashboard />
              </ProtectedRoute>
            } />

            <Route path="/test/:testId" element={
              <ProtectedRoute>
                <TestTaking />
              </ProtectedRoute>
            } />

            {/* Default redirect */}
            <Route path="/" element={
              <Navigate to="/login" replace />
            } />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </AuthProvider>
    </div>
  );
}

export default App;