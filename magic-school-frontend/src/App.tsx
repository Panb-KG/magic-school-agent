import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Dashboard, SchedulePage, AchievementsPage, HomeworkPage } from '@/pages';

function App() {
  const studentName = '小明';

  return (
    <Router>
      <div className="min-h-screen">
        {/* 导航栏 */}
        <nav className="bg-white/95 backdrop-blur-sm shadow-lg sticky top-0 z-50">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <div className="flex items-center space-x-2">
                <span className="text-3xl">⚡</span>
                <span className="text-xl font-bold magic-title">魔法学校</span>
              </div>

              {/* 导航链接 */}
              <div className="flex space-x-1 md:space-x-4">
                <Link
                  to={`/dashboard/${studentName}`}
                  className="px-3 py-2 rounded-lg text-sm md:text-base font-semibold text-gray-700 hover:text-magic-primary hover:bg-magic-primary/10 transition-all"
                >
                  📊 仪表盘
                </Link>
                <Link
                  to={`/schedule/${studentName}`}
                  className="px-3 py-2 rounded-lg text-sm md:text-base font-semibold text-gray-700 hover:text-magic-primary hover:bg-magic-primary/10 transition-all"
                >
                  📚 课程表
                </Link>
                <Link
                  to={`/achievements/${studentName}`}
                  className="px-3 py-2 rounded-lg text-sm md:text-base font-semibold text-gray-700 hover:text-magic-primary hover:bg-magic-primary/10 transition-all"
                >
                  🏆 成就墙
                </Link>
                <Link
                  to={`/homework/${studentName}`}
                  className="px-3 py-2 rounded-lg text-sm md:text-base font-semibold text-gray-700 hover:text-magic-primary hover:bg-magic-primary/10 transition-all"
                >
                  📝 作业
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* 路由 */}
        <Routes>
          <Route path="/dashboard/:studentName" element={<Dashboard />} />
          <Route path="/schedule/:studentName" element={<SchedulePage />} />
          <Route path="/achievements/:studentName" element={<AchievementsPage />} />
          <Route path="/homework/:studentName" element={<HomeworkPage />} />
          <Route
            path="/"
            element={<Dashboard />}
          />
        </Routes>

        {/* 页脚 */}
        <footer className="bg-white/95 backdrop-blur-sm mt-12 py-8 border-t border-gray-200">
          <div className="container mx-auto px-4 text-center">
            <p className="text-gray-600">
              ⚡ 魔法学校学习管理系统 · 让学习充满魔法
            </p>
            <p className="text-sm text-gray-500 mt-2">
              © 2025 Magic School. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
