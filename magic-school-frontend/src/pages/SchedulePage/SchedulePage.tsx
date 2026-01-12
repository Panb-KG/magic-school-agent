import React from 'react';
import { useParams } from 'react-router-dom';
import { useAPI } from '@/hooks/useAPI';
import { getSchedule } from '@/api';
import { Schedule as ScheduleComponent } from '@/components';

export const SchedulePage: React.FC = () => {
  const { studentName = '小明' } = useParams();

  const { data: scheduleData, loading, error } = useAPI(getSchedule, true, studentName);

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

  if (!scheduleData) {
    return null;
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* 页面标题 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold magic-title mb-2">
          📚 魔法课程表
        </h1>
        <p className="text-gray-600">
          查看 {studentName} 的课程安排
        </p>
      </div>

      <div className="max-w-4xl mx-auto">
        <ScheduleComponent scheduleData={scheduleData} />
      </div>
    </div>
  );
};
