import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User, LoginCredentials, RegisterData } from '../types';
import { authApi } from '../api';
import { setTokens, removeTokens, setUser as saveUser, getUser, getAccessToken, isTokenExpired } from '../utils/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUserState] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = () => {
      try {
        const token = getAccessToken();
        if (token && !isTokenExpired(token)) {
          const storedUser = getUser();
          if (storedUser) {
            setUserState(storedUser);
          }
        } else {
          // Token is expired or missing, clear storage
          removeTokens();
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        removeTokens();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      // Handle both nested (tokens.access) and flat (response.access) response structures
      const tokens = response.tokens || response;
      setTokens(tokens.access, tokens.refresh);
      saveUser(tokens.user);
      setUserState(tokens.user);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const response = await authApi.register(data);
      // Handle both nested (tokens.access) and flat (response.access) response structures
      const tokens = response.tokens || response;
      setTokens(tokens.access, tokens.refresh);
      saveUser(tokens.user);
      setUserState(tokens.user);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    removeTokens();
    setUserState(null);
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};