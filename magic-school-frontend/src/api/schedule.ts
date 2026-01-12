import request from '@/utils/request';
import type { ScheduleData } from '@/types';

/**
 * 获取学生课程表
 */
export const getSchedule = (studentName: string): Promise<ScheduleData> => {
  return request.get(`/schedule/${encodeURIComponent(studentName)}`);
};
