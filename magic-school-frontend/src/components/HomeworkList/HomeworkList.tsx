import React from 'react';
import type { HomeworkProgress } from '@/types';

interface HomeworkListProps {
  data: HomeworkProgress;
}

export const HomeworkList: React.FC<HomeworkListProps> = ({ data }) => {
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: 'bg-green-100 text-green-700',
      pending: 'bg-yellow-100 text-yellow-700',
      overdue: 'bg-red-100 text-red-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      completed: '已完成',
      pending: '待完成',
      overdue: '已逾期',
    };
    return labels[status] || status;
  };

  const getUrgencyColor = (daysLeft: number) => {
    if (daysLeft < 0) return 'text-red-500';
    if (daysLeft <= 2) return 'text-orange-500';
    return 'text-gray-500';
  };

  return (
    <div className="magic-card p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold magic-title">📝 作业进度</h2>
        <span className="text-sm text-gray-500">
          完成率 {data.completion_rate.toFixed(1)}%
        </span>
      </div>

      {/* 进度统计 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-600 mb-1">
            {data.completed}
          </div>
          <div className="text-sm text-gray-600">已完成</div>
        </div>
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-yellow-600 mb-1">
            {data.pending}
          </div>
          <div className="text-sm text-gray-600">待完成</div>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-600 mb-1">
            {data.overdue}
          </div>
          <div className="text-sm text-gray-600">已逾期</div>
        </div>
      </div>

      {/* 进度条 */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="magic-progress h-full rounded-full transition-all duration-500"
            style={{ width: `${data.completion_rate}%` }}
          />
        </div>
      </div>

      {/* 学科统计 */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-700 mb-3">按学科统计</h3>
        <div className="space-y-2">
          {data.subjects.map((subject) => (
            <div
              key={subject.subject}
              className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
            >
              <span className="font-semibold text-gray-700">{subject.subject}</span>
              <div className="flex items-center space-x-4 text-sm">
                <span className="text-green-600">✓ {subject.completed}</span>
                <span className="text-yellow-600">⏰ {subject.pending}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 作业列表 */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">作业列表</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {data.homeworks.map((homework) => (
            <div
              key={homework.id}
              className="flex justify-between items-center p-3 bg-white border border-gray-200 rounded-lg hover:border-magic-primary transition-all"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <h4 className="font-semibold text-gray-800">{homework.title}</h4>
                  <span className="px-2 py-0.5 rounded text-xs font-semibold">
                    {homework.subject}
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  📅 {new Date(homework.due_date).toLocaleDateString('zh-CN')}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(homework.status)}`}>
                  {getStatusLabel(homework.status)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
