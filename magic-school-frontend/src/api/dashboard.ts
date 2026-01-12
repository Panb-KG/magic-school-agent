import request from '@/utils/request';
import type { DashboardData, ProfileSummary } from '@/types';

/**
 * 获取学生仪表盘数据
 */
export const getDashboard = (studentName: string): Promise<DashboardData> => {
  return request.get(`/dashboard/${encodeURIComponent(studentName)}`);
};

/**
 * 获取学生档案摘要
 */
export const getProfile = (studentName: string): Promise<ProfileSummary> => {
  return request.get(`/profile/${encodeURIComponent(studentName)}`);
};
