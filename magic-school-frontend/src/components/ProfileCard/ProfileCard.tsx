import React from 'react';
import type { StudentProfile } from '@/types';

interface ProfileCardProps {
  profile: StudentProfile;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({ profile }) => {
  const getLevelColor = (level: number) => {
    const colors = ['#9CA3AF', '#B45309', '#D97706', '#F59E0B', '#10B981', '#3B82F6', '#7C3AED'];
    return colors[Math.min(level - 1, colors.length - 1)];
  };

  const levelColor = getLevelColor(profile.magic_level);

  return (
    <div className="magic-card p-6">
      <div className="flex items-center space-x-4 mb-4">
        {/* 头像 */}
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-magic-primary to-magic-secondary flex items-center justify-center text-white text-3xl font-bold shadow-lg">
          {profile.nickname?.charAt(0) || profile.name.charAt(0)}
        </div>

        {/* 基本信息 */}
        <div className="flex-1">
          <h2 className="text-2xl font-bold magic-title mb-1">{profile.name}</h2>
          <p className="text-gray-600 mb-1">
            {profile.school} · {profile.class_name}
          </p>
          <div className="flex items-center space-x-2">
            <span
              className="px-3 py-1 rounded-full text-white text-sm font-semibold"
              style={{ backgroundColor: levelColor }}
            >
              等级 {profile.magic_level}
            </span>
            <span className="text-gray-500 text-sm">{profile.grade}</span>
          </div>
        </div>
      </div>

      {/* 积分展示 */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-700 font-semibold">魔法积分</span>
          <span className="text-2xl font-bold text-magic-primary">
            {profile.total_points}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className="magic-progress h-full rounded-full transition-all duration-500"
            style={{ width: `${profile.level_progress}%` }}
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-500">
          <span>当前进度</span>
          <span>
            {profile.level_progress}% · 还需 {profile.next_level_points - profile.total_points} 分升级
          </span>
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="bg-gradient-to-br from-magic-primary/10 to-magic-secondary/10 rounded-lg p-3">
          <div className="text-sm text-gray-600 mb-1">等级</div>
          <div className="text-xl font-bold text-magic-primary">
            {profile.magic_level}
          </div>
        </div>
        <div className="bg-gradient-to-br from-magic-secondary/10 to-magic-accent/10 rounded-lg p-3">
          <div className="text-sm text-gray-600 mb-1">总积分</div>
          <div className="text-xl font-bold text-magic-secondary">
            {profile.total_points}
          </div>
        </div>
      </div>
    </div>
  );
};
