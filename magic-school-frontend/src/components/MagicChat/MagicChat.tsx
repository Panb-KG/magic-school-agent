/**
 * 魔法课桌智能体 - 聊天组件
 * 提供完整的聊天界面和智能体交互功能
 */

import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, message, Spin, Space, Tag, Tooltip } from 'antd';
import { 
  SendOutlined, 
  RobotOutlined, 
  UserOutlined, 
  ClearOutlined,
  StopOutlined 
} from '@ant-design/icons';
import { 
  streamMessage, 
  cancelMessage, 
  generateSessionId,
  type ChatMessage 
} from '@/services/chatService';
import { authStorage } from '@/contexts/AuthContext';
import './MagicChat.css';

const { TextArea } = Input;

interface MagicChatProps {
  className?: string;
  defaultSessionId?: string;
  showHeader?: boolean;
  height?: string | number;
  onMessageReceived?: (message: string) => void;
}

const MagicChat: React.FC<MagicChatProps> = ({ 
  className, 
  defaultSessionId,
  showHeader = true,
  height = '100%',
  onMessageReceived 
}) => {
  // 状态管理
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentRunId, setCurrentRunId] = useState<string>('');
  const [sessionId] = useState<string>(
    defaultSessionId || generateSessionId()
  );

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // 获取当前用户
  const user = authStorage.getUser();
  const isStudent = user?.role === 'student';

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    // 添加用户消息
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setIsStreaming(true);

    // 创建助手消息占位符
    const assistantMessage: ChatMessage = {
      id: `msg_${Date.now() + 1}`,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, assistantMessage]);

    try {
      // 使用流式响应
      await streamMessage(
        userMessage.content,
        sessionId,
        // onChunk: 收到新内容时更新
        (chunk: string) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessage.id
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        // onComplete: 完成时的回调
        (fullResponse: string) => {
          message.success('回复完成');
          onMessageReceived?.(fullResponse);
        },
        // onError: 错误处理
        (error: Error) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessage.id
                ? {
                    ...msg,
                    content: `抱歉，发生了错误：${error.message}。请稍后重试。`,
                  }
                : msg
            )
          );
          message.error(`错误: ${error.message}`);
        }
      );
    } catch (error) {
      console.error('发送消息失败:', error);
      message.error('发送消息失败，请稍后重试');
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      setCurrentRunId('');
    }
  };

  // 停止生成
  const handleStopGeneration = () => {
    if (currentRunId) {
      cancelMessage(currentRunId);
      setIsStreaming(false);
      setIsLoading(false);
      message.info('已停止生成');
    }
  };

  // 清空对话
  const handleClearMessages = () => {
    setMessages([]);
    message.success('对话已清空');
  };

  // 按回车发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading) {
        handleSendMessage();
      } else {
        handleStopGeneration();
      }
    }
  };

  // 格式化消息内容（支持简单的 Markdown）
  const formatMessage = (content: string) => {
    // 这里可以添加 Markdown 渲染逻辑
    return content;
  };

  return (
    <Card
      className={`magic-chat ${className}`}
      style={{ height }}
      bodyStyle={{ padding: 0, display: 'flex', flexDirection: 'column', height: '100%' }}
    >
      {/* 头部 */}
      {showHeader && (
        <div className="magic-chat-header">
          <Space align="center">
            <RobotOutlined className="magic-chat-icon" />
            <div>
              <div className="magic-chat-title">魔法课桌助手</div>
              <div className="magic-chat-subtitle">
                {isStudent ? '学生模式' : '家长模式'}
                {messages.length > 0 && (
                  <Tag color="blue" style={{ marginLeft: 8 }}>
                    {messages.length} 条消息
                  </Tag>
                )}
              </div>
            </div>
          </Space>
          <Space>
            <Tooltip title="清空对话">
              <Button
                type="text"
                icon={<ClearOutlined />}
                onClick={handleClearMessages}
                disabled={isLoading}
                size="small"
              />
            </Tooltip>
          </Space>
        </div>
      )}

      {/* 消息区域 */}
      <div className="magic-chat-messages">
        {messages.length === 0 && (
          <div className="magic-chat-welcome">
            <RobotOutlined className="magic-chat-welcome-icon" />
            <div className="magic-chat-welcome-title">
              你好！我是魔法课桌助手
            </div>
            <div className="magic-chat-welcome-subtitle">
              我可以帮你：
            </div>
            <ul className="magic-chat-welcome-features">
              <li>📅 查询今天的课程和作业</li>
              <li>📖 回答学习问题（但不直接给答案）</li>
              <li>🏆 查看你的成就和积分</li>
              <li>📊 生成学习报告和建议</li>
            </ul>
            <div className="magic-chat-welcome-tip">
              💡 我会引导你思考，而不是直接告诉你答案哦！
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`magic-chat-message ${msg.role}`}
          >
            <div className="magic-chat-avatar">
              {msg.role === 'user' ? (
                <UserOutlined />
              ) : (
                <RobotOutlined />
              )}
            </div>
            <div className="magic-chat-content">
              <div className="magic-chat-text">
                {formatMessage(msg.content)}
                {isLoading &&
                  msg.role === 'assistant' &&
                  !msg.content && (
                    <Spin size="small" />
                  )}
                {isStreaming && msg.role === 'assistant' && (
                  <span className="magic-chat-cursor" />
                )}
              </div>
              <div className="magic-chat-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="magic-chat-input">
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            isStudent
              ? '输入你的问题... (我会引导你思考哦！)'
              : '输入你的问题...'
          }
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={isLoading}
          className="magic-chat-textarea"
        />
        <Button
          type="primary"
          icon={isLoading ? <StopOutlined /> : <SendOutlined />}
          onClick={isLoading ? handleStopGeneration : handleSendMessage}
          disabled={!inputValue.trim() && !isLoading}
          loading={isLoading && !isStreaming}
          className="magic-chat-send-button"
        >
          {isLoading ? '停止' : '发送'}
        </Button>
      </div>
    </Card>
  );
};

export default MagicChat;
