import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { UserInfo, LoginRequest, RegisterRequest, AuthContextType } from '@/types';
import request from '@/utils/request';
import { message } from 'antd';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'magic_school_token';
const USER_KEY = 'magic_school_user';

// 本地存储工具
const storage = {
  getToken: (): string | null => localStorage.getItem(TOKEN_KEY),
  setToken: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  removeToken: () => localStorage.removeItem(TOKEN_KEY),
  getUser: (): UserInfo | null => {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },
  setUser: (user: UserInfo) => localStorage.setItem(USER_KEY, JSON.stringify(user)),
  removeUser: () => localStorage.removeItem(USER_KEY),
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(storage.getUser());
  const [token, setToken] = useState<string | null>(storage.getToken());
  const [isLoading, setIsLoading] = useState(false);

  const isAuthenticated = !!token && !!user;

  // 初始化时检查 token 有效性
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          // 验证 token 是否有效
          await refreshUserInfo();
        } catch (error) {
          // token 无效，清除认证信息
          logout();
        }
      }
    };
    initAuth();
  }, []);

  // 登录
  const login = useCallback(async (credentials: LoginRequest) => {
    setIsLoading(true);
    try {
      const response = await request.post('/auth/login', credentials);
      
      if (response.success) {
        const { access_token, user: userData } = response.data;
        
        // 保存到状态
        setToken(access_token);
        setUser(userData);
        
        // 保存到本地存储
        storage.setToken(access_token);
        storage.setUser(userData);
        
        message.success('登录成功！');
      } else {
        throw new Error(response.message || '登录失败');
      }
    } catch (error: any) {
      console.error('Login error:', error);
      message.error(error.response?.data?.message || error.message || '登录失败，请检查用户名和密码');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 注册
  const register = useCallback(async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      const response = await request.post('/auth/register', data);
      
      if (response.success) {
        const { access_token, user: userData } = response.data;
        
        // 保存到状态
        setToken(access_token);
        setUser(userData);
        
        // 保存到本地存储
        storage.setToken(access_token);
        storage.setUser(userData);
        
        message.success('注册成功！');
      } else {
        throw new Error(response.message || '注册失败');
      }
    } catch (error: any) {
      console.error('Register error:', error);
      message.error(error.response?.data?.message || error.message || '注册失败，请稍后重试');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 登出
  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    storage.removeToken();
    storage.removeUser();
    message.info('已退出登录');
  }, []);

  // 刷新用户信息
  const refreshUserInfo = useCallback(async () => {
    if (!token) {
      throw new Error('未登录');
    }

    try {
      const response = await request.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.success) {
        const userData = response.data;
        setUser(userData);
        storage.setUser(userData);
      } else {
        throw new Error(response.message || '获取用户信息失败');
      }
    } catch (error: any) {
      console.error('Refresh user info error:', error);
      throw error;
    }
  }, [token]);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    refreshUserInfo,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 自定义 Hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// 导出存储工具（供 API 拦截器使用）
export { storage as authStorage };
