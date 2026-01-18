import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Tabs, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '@/contexts/AuthContext';
import './LoginPage.css';

interface LoginFormData {
  username: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  const [form] = Form.useForm<LoginFormData>();

  const handleSubmit = async (values: LoginFormData) => {
    try {
      await login(values);
      // 登录成功后，根据角色跳转到不同页面
      navigate('/dashboard');
    } catch (error) {
      // 错误已在 AuthContext 中处理
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="magic-particles"></div>
      </div>
      
      <div className="login-content">
        <div className="login-header">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">霍格沃茨魔法学校</span>
          </div>
          <p className="login-subtitle">让学习充满魔法 ✨</p>
        </div>

        <Card className="login-card" bordered={false}>
          <Tabs
            defaultActiveKey="login"
            centered
            items={[
              {
                key: 'login',
                label: '🔮 登录',
                children: (
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                    autoComplete="off"
                    size="large"
                  >
                    <Form.Item
                      name="username"
                      rules={[
                        { required: true, message: '请输入用户名' },
                        { min: 3, message: '用户名至少3个字符' },
                      ]}
                    >
                      <Input
                        prefix={<UserOutlined className="input-icon" />}
                        placeholder="用户名"
                      />
                    </Form.Item>

                    <Form.Item
                      name="password"
                      rules={[
                        { required: true, message: '请输入密码' },
                        { min: 6, message: '密码至少6个字符' },
                      ]}
                    >
                      <Input.Password
                        prefix={<LockOutlined className="input-icon" />}
                        placeholder="密码"
                      />
                    </Form.Item>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={isLoading}
                        block
                        className="magic-button"
                      >
                        施展魔法登录
                      </Button>
                    </Form.Item>
                  </Form>
                ),
              },
              {
                key: 'register',
                label: '✨ 注册',
                children: (
                  <div className="register-tip">
                    <p>还没有账号？</p>
                    <Link to="/register" className="magic-link">
                      立即注册，开启魔法之旅
                    </Link>
                  </div>
                ),
              },
            ]}
          />
        </Card>

        <div className="login-footer">
          <p>⚡ 魔法学校学习管理系统</p>
          <p className="footer-text">© 2025 Magic School. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
