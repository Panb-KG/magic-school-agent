/**
 * 魔法课桌智能体 - 聊天页面示例
 * 展示如何在前端页面中使用智能体
 */

import React, { useState } from 'react';
import { Layout, Typography, Space, Card, Statistic, Row, Col } from 'antd';
import { 
  MessageOutlined, 
  RobotOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined 
} from '@ant-design/icons';
import MagicChat from '@/components/MagicChat';
import { authStorage } from '@/contexts/AuthContext';
import './MagicChatPage.css';

const { Header, Content } = Layout;
const { Title, Paragraph } = Typography;

const MagicChatPage: React.FC = () => {
  const user = authStorage.getUser();
  const [messageCount, setMessageCount] = useState(0);

  const handleMessageReceived = (message: string) => {
    setMessageCount((prev) => prev + 1);
    console.log('收到新消息:', message);
  };

  return (
    <Layout className="magic-chat-page">
      <Header className="magic-chat-page-header">
        <div className="header-content">
          <Space align="center" size="large">
            <RobotOutlined className="page-icon" />
            <div>
              <Title level={3} style={{ margin: 0 }}>
                魔法课桌智能体
              </Title>
              <Paragraph style={{ margin: 0, color: 'rgba(255,255,255,0.8)' }}>
                {user?.role === 'student' ? '学生模式' : '家长模式'}
              </Paragraph>
            </div>
          </Space>
        </div>
      </Header>

      <Content className="magic-chat-page-content">
        <Row gutter={[16, 16]}>
          {/* 左侧：统计信息 */}
          <Col xs={24} lg={6}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Card>
                <Statistic
                  title="今日对话"
                  value={messageCount}
                  prefix={<MessageOutlined />}
                  suffix="次"
                />
              </Card>
              
              <Card>
                <Statistic
                  title="在线状态"
                  value="在线"
                  prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>

              <Card>
                <Statistic
                  title="响应时间"
                  value="< 2s"
                  prefix={<ClockCircleOutlined />}
                  suffix="平均"
                />
              </Card>

              <Card
                title="💡 使用提示"
                style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}
              >
                <Paragraph style={{ color: 'white', margin: 0 }}>
                  我会引导你思考问题，而不是直接给你答案哦！
                </Paragraph>
              </Card>
            </Space>
          </Col>

          {/* 右侧：聊天界面 */}
          <Col xs={24} lg={18}>
            <Card 
              className="chat-card"
              bodyStyle={{ padding: 0, height: 'calc(100vh - 200px)' }}
            >
              <MagicChat
                showHeader={false}
                height="100%"
                onMessageReceived={handleMessageReceived}
              />
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default MagicChatPage;
