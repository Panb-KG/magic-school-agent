import request from '@/utils/request';
import type {
  ApiResponse,
  ParentStudentInfo,
  ConversationRecord,
  ConversationDetail,
  DashboardData,
} from '@/types';

// 获取家长管理的所有学生列表
export const getParentStudents = async (): Promise<ApiResponse<ParentStudentInfo[]>> => {
  return request.get('/parent/students');
};

// 联系学生（将学生添加到家长管理列表）
export const linkStudent = async (studentId: number): Promise<ApiResponse<{ success: boolean }>> => {
  return request.post('/parent/link-student', { student_id: studentId });
};

// 查看学生对话历史列表
export const getStudentConversations = async (studentId: number): Promise<ApiResponse<ConversationRecord[]>> => {
  return request.get(`/parent/students/${studentId}/conversations`);
};

// 查看具体对话详情
export const getConversationDetail = async (
  studentId: number,
  conversationId: string
): Promise<ApiResponse<ConversationDetail>> => {
  return request.get(`/parent/students/${studentId}/conversations/${conversationId}`);
};

// 修改学生作业
export const modifyStudentHomework = async (data: {
  student_id: number;
  homework_id: number;
  title?: string;
  description?: string;
  due_date?: string;
  priority?: string;
}): Promise<ApiResponse<{ success: boolean }>> => {
  return request.post('/parent/modify-homework', data);
};

// 给学生奖励积分
export const rewardStudentPoints = async (data: {
  student_id: number;
  points: number;
  reason: string;
}): Promise<ApiResponse<{ success: boolean; new_points: number }>> => {
  return request.post('/parent/reward-points', data);
};

// 审核学生作业
export const approveHomework = async (data: {
  student_id: number;
  homework_id: number;
  approved: boolean;
  feedback?: string;
}): Promise<ApiResponse<{ success: boolean }>> => {
  return request.post('/parent/approve-homework', data);
};

// 获取学生仪表盘（家长视角）
export const getStudentDashboard = async (studentId: number): Promise<ApiResponse<DashboardData>> => {
  return request.get(`/parent/students/${studentId}/dashboard`);
};
