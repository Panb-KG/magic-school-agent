import request from '@/utils/request';
import type {
  ApiResponse,
  UserProfile,
  KnowledgeStats,
  MemoryQueryResult,
} from '@/types';

// 获取用户画像
export const getUserProfile = async (userId?: number): Promise<ApiResponse<UserProfile>> => {
  const params = userId ? { user_id: userId } : {};
  return request.get('/memory/profile', { params });
};

// 更新用户画像
export const updateUserProfile = async (data: Partial<UserProfile>): Promise<ApiResponse<{ success: boolean }>> => {
  return request.post('/memory/profile', data);
};

// 获取知识掌握度统计
export const getKnowledgeStats = async (userId?: number): Promise<ApiResponse<KnowledgeStats>> => {
  const params = userId ? { user_id: userId } : {};
  return request.get('/memory/knowledge', { params });
};

// 查询相关记忆
export const queryMemories = async (query: string, userId?: number): Promise<ApiResponse<MemoryQueryResult>> => {
  const params: any = { query };
  if (userId) params.user_id = userId;
  return request.get('/memory/query', { params });
};
