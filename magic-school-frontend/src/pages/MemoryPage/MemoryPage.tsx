import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Tabs, Progress, Tag, List, Input, Button, Empty, Descriptions } from 'antd';
import {
  UserOutlined,
  BookOutlined,
  TrophyOutlined,
  BulbOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { getUserProfile, getKnowledgeStats } from '@/api/memory';
import { useAuth } from '@/contexts/AuthContext';
import type { UserProfile, KnowledgeStats, KnowledgeMastery } from '@/types';
import './MemoryPage.css';

const MemoryPage: React.FC = () => {
  const { user } = useAuth();
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [knowledgeStats, setKnowledgeStats] = useState<KnowledgeStats | null>(null);
  const [loading, setLoading] = useState(false);

  // 加载用户画像
  const loadUserProfile = async () => {
    setLoading(true);
    try {
      const response = await getUserProfile();
      if (response.success) {
        setUserProfile(response.data);
      }
    } catch (error) {
      console.error('加载用户画像失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载知识掌握度
  const loadKnowledgeStats = async () => {
    setLoading(true);
    try {
      const response = await getKnowledgeStats();
      if (response.success) {
        setKnowledgeStats(response.data);
      }
    } catch (error) {
      console.error('加载知识掌握度失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUserProfile();
    loadKnowledgeStats();
  }, []);

  // 获取掌握度等级颜色
  const getMasteryColor = (level: number) => {
    if (level >= 80) return '#52c41a';
    if (level >= 50) return '#faad14';
    return '#ff4d4f';
  };

  // 获取掌握度等级标签
  const getMasteryLevel = (level: number) => {
    if (level >= 80) return '已掌握';
    if (level >= 50) return '学习中';
    return '需加强';
  };

  // 获取难度标签颜色
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'green';
      case 'intermediate':
        return 'blue';
      case 'advanced':
        return 'purple';
      default:
        return 'default';
    }
  };

  // 获取难度标签文本
  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return '初级';
      case 'intermediate':
        return '中级';
      case 'advanced':
        return '高级';
      default:
        return difficulty;
    }
  };

  return (
    <div className="memory-page">
      <div className="page-header">
        <h1>🧠 长期记忆中心</h1>
        <p className="page-subtitle">
          {user?.role === 'student'
            ? '查看你的学习画像和知识掌握情况'
            : '查看学生的学习画像和知识掌握情况'}
        </p>
      </div>

      <Tabs
        defaultActiveKey="profile"
        items={[
          {
            key: 'profile',
            label: '👤 用户画像',
            children: userProfile && (
              <div className="profile-content">
                <Row gutter={[24, 24]}>
                  {/* 基本信息 */}
                  <Col xs={24} md={8}>
                    <Card title="基本信息" loading={loading}>
                      <div className="profile-avatar">
                        <UserOutlined className="avatar-icon" />
                      </div>
                      <Descriptions column={1} bordered>
                        <Descriptions.Item label="用户名">{userProfile.username}</Descriptions.Item>
                        <Descriptions.Item label="学生名">
                          {userProfile.student_name || userProfile.nickname || '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="年级">
                          {userProfile.grade || '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="学习风格">
                          {userProfile.learning_style || '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="最后更新">
                          {new Date(userProfile.last_updated).toLocaleDateString('zh-CN')}
                        </Descriptions.Item>
                      </Descriptions>
                    </Card>
                  </Col>

                  {/* 兴趣爱好 */}
                  <Col xs={24} md={8}>
                    <Card title="兴趣爱好" loading={loading}>
                      {userProfile.interests && userProfile.interests.length > 0 ? (
                        <div className="tags-container">
                          {userProfile.interests.map((interest, index) => (
                            <Tag key={index} color="blue" icon={<BulbOutlined />}>
                              {interest}
                            </Tag>
                          ))}
                        </div>
                      ) : (
                        <Empty description="暂无兴趣爱好记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                      )}
                    </Card>

                    <Card title="优势" loading={loading} style={{ marginTop: 16 }}>
                      {userProfile.strengths && userProfile.strengths.length > 0 ? (
                        <List
                          dataSource={userProfile.strengths}
                          renderItem={(strength) => (
                            <List.Item>
                              <Tag color="success" icon={<TrophyOutlined />}>
                                {strength}
                              </Tag>
                            </List.Item>
                          )}
                        />
                      ) : (
                        <Empty description="暂无优势记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                      )}
                    </Card>
                  </Col>

                  {/* 待提升和学习目标 */}
                  <Col xs={24} md={8}>
                    <Card title="待提升" loading={loading}>
                      {userProfile.weaknesses && userProfile.weaknesses.length > 0 ? (
                        <List
                          dataSource={userProfile.weaknesses}
                          renderItem={(weakness) => (
                            <List.Item>
                              <Tag color="warning">{weakness}</Tag>
                            </List.Item>
                          )}
                        />
                      ) : (
                        <Empty description="暂无待提升项" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                      )}
                    </Card>

                    <Card title="学习目标" loading={loading} style={{ marginTop: 16 }}>
                      {userProfile.goals && userProfile.goals.length > 0 ? (
                        <List
                          dataSource={userProfile.goals}
                          renderItem={(goal, index) => (
                            <List.Item>
                              <span className="goal-item">
                                <span className="goal-number">{index + 1}.</span>
                                {goal}
                              </span>
                            </List.Item>
                          )}
                        />
                      ) : (
                        <Empty description="暂无学习目标" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                      )}
                    </Card>
                  </Col>
                </Row>

                {/* 学习偏好 */}
                <Card title="学习偏好" loading={loading} style={{ marginTop: 24 }}>
                  <Descriptions column={1} bordered>
                    <Descriptions.Item label="回复风格">
                      {userProfile.preferences?.response_style || '默认'}
                    </Descriptions.Item>
                    <Descriptions.Item label="难度偏好">
                      {userProfile.preferences?.difficulty_level || '默认'}
                    </Descriptions.Item>
                    <Descriptions.Item label="鼓励程度">
                      {userProfile.preferences?.encouragement_level || '默认'}
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </div>
            ),
          },
          {
            key: 'knowledge',
            label: '📚 知识掌握度',
            children: knowledgeStats && (
              <div className="knowledge-content">
                <Row gutter={[24, 24]}>
                  {/* 统计概览 */}
                  <Col xs={24} md={12}>
                    <Card title="掌握度统计" loading={loading}>
                      <Row gutter={[16, 16]}>
                        <Col span={12}>
                          <div className="stat-item">
                            <div className="stat-label">总知识点</div>
                            <div className="stat-value">{knowledgeStats.total_topics}</div>
                          </div>
                        </Col>
                        <Col span={12}>
                          <div className="stat-item">
                            <div className="stat-label">已掌握</div>
                            <div className="stat-value success">{knowledgeStats.mastered_topics}</div>
                          </div>
                        </Col>
                        <Col span={12}>
                          <div className="stat-item">
                            <div className="stat-label">学习中</div>
                            <div className="stat-value warning">{knowledgeStats.in_progress_topics}</div>
                          </div>
                        </Col>
                        <Col span={12}>
                          <div className="stat-item">
                            <div className="stat-label">需加强</div>
                            <div className="stat-value danger">{knowledgeStats.weak_topics}</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  <Col xs={24} md={12}>
                    <Card title="平均掌握度" loading={loading}>
                      <div className="mastery-progress">
                        <Progress
                          type="circle"
                          percent={Math.round(knowledgeStats.average_mastery)}
                          format={(percent) => `${percent}%`}
                          strokeColor={{
                            '0%': '#ff4d4f',
                            '50%': '#faad14',
                            '80%': '#52c41a',
                          }}
                          size={180}
                        />
                        <p className="mastery-text">
                          {knowledgeStats.average_mastery >= 80
                            ? '🎉 掌握情况优秀！'
                            : knowledgeStats.average_mastery >= 50
                            ? '💪 继续加油！'
                            : '📖 需要更多练习'}
                        </p>
                      </div>
                    </Card>
                  </Col>

                  {/* 按科目统计 */}
                  <Col xs={24}>
                    <Card title="科目掌握度" loading={loading}>
                      {knowledgeStats.by_subject && knowledgeStats.by_subject.length > 0 ? (
                        <Row gutter={[16, 16]}>
                          {knowledgeStats.by_subject.map((subject, index) => (
                            <Col xs={24} sm={12} md={8} key={index}>
                              <Card size="small" className="subject-card">
                                <h4 className="subject-title">{subject.subject}</h4>
                                <Progress
                                  percent={Math.round(subject.average_mastery)}
                                  strokeColor={getMasteryColor(subject.average_mastery)}
                                  format={(percent) => `${percent}%`}
                                />
                              </Card>
                            </Col>
                          ))}
                        </Row>
                      ) : (
                        <Empty description="暂无科目数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                      )}
                    </Card>
                  </Col>

                  {/* 详细知识点列表 */}
                  <Col xs={24}>
                    <Card title="知识点详情" loading={loading}>
                      {knowledgeStats.topics && knowledgeStats.topics.length > 0 ? (
                        <List
                          grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 4 }}
                          dataSource={knowledgeStats.topics.slice(0, 20)}
                          renderItem={(topic: KnowledgeMastery) => (
                            <List.Item>
                              <Card size="small" className="topic-card">
                                <div className="topic-header">
                                  <Tag color={getDifficultyColor(topic.difficulty)}>
                                    {getDifficultyText(topic.difficulty)}
                                  </Tag>
                                  <span className="topic-subject">{topic.subject}</span>
                                </div>
                                <h4 className="topic-name">{topic.topic}</h4>
                                <Progress
                                  percent={topic.mastery_level}
                                  strokeColor={getMasteryColor(topic.mastery_level)}
                                  showInfo={false}
                                />
                                <div className="topic-footer">
                                  <span className="mastery-badge">{getMasteryLevel(topic.mastery_level)}</span>
                                  <span className="practice-count">
                                    练习 {topic.practice_count} 次
                                  </span>
                                </div>
                              </Card>
                            </List.Item>
                          )}
                        />
                      ) : (
                        <Empty description="暂无知识点数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                      )}
                    </Card>
                  </Col>
                </Row>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
};

export default MemoryPage;
