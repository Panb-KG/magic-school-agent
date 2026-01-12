import request from '@/utils/request';
import type { AchievementWallData, HomeworkProgress } from '@/types';

/**
 * 获取学生成就墙数据
 */
export const getAchievementWall = (
  studentName: string
): Promise<AchievementWallData> => {
  return request.get(`/achievements/wall/${encodeURIComponent(studentName)}`);
};

/**
 * 获取学生作业进度
 */
export const getHomeworkProgress = (
  studentName: string
): Promise<HomeworkProgress> => {
  return request.get(`/homework/progress/${encodeURIComponent(studentName)}`);
};
