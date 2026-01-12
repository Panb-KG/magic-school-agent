import React, { useState } from 'react';
import type { AchievementWallData } from '@/types';

interface AchievementWallProps {
  data: AchievementWallData;
}

export const AchievementWall: React.FC<AchievementWallProps> = ({ data }) => {
  const [filter, setFilter] = useState<'all' | 'featured' | 'recent'>('all');

  const getAchievementIcon = (type: string) => {
    const icons: Record<string, string> = {
      bronze: '🥉',
      silver: '🥈',
      gold: '🥇',
      platinum: '💎',
      diamond: '👑',
    };
    return icons[type] || '🏆';
  };

  const getAchievementColor = (type: string) => {
    const colors: Record<string, string> = {
      bronze: '#B45309',
      silver: '#6B7280',
      gold: '#F59E0B',
      platinum: '#3B82F6',
      diamond: '#7C3AED',
    };
    return colors[type] || '#9CA3AF';
  };

  const filteredAchievements = (() => {
    if (filter === 'featured') return data.featured_achievements;
    if (filter === 'recent') return data.recent_achievements;
    return [...data.featured_achievements, ...data.recent_achievements].slice(0, 10);
  })();

  return (
    <div className="magic-card p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold magic-title">🏆 成就墙</h2>
        <span className="text-sm text-gray-500">
          共 {data.total_achievements} 个成就
        </span>
      </div>

      {/* 成就统计 */}
      <div className="grid grid-cols-5 gap-3 mb-6">
        {Object.entries(data.achievements_by_level).map(([level, count]) => (
          <div
            key={level}
            className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-3 text-center"
          >
            <div className="text-2xl mb-1">{getAchievementIcon(level)}</div>
            <div className="text-lg font-bold text-gray-800">{count}</div>
            <div className="text-xs text-gray-500 capitalize">{level}</div>
          </div>
        ))}
      </div>

      {/* 筛选按钮 */}
      <div className="flex space-x-2 mb-6">
        {(['all', 'featured', 'recent'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              filter === f
                ? 'bg-magic-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {f === 'all' ? '全部' : f === 'featured' ? '精选' : '最新'}
          </button>
        ))}
      </div>

      {/* 成就列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredAchievements.map((achievement) => (
          <div
            key={achievement.id}
            className="achievement-card"
            style={{ borderColor: getAchievementColor(achievement.type) }}
          >
            <div className="flex items-start space-x-3">
              <div className="text-3xl">{getAchievementIcon(achievement.type)}</div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-gray-800">{achievement.title}</h3>
                  {achievement.is_featured && (
                    <span className="magic-badge">精选</span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  {achievement.description}
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">
                    📅 {new Date(achievement.unlocked_at).toLocaleDateString('zh-CN')}
                  </span>
                  <span className="text-sm font-semibold text-magic-primary">
                    +{achievement.points} 积分
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 总成就积分 */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">总成就积分</span>
          <span className="text-2xl font-bold text-magic-primary">
            {data.achievement_points}
          </span>
        </div>
      </div>
    </div>
  );
};
