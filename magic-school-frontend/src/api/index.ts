import request from '@/utils/request';
import type {
  DashboardData,
  ScheduleData,
  PointsTrendData,
  HomeworkProgress,
  AchievementWallData,
  ProfileSummary,
} from '@/types';

// 导出各个 API 模块
export * from './dashboard';
export * from './schedule';
export * from './points';
export * from './achievements';
