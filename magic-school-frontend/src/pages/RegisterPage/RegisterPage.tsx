import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Radio, Divider } from 'antd';
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  BookOutlined,
  UserSwitchOutlined,
} from '@ant-design/icons';
import { useAuth } from '@/contexts/AuthContext';
import type { RegisterRequest, UserRole } from '@/types';
import './RegisterPage.css';

interface RegisterFormData {
  username: string;
  password: string;
  confirmPassword: string;
  email?: string;
  role: UserRole;
  student_name?: string;
  nickname?: string;
  grade?: string;
  class_name?: string;
  school?: string;
  real_name?: string;
}

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();
  const [form] = Form.useForm<RegisterFormData>();
  const [selectedRole, setSelectedRole] = useState<UserRole>('student');

  const handleSubmit = async (values: RegisterFormData) => {
    try {
      const { confirmPassword, ...registerData } = values;
      
      await register(registerData as RegisterRequest);
      
      // 注册成功后跳转到仪表盘
      navigate('/dashboard');
    } catch (error) {
      // 错误已在 AuthContext 中处理
    }
  };

  return (
    <div className="register-container">
      <div className="register-background">
        <div className="magic-particles"></div>
      </div>
      
      <div className="register-content">
        <div className="register-header">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">魔法课桌</span>
          </div>
          <p className="register-subtitle">加入魔法家族，开启学习之旅 ✨</p>
        </div>

        <Card className="register-card" bordered={false}>
          <div className="role-selection">
            <p className="role-label">你是谁？</p>
            <Radio.Group
              value={selectedRole}
              onChange={(e) => {
                setSelectedRole(e.target.value);
                form.setFieldsValue({ role: e.target.value });
              }}
              size="large"
              buttonStyle="solid"
              className="role-buttons"
            >
              <Radio.Button value="student">
                <span className="role-icon">🎓</span>
                小巫师
              </Radio.Button>
              <Radio.Button value="parent">
                <span className="role-icon">👨‍👩‍👧‍👦</span>
                魔法守护者
              </Radio.Button>
            </Radio.Group>
          </div>

          <Divider />

          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            autoComplete="off"
            size="large"
            initialValues={{ role: 'student' }}
          >
            <Form.Item
              name="role"
              initialValue="student"
              hidden
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
                { max: 20, message: '用户名最多20个字符' },
                { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' },
              ]}
            >
              <Input
                prefix={<UserOutlined className="input-icon" />}
                placeholder="用户名（登录账号）"
              />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[
                { type: 'email', message: '请输入有效的邮箱地址' },
              ]}
            >
              <Input
                prefix={<MailOutlined className="input-icon" />}
                placeholder="邮箱（可选）"
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

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined className="input-icon" />}
                placeholder="确认密码"
              />
            </Form.Item>

            {selectedRole === 'student' && (
              <>
                <Divider>学生信息</Divider>
                <Form.Item
                  name="student_name"
                  rules={[
                    { required: true, message: '请输入真实姓名' },
                  ]}
                >
                  <Input
                    prefix={<UserOutlined className="input-icon" />}
                    placeholder="真实姓名"
                  />
                </Form.Item>

                <Form.Item
                  name="nickname"
                  rules={[
                    { required: true, message: '请输入昵称' },
                  ]}
                >
                  <Input
                    prefix={<BookOutlined className="input-icon" />}
                    placeholder="昵称"
                  />
                </Form.Item>

                <Form.Item
                  name="grade"
                  rules={[
                    { required: true, message: '请选择年级' },
                  ]}
                >
                  <Input
                    prefix={<BookOutlined className="input-icon" />}
                    placeholder="年级（如：三年级）"
                  />
                </Form.Item>

                <Form.Item
                  name="class_name"
                  rules={[
                    { required: true, message: '请输入班级' },
                  ]}
                >
                  <Input
                    placeholder="班级（如：3班）"
                  />
                </Form.Item>

                <Form.Item
                  name="school"
                  rules={[
                    { required: true, message: '请输入学校名称' },
                  ]}
                >
                  <Input
                    placeholder="学校名称"
                  />
                </Form.Item>
              </>
            )}

            {selectedRole === 'parent' && (
              <>
                <Divider>家长信息</Divider>
                <Form.Item
                  name="real_name"
                  rules={[
                    { required: true, message: '请输入真实姓名' },
                  ]}
                >
                  <Input
                    prefix={<UserSwitchOutlined className="input-icon" />}
                    placeholder="真实姓名"
                  />
                </Form.Item>
              </>
            )}

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={isLoading}
                block
                className="magic-button"
              >
                {selectedRole === 'student' ? '加入魔法学校' : '成为魔法守护者'}
              </Button>
            </Form.Item>
          </Form>

          <div className="register-footer">
            <p>已有账号？</p>
            <Link to="/login" className="magic-link">
              立即登录
            </Link>
          </div>
        </Card>

        <div className="page-footer">
          <p>⚡ 魔法学校学习管理系统</p>
          <p className="footer-text">© 2025 Magic School. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
