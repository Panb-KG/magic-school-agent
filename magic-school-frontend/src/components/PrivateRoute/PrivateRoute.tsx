import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import type { UserRole } from '@/types';

interface PrivateRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, allowedRoles }) => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  // 加载中
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  // 未登录，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 检查角色权限
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    // 角色不匹配，重定向到合适的页面
    if (user.role === 'student') {
      return <Navigate to="/dashboard" replace />;
    } else if (user.role === 'parent') {
      return <Navigate to="/parent/dashboard" replace />;
    }
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;
