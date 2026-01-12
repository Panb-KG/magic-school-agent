import request from '@/utils/request';
import type { PointsTrendData } from '@/types';

/**
 * 获取学生积分趋势
 * @param studentName 学生姓名
 * @param days 查询天数，默认7天
 */
export const getPointsTrend = (
  studentName: string,
  days: number = 7
): Promise<PointsTrendData> => {
  return request.get(
    `/points/trend/${encodeURIComponent(studentName)}?days=${days}`
  );
};
