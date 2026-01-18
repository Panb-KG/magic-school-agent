import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown } from 'antd';
import {
  UserOutlined,
  LogoutOutlined,
  DashboardOutlined,
  ScheduleOutlined,
  TrophyOutlined,
  BookOutlined,
  HomeOutlined,
  BrainOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import PrivateRoute from '@/components/PrivateRoute';
import {
  Dashboard,
  SchedulePage,
  AchievementsPage,
  HomeworkPage,
  LoginPage,
  RegisterPage,
  ParentDashboardPage,
  MemoryPage,
} from '@/pages';
import './App.css';

const { Header, Content, Footer } = Layout;

// 内部导航栏组件（需要认证）
const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: user?.role === 'parent' ? user?.real_name : user?.student_name || user?.username,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  // 根据用户角色返回不同的菜单项
  const getMenuItems = () => {
    if (user?.role === 'parent') {
      return [
        {
          key: 'parent-dashboard',
          icon: <TeamOutlined />,
          label: <Link to="/parent/dashboard">家长中心</Link>,
        },
        {
          key: 'memory',
          icon: <BrainOutlined />,
          label: <Link to="/memory">记忆中心</Link>,
        },
      ];
    } else {
      return [
        {
          key: 'dashboard',
          icon: <DashboardOutlined />,
          label: <Link to="/dashboard">仪表盘</Link>,
        },
        {
          key: 'schedule',
          icon: <ScheduleOutlined />,
          label: <Link to="/schedule">课程表</Link>,
        },
        {
          key: 'achievements',
          icon: <TrophyOutlined />,
          label: <Link to="/achievements">成就墙</Link>,
        },
        {
          key: 'homework',
          icon: <BookOutlined />,
          label: <Link to="/homework">作业</Link>,
        },
        {
          key: 'memory',
          icon: <BrainOutlined />,
          label: <Link to="/memory">记忆中心</Link>,
        },
      ];
    }
  };

  return (
    <Layout className="main-layout">
      <Header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">魔法学校</span>
          </div>

          <Menu
            mode="horizontal"
            theme="light"
            items={getMenuItems()}
            className="nav-menu"
            selectedKeys={[]}
          />

          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div className="user-info">
              <Avatar icon={<UserOutlined />} />
              <span className="username">
                {user?.role === 'parent' ? '家长' : '小巫师'}
              </span>
            </div>
          </Dropdown>
        </div>
      </Header>

      <Content className="app-content">{children}</Content>

      <Footer className="app-footer">
        <p>⚡ 魔法学校学习管理系统 · 让学习充满魔法</p>
        <p className="footer-text">© 2025 Magic School. All rights reserved.</p>
      </Footer>
    </Layout>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* 公开路由 */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* 受保护路由 - 需要认证 */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Navigate to="/dashboard" replace />
              </PrivateRoute>
            }
          />

          {/* 学生路由 */}
          <Route
            path="/dashboard/*"
            element={
              <PrivateRoute allowedRoles={['student']}>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                  </Routes>
                </MainLayout>
              </PrivateRoute>
            }
          />

          <Route
            path="/schedule/*"
            element={
              <PrivateRoute allowedRoles={['student']}>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<SchedulePage />} />
                  </Routes>
                </MainLayout>
              </PrivateRoute>
            }
          />

          <Route
            path="/achievements/*"
            element={
              <PrivateRoute allowedRoles={['student']}>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<AchievementsPage />} />
                  </Routes>
                </MainLayout>
              </PrivateRoute>
            }
          />

          <Route
            path="/homework/*"
            element={
              <PrivateRoute allowedRoles={['student']}>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<HomeworkPage />} />
                  </Routes>
                </MainLayout>
              </PrivateRoute>
            }
          />

          <Route
            path="/memory/*"
            element={
              <PrivateRoute>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<MemoryPage />} />
                  </Routes>
                </MainLayout>
              </PrivateRoute>
            }
          />

          {/* 家长路由 */}
          <Route
            path="/parent/dashboard/*"
            element={
              <PrivateRoute allowedRoles={['parent']}>
                <MainLayout>
                  <Routes>
                    <Route path="/" element={<ParentDashboardPage />} />
                  </Routes>
                </MainLayout>
              </PrivateRoute>
            }
          />

          {/* 404 页面 */}
          <Route
            path="*"
            element={
              <div className="not-found">
                <h1>404</h1>
                <p>页面未找到</p>
                <Link to="/dashboard">返回首页</Link>
              </div>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
