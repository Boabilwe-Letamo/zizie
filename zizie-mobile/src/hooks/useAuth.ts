/**
 * Auth Hook - Authentication and user management
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { StorageService } from '../services/storage';


export interface User {
  id: string;
  email: string;
  full_name?: string;
  phone?: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  error: string | null;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    error: null,
  });
  
  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);
  
  const checkAuth = async () => {
    const token = await StorageService.get('auth_token');
    
    if (token) {
      // Verify token is still valid
      // In production, make API call to verify
      setState({
        isAuthenticated: true,
        isLoading: false,
        user: null,
        error: null,
      });
    } else {
      setState(prev => ({
        ...prev,
        isLoading: false,
      }));
    }
  };
  
  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));
    
    try {
      const result = await apiService.login(email, password);
      
      setState({
        isAuthenticated: true,
        isLoading: false,
        user: {
          id: result.user_id,
          email,
        },
        error: null,
      });
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Login failed',
      }));
      throw error;
    }
  }, []);
  
  const register = useCallback(async (email: string, password: string, fullName?: string) => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));
    
    try {
      await apiService.register(email, password, fullName);
      
      // Auto-login after registration
      await login(email, password);
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Registration failed',
      }));
      throw error;
    }
  }, [login]);
  
  const logout = useCallback(async () => {
    try {
      await apiService.logout();
    } finally {
      setState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: null,
      });
    }
  }, []);
  
  const value: AuthContextValue = {
    ...state,
    login,
    register,
    logout,
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default useAuth;