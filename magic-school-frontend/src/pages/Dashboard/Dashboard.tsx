import React from 'react';
import { useParams } from 'react-router-dom';
import { useAPI } from '@/hooks/useAPI';
import { getDashboard, getPointsTrend } from '@/api';
import { ProfileCard, Schedule, PointsChart, AchievementWall, HomeworkList } from '@/components';

export const Dashboard: React.FC = () => {
  const { studentName = '小明' } = useParams();

  // 获取仪表盘数据
  const { data: dashboardData, loading: dashboardLoading, error: dashboardError } =
    useAPI(getDashboard, true, studentName);

  // 获取积分趋势数据
  const { data: pointsTrendData, loading: pointsLoading, error: pointsError } =
    useAPI(getPointsTrend, true, studentName, 7);

  if (dashboardLoading || pointsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="magic-spinner" />
      </div>
    );
  }

  if (dashboardError || pointsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="magic-card p-8 text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">加载失败</h2>
          <p className="text-gray-600">
            {(dashboardError || pointsError)?.message || '无法加载数据'}
          </p>
        </div>
      </div>
    );
  }

  if (!dashboardData || !pointsTrendData) {
    return null;
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* 页面标题 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold magic-title mb-2">
          ✨ 魔法学校学习仪表盘 ✨
        </h1>
        <p className="text-gray-600">
          欢迎, {dashboardData.profile.nickname || dashboardData.profile.name}!
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 学生档案 */}
        <div className="lg:col-span-2">
          <ProfileCard profile={dashboardData.profile} />
        </div>

        {/* 积分趋势 */}
        <div className="lg:col-span-2">
          <PointsChart data={pointsTrendData} />
        </div>

        {/* 课程表 */}
        <Schedule scheduleData={{
          weekdays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
          courses: dashboardData.todos.reduce((acc, todo) => {
            const day = todo.due_date ? new Date(todo.due_date).toLocaleDateString('zh-CN', { weekday: 'long' }) : '周一';
            if (!acc[day]) acc[day] = [];
            return acc;
          }, {} as Record<string, any[]>),
          statistics: {
            total_courses: 0,
            school_courses: 0,
            extra_courses: 0,
            course_count_by_day: {}
          },
          generated_at: new Date().toISOString()
        }} />

        {/* 成就墙 */}
        <AchievementWall data={{
          student_name: dashboardData.profile.name,
          total_achievements: dashboardData.stats.total_achievements,
          achievements_by_level: {
            bronze: 3,
            silver: 2,
            gold: 2,
            platinum: 1,
            diamond: 0
          },
          featured_achievements: dashboardData.recent_achievements.filter(a => a.is_featured),
          recent_achievements: dashboardData.recent_achievements,
          achievement_points: dashboardData.stats.total_achievements * 10,
          generated_at: new Date().toISOString()
        }} />
      </div>
    </div>
  );
};
