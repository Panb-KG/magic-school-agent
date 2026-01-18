import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useAPI } from '@/hooks/useAPI';
import { getAchievementWall } from '@/api';
import { AchievementWall } from '@/components';

export const AchievementsPage: React.FC = () => {
  const { user } = useAuth();
  const studentName = user?.student_name || user?.nickname || '小巫师';

  const { data: achievementData, loading, error } = useAPI(getAchievementWall, true, studentName);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="magic-spinner" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="magic-card p-8 text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">加载失败</h2>
          <p className="text-gray-600">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!achievementData) {
    return null;
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* 页面标题 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold magic-title mb-2">
          🏆 成就墙
        </h1>
        <p className="text-gray-600">
          查看 {studentName} 的魔法成就
        </p>
      </div>

      <div className="max-w-5xl mx-auto">
        <AchievementWall data={achievementData} />
      </div>
    </div>
  );
};
