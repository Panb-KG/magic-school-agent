import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Button, Modal, Form, Input, message, Tabs, List, Tag, Avatar, Statistic } from 'antd';
import {
  UserOutlined,
  GiftOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useAuth } from '@/contexts/AuthContext';
import {
  getParentStudents,
  rewardStudentPoints,
  getStudentConversations,
  getStudentDashboard,
} from '@/api/parent';
import type {
  ParentStudentInfo,
  DashboardData,
  ConversationRecord,
} from '@/types';
import './ParentDashboardPage.css';

const ParentDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [students, setStudents] = useState<ParentStudentInfo[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<ParentStudentInfo | null>(null);
  const [studentDashboard, setStudentDashboard] = useState<DashboardData | null>(null);
  const [conversations, setConversations] = useState<ConversationRecord[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 奖励积分相关状态
  const [rewardModalVisible, setRewardModalVisible] = useState(false);
  const [rewardForm] = Form.useForm();

  // 对话历史相关状态
  const [conversationsVisible, setConversationsVisible] = useState(false);

  // 加载学生列表
  const loadStudents = async () => {
    setLoading(true);
    try {
      const response = await getParentStudents();
      if (response.success) {
        setStudents(response.data);
        if (response.data.length > 0 && !selectedStudent) {
          setSelectedStudent(response.data[0]);
        }
      }
    } catch (error) {
      message.error('加载学生列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载学生仪表盘
  const loadStudentDashboard = async (studentId: number) => {
    try {
      const response = await getStudentDashboard(studentId);
      if (response.success) {
        setStudentDashboard(response.data);
      }
    } catch (error) {
      message.error('加载学生数据失败');
    }
  };

  // 加载对话历史
  const loadConversations = async (studentId: number) => {
    try {
      const response = await getStudentConversations(studentId);
      if (response.success) {
        setConversations(response.data);
        setConversationsVisible(true);
      }
    } catch (error) {
      message.error('加载对话历史失败');
    }
  };

  // 奖励积分
  const handleRewardPoints = async (values: any) => {
    if (!selectedStudent) return;
    
    try {
      const response = await rewardStudentPoints({
        student_id: selectedStudent.id,
        points: values.points,
        reason: values.reason,
      });
      
      if (response.success) {
        message.success(`奖励成功！${selectedStudent.student_name} 获得了 ${values.points} 魔法积分！`);
        setRewardModalVisible(false);
        rewardForm.resetFields();
        // 刷新学生列表和仪表盘
        loadStudents();
        loadStudentDashboard(selectedStudent.id);
      }
    } catch (error) {
      message.error('奖励失败');
    }
  };

  // 切换学生
  const handleSelectStudent = (student: ParentStudentInfo) => {
    setSelectedStudent(student);
    setStudentDashboard(null);
    loadStudentDashboard(student.id);
  };

  useEffect(() => {
    loadStudents();
  }, []);

  useEffect(() => {
    if (selectedStudent) {
      loadStudentDashboard(selectedStudent.id);
    }
  }, [selectedStudent]);

  return (
    <div className="parent-dashboard">
      {/* 页面标题 */}
      <div className="dashboard-header">
        <h1>🏠 家长管理中心</h1>
        <p className="welcome-text">欢迎，{user?.real_name || '家长'}！管理孩子的学习进度</p>
      </div>

      <Row gutter={[24, 24]}>
        {/* 左侧：学生列表 */}
        <Col xs={24} md={8}>
          <Card
            title="🎓 我的学生"
            className="student-list-card"
            loading={loading}
          >
            <List
              dataSource={students}
              renderItem={(student) => (
                <List.Item
                  className={`student-item ${selectedStudent?.id === student.id ? 'active' : ''}`}
                  onClick={() => handleSelectStudent(student)}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar size={48} icon={<UserOutlined />} style={{ backgroundColor: '#667eea' }} />
                    }
                    title={student.student_name}
                    description={
                      <div>
                        <div className="student-info">
                          <Tag color="blue">{student.grade}</Tag>
                          <Tag color="purple">Lv.{student.magic_level}</Tag>
                        </div>
                        <div className="student-points">
                          🌟 {student.total_points} 积分
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
            
            {students.length === 0 && (
              <div className="empty-state">
                <p>还没有关联的学生</p>
                <Button type="primary">添加学生</Button>
              </div>
            )}
          </Card>
        </Col>

        {/* 右侧：学生详情 */}
        <Col xs={24} md={16}>
          {selectedStudent ? (
            <Tabs
              defaultActiveKey="overview"
              items={[
                {
                  key: 'overview',
                  label: '📊 学习概览',
                  children: studentDashboard && (
                    <div className="overview-tab">
                      <Row gutter={[16, 16]}>
                        <Col xs={12} sm={6}>
                          <Card>
                            <Statistic
                              title="总积分"
                              value={studentDashboard.stats.total_points}
                              prefix={<TrophyOutlined />}
                              valueStyle={{ color: '#3f8600' }}
                            />
                          </Card>
                        </Col>
                        <Col xs={12} sm={6}>
                          <Card>
                            <Statistic
                              title="魔法等级"
                              value={studentDashboard.stats.magic_level}
                              prefix="✨"
                              valueStyle={{ color: '#722ed1' }}
                            />
                          </Card>
                        </Col>
                        <Col xs={12} sm={6}>
                          <Card>
                            <Statistic
                              title="已完成作业"
                              value={studentDashboard.stats.completed_homeworks}
                              prefix={<CheckCircleOutlined />}
                              valueStyle={{ color: '#1890ff' }}
                            />
                          </Card>
                        </Col>
                        <Col xs={12} sm={6}>
                          <Card>
                            <Statistic
                              title="待完成作业"
                              value={studentDashboard.stats.pending_homeworks}
                              prefix={<ClockCircleOutlined />}
                              valueStyle={{ color: '#fa8c16' }}
                            />
                          </Card>
                        </Col>
                      </Row>

                      {/* 操作按钮 */}
                      <Card title="快捷操作" className="actions-card" style={{ marginTop: 16 }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Button
                            type="primary"
                            icon={<GiftOutlined />}
                            size="large"
                            block
                            onClick={() => setRewardModalVisible(true)}
                          >
                            奖励魔法积分
                          </Button>
                          <Button
                            icon={<EyeOutlined />}
                            size="large"
                            block
                            onClick={() => loadConversations(selectedStudent.id)}
                          >
                            查看对话历史
                          </Button>
                        </Space>
                      </Card>
                    </div>
                  ),
                },
                {
                  key: 'conversations',
                  label: '💬 对话历史',
                  children: (
                    <div className="conversations-tab">
                      <Button
                        type="primary"
                        onClick={() => loadConversations(selectedStudent.id)}
                        style={{ marginBottom: 16 }}
                      >
                        刷新对话记录
                      </Button>
                      <List
                        dataSource={conversations}
                        renderItem={(conv) => (
                          <List.Item>
                            <List.Item.Meta
                              title={
                                <span>
                                  对话 #{conv.conversation_id.slice(0, 8)}
                                  <Tag color="green" style={{ marginLeft: 8 }}>
                                    {conv.message_count} 条消息
                                  </Tag>
                                </span>
                              }
                              description={
                                <div>
                                  <p className="last-message">{conv.last_message}</p>
                                  <p className="last-time">
                                    {new Date(conv.last_message_time).toLocaleString('zh-CN')}
                                  </p>
                                </div>
                              }
                            />
                          </List.Item>
                        )}
                      />
                    </div>
                  ),
                },
              ]}
            />
          ) : (
            <Card>
              <div className="empty-state">
                <p>请选择一个学生查看详情</p>
              </div>
            </Card>
          )}
        </Col>
      </Row>

      {/* 奖励积分弹窗 */}
      <Modal
        title="🎁 奖励魔法积分"
        open={rewardModalVisible}
        onCancel={() => setRewardModalVisible(false)}
        onOk={() => rewardForm.submit()}
        okText="奖励"
        cancelText="取消"
      >
        <Form
          form={rewardForm}
          layout="vertical"
          onFinish={handleRewardPoints}
        >
          <Form.Item
            name="points"
            label="积分数量"
            rules={[
              { required: true, message: '请输入积分数量' },
              { type: 'number', min: 1, max: 100, message: '积分数量应在 1-100 之间' },
            ]}
          >
            <Input type="number" placeholder="输入奖励的积分数量" />
          </Form.Item>
          <Form.Item
            name="reason"
            label="奖励理由"
            rules={[{ required: true, message: '请输入奖励理由' }]}
          >
            <Input.TextArea
              rows={3}
              placeholder="例如：完成了数学作业、表现出色等"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

const { Space } = { Space: ({ children, direction }: { children: React.ReactNode; direction?: string }) => (
  <div style={{ display: 'flex', flexDirection: direction === 'vertical' ? 'column' : 'row', gap: '12px' }}>
    {children}
  </div>
)};

export default ParentDashboardPage;
