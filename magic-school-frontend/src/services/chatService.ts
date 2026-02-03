/**
 * 魔法课桌智能体 - 聊天服务
 * 提供与后端智能体API的交互功能
 */

import { authStorage } from '@/contexts/AuthContext';

// ============ 类型定义 ============

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  user_id?: string;
  user_role?: 'student' | 'parent';
}

export interface ChatResponse {
  message?: string;
  output?: string;
  session_id?: string;
  run_id?: string;
  tools_used?: string[];
  time_cost_ms?: number;
}

export interface SSEMessage {
  type?: string;
  content?: string;
  message?: string;
  session_id?: string;
  query_msg_id?: string;
  local_msg_id?: string;
  log_id?: string;
  run_id?: string;
  reply_id?: string;
  sequence_id?: number;
  code?: string;
  [key: string]: any;
}

// ============ 配置 ============

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';
const DEFAULT_TIMEOUT = 60000; // 60秒

// ============ 辅助函数 ============

/**
 * 生成会话 ID
 */
export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * 获取认证 Token
 */
const getAuthToken = (): string => {
  return localStorage.getItem('token') || '';
};

/**
 * 获取当前用户信息
 */
const getCurrentUser = () => {
  try {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    console.error('解析用户信息失败:', e);
    return null;
  }
};

// ============ 核心 API ============

/**
 * 非流式对话 - 等待完整响应后返回
 * 
 * @param query 用户消息
 * @param sessionId 会话ID（可选，默认生成新ID）
 * @returns Promise<ChatResponse> 完整的响应
 * 
 * @example
 * const response = await sendMessage('你好');
 * console.log(response.output);
 */
export const sendMessage = async (
  query: string,
  sessionId?: string
): Promise<ChatResponse> => {
  try {
    const token = getAuthToken();
    const user = getCurrentUser();
    const actualSessionId = sessionId || generateSessionId();

    const response = await fetch(`${BACKEND_URL}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        query,
        session_id: actualSessionId,
        user_id: user?.id,
        user_role: user?.role,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        `HTTP ${response.status}: ${errorData.detail || errorData.message || '请求失败'}`
      );
    }

    const data: ChatResponse = await response.json();
    
    return {
      ...data,
      session_id: actualSessionId,
    };
  } catch (error) {
    console.error('发送消息失败:', error);
    throw error;
  }
};

/**
 * 流式对话 - 实时接收响应
 * 
 * @param query 用户消息
 * @param sessionId 会话ID
 * @param onChunk 接收到内容块时的回调
 * @param onComplete 完成时的回调
 * @param onError 错误时的回调
 * @returns Promise<string> 完整的响应内容
 * 
 * @example
 * await streamMessage(
 *   '帮我查一下今天的课程',
 *   sessionId,
 *   (chunk) => console.log('收到:', chunk),
 *   (full) => console.log('完成:', full),
 *   (err) => console.error('错误:', err)
 * );
 */
export const streamMessage = async (
  query: string,
  sessionId: string,
  onChunk?: (chunk: string) => void,
  onComplete?: (fullResponse: string) => void,
  onError?: (error: Error) => void
): Promise<string> => {
  try {
    const token = getAuthToken();
    const user = getCurrentUser();

    const response = await fetch(`${BACKEND_URL}/stream_run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        query,
        session_id: sessionId,
        user_id: user?.id,
        user_role: user?.role,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(
        `HTTP ${response.status}: ${errorData.detail || errorData.message || '请求失败'}`
      );
      onError?.(error);
      throw error;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      const error = new Error('无法读取响应流');
      onError?.(error);
      throw error;
    }

    const decoder = new TextDecoder();
    let fullResponse = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        onComplete?.(fullResponse);
        break;
      }

      // 解码数据
      buffer += decoder.decode(value, { stream: true });
      
      // 处理 SSE 格式: event: message\ndata: {...}\n\n
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // 保留未完整的行

      for (const line of lines) {
        const trimmedLine = line.trim();
        
        if (trimmedLine.startsWith('data: ')) {
          try {
            const jsonStr = trimmedLine.replace('data: ', '');
            const data: SSEMessage = JSON.parse(jsonStr);
            
            // 提取消息内容
            const content = data.content || data.message || '';
            
            if (content) {
              fullResponse += content;
              onChunk?.(content);
            }

            // 检查是否结束
            if (data.type === 'end' || data.code === 'end') {
              onComplete?.(fullResponse);
              return fullResponse;
            }
          } catch (e) {
            console.warn('解析 SSE 数据失败:', e, trimmedLine);
          }
        }
      }
    }

    return fullResponse;
  } catch (error) {
    console.error('流式发送消息失败:', error);
    onError?.(error as Error);
    throw error;
  }
};

/**
 * 取消正在进行的对话
 * 
 * @param runId 运行ID
 */
export const cancelMessage = async (runId: string): Promise<void> => {
  try {
    const token = getAuthToken();
    
    await fetch(`${BACKEND_URL}/cancel/${runId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.error('取消消息失败:', error);
    throw error;
  }
};

// ============ 高级功能 ============

/**
 * 批量发送消息
 * 
 * @param messages 消息列表
 * @param onProgress 进度回调
 */
export const batchSendMessage = async (
  messages: string[],
  sessionId: string,
  onProgress?: (index: number, total: number, response: string) => void
): Promise<string[]> => {
  const responses: string[] = [];
  
  for (let i = 0; i < messages.length; i++) {
    const response = await streamMessage(
      messages[i],
      sessionId,
      undefined,
      (fullResponse) => {
        responses.push(fullResponse);
        onProgress?.(i + 1, messages.length, fullResponse);
      }
    );
  }
  
  return responses;
};

/**
 * 带超时的流式对话
 */
export const streamMessageWithTimeout = async (
  query: string,
  sessionId: string,
  timeout: number = DEFAULT_TIMEOUT,
  onChunk?: (chunk: string) => void,
  onComplete?: (fullResponse: string) => void,
  onError?: (error: Error) => void
): Promise<string> => {
  return Promise.race([
    streamMessage(query, sessionId, onChunk, onComplete, onError),
    new Promise<string>((_, reject) => {
      setTimeout(() => {
        const error = new Error(`请求超时 (${timeout}ms)`);
        onError?.(error);
        reject(error);
      }, timeout);
    }),
  ]);
};

// ============ 默认导出 ============

export default {
  sendMessage,
  streamMessage,
  streamMessageWithTimeout,
  cancelMessage,
  batchSendMessage,
  generateSessionId,
};
