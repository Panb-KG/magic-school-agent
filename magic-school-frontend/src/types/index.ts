// API 响应通用类型
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

// 学生档案
export interface StudentProfile {
  id: number;
  name: string;
  grade: string;
  class_name: string;
  school: string;
  nickname: string;
  avatar_url: string;
  magic_level: number;
  total_points: number;
  level_progress: number;
  next_level_points: number;
}

// 学生统计
export interface StudentStats {
  total_points: number;
  magic_level: number;
  completed_homeworks: number;
  pending_homeworks: number;
  total_exercises: number;
  total_exercise_minutes: number;
  total_achievements: number;
  featured_achievements: number;
  homework_completion_rate: number;
}

// 成就
export interface Achievement {
  id: number;
  title: string;
  description: string;
  type: string;
  icon: string;
  unlocked_at: string;
  points: number;
  is_featured: boolean;
}

// 待办事项
export interface Todo {
  id: number;
  title: string;
  subject: string;
  due_date: string;
  days_left: number;
  urgency: 'high' | 'medium' | 'low';
  type: 'homework' | 'exercise' | 'reading' | 'other';
}

// 仪表盘数据
export interface DashboardData {
  profile: StudentProfile;
  stats: StudentStats;
  recent_achievements: Achievement[];
  todos: Todo[];
  suggestions: string[];
  week_stats: {
    total_points: number;
    breakdown: {
      homework: number;
      exercise: number;
      reading: number;
      other: number;
    };
  };
  generated_at: string;
}

// 课程
export interface Course {
  id: number;
  name: string;
  type: 'school' | 'extra';
  time: string;
  location: string;
  teacher: string;
  classroom: string;
  notes: string;
}

// 课程表数据
export interface ScheduleData {
  weekdays: string[];
  courses: Record<string, Course[]>;
  statistics: {
    total_courses: number;
    school_courses: number;
    extra_courses: number;
    course_count_by_day: Record<string, number>;
  };
  generated_at: string;
}

// 积分趋势点
export interface PointsTrendPoint {
  date: string;
  points: number;
  daily_gain: number;
}

// 积分趋势数据
export interface PointsTrendData {
  student_name: string;
  days: number;
  data: PointsTrendPoint[];
  summary: {
    total_gain: number;
    average_daily_gain: number;
    best_day: string;
  };
  generated_at: string;
}

// 作业进度
export interface HomeworkProgress {
  student_name: string;
  total: number;
  completed: number;
  pending: number;
  overdue: number;
  completion_rate: number;
  subjects: {
    subject: string;
    total: number;
    completed: number;
    pending: number;
  }[];
  homeworks: {
    id: number;
    title: string;
    subject: string;
    status: 'pending' | 'completed' | 'overdue';
    due_date: string;
  }[];
  generated_at: string;
}

// 成就墙数据
export interface AchievementWallData {
  student_name: string;
  total_achievements: number;
  achievements_by_level: {
    bronze: number;
    silver: number;
    gold: number;
    platinum: number;
    diamond: number;
  };
  featured_achievements: Achievement[];
  recent_achievements: Achievement[];
  achievement_points: number;
  generated_at: string;
}

// WebSocket 消息类型
export type WebSocketMessage =
  | { type: 'dashboard_update'; data: DashboardData }
  | { type: 'points_update'; data: { points: number; level: number } }
  | { type: 'new_achievement'; data: Achievement }
  | { type: 'homework_reminder'; data: Todo }
  | { type: 'error'; message: string };

// 学生档案摘要
export interface ProfileSummary {
  id: number;
  name: string;
  nickname: string;
  grade: string;
  class_name: string;
  school: string;
  avatar_url: string;
  magic_level: number;
  total_points: number;
  level_progress: number;
  level_percentage: number;
  achievements_by_level: {
    bronze: number;
    silver: number;
    gold: number;
    platinum: number;
    diamond: number;
  };
  featured_count: number;
  total_achievement_points: number;
}
