'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, Session, UserRole } from '@/types';

interface AuthContextType {
  session: Session | null;
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock users for demo
const MOCK_USERS: Record<string, { password: string; user: User }> = {
  'admin@rag.dev': {
    password: 'admin123',
    user: {
      id: 'user-admin-001',
      email: 'admin@rag.dev',
      name: 'Admin User',
      role: 'admin' as UserRole,
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin',
      createdAt: new Date('2024-01-01'),
    },
  },
  'demo@rag.dev': {
    password: 'demo123',
    user: {
      id: 'user-demo-001',
      email: 'demo@rag.dev',
      name: 'Demo User',
      role: 'user' as UserRole,
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo',
      createdAt: new Date('2024-01-15'),
    },
  },
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize session from localStorage
  useEffect(() => {
    const storedSession = localStorage.getItem('rag-session');
    if (storedSession) {
      try {
        const parsedSession = JSON.parse(storedSession);
        // Check if session hasn't expired
        if (new Date(parsedSession.expiresAt) > new Date()) {
          setSession(parsedSession);
        } else {
          localStorage.removeItem('rag-session');
        }
      } catch (error) {
        console.error('Failed to parse stored session:', error);
        localStorage.removeItem('rag-session');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 800));

    const mockUser = MOCK_USERS[email];
    if (!mockUser || mockUser.password !== password) {
      throw new Error('Invalid email or password');
    }

    const newSession: Session = {
      user: mockUser.user,
      token: `mock-token-${Date.now()}`,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
    };

    setSession(newSession);
    localStorage.setItem('rag-session', JSON.stringify(newSession));
    setIsLoading(false);
  };

  const logout = () => {
    setSession(null);
    localStorage.removeItem('rag-session');
  };

  return React.createElement(
    AuthContext.Provider,
    {
      value: {
        session,
        user: session?.user || null,
        isLoading,
        login,
        logout,
        isAuthenticated: !!session,
      },
    },
    children
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};




