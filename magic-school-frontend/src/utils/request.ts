import axios from 'axios';
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { authStorage } from '@/contexts/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api/v1';

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：自动添加 JWT token
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authStorage.getToken();
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理 401 错误
request.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error: AxiosError) => {
    // 统一错误处理
    if (error.response) {
      const status = error.response.status;
      
      // 处理 401 未授权错误
      if (status === 401) {
        // 清除本地存储的认证信息
        authStorage.removeToken();
        authStorage.removeUser();
        
        // 重定向到登录页（如果不是已经在登录页）
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
          window.location.href = '/login';
        }
      }
      
      console.error('API Error:', status, error.response.data);
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('Network Error:', error.message);
    } else {
      // 请求配置错误
      console.error('Request Error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default request;
