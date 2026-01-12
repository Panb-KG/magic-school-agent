import React, { useState } from 'react';
import type { ScheduleData, Course } from '@/types';

interface ScheduleProps {
  scheduleData: ScheduleData;
}

export const Schedule: React.FC<ScheduleProps> = ({ scheduleData }) => {
  const [selectedDay, setSelectedDay] = useState('周一');

  const courses = scheduleData.courses[selectedDay] || [];

  const getCourseTypeColor = (type: string) => {
    return type === 'school'
      ? 'border-l-magic-primary bg-gradient-to-r from-magic-primary/5 to-transparent'
      : 'border-l-magic-secondary bg-gradient-to-r from-magic-secondary/5 to-transparent';
  };

  const getCourseTypeLabel = (type: string) => {
    return type === 'school' ? '必修' : '选修';
  };

  return (
    <div className="magic-card p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold magic-title">📚 课程表</h2>
        <span className="text-sm text-gray-500">
          共 {scheduleData.statistics.total_courses} 节课
        </span>
      </div>

      {/* 星期选择器 */}
      <div className="flex overflow-x-auto space-x-2 mb-6 pb-2">
        {scheduleData.weekdays.map((day) => (
          <button
            key={day}
            onClick={() => setSelectedDay(day)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
              selectedDay === day
                ? 'bg-magic-primary text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            {day}
          </button>
        ))}
      </div>

      {/* 课程列表 */}
      <div className="space-y-3">
        {courses.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-3">📭</div>
            <p>今天没有课程</p>
          </div>
        ) : (
          courses.map((course: Course) => (
            <div
              key={course.id}
              className={`course-card p-4 ${getCourseTypeColor(course.type)}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-bold text-gray-800 mb-1">{course.name}</h3>
                  <p className="text-sm text-gray-600">
                    🕐 {course.time} · 📍 {course.location}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    course.type === 'school'
                      ? 'bg-magic-primary/10 text-magic-primary'
                      : 'bg-magic-secondary/10 text-magic-secondary'
                  }`}
                >
                  {getCourseTypeLabel(course.type)}
                </span>
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>👨‍🏫 {course.teacher}</span>
                {course.notes && <span className="italic">📝 {course.notes}</span>}
              </div>
            </div>
          ))
        )}
      </div>

      {/* 课程统计 */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">必修课程</span>
            <span className="font-semibold text-magic-primary">
              {scheduleData.statistics.school_courses} 节
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">选修课程</span>
            <span className="font-semibold text-magic-secondary">
              {scheduleData.statistics.extra_courses} 节
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
