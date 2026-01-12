# 魔法学校学习管理系统 - API 文档

## 📖 概述

本文档描述了魔法学校学习管理系统的后端API接口。所有接口均返回JSON格式的数据，供前端Web应用使用。

**基础信息**
- API版本：v1.0
- 数据格式：JSON
- 字符编码：UTF-8

---

## 🔗 基础URL

```
http://your-server-ip:port/api/v1
```

---

## 📡 API 接口列表

### 1. 学生档案

#### 1.1 获取学生仪表盘数据

获取学生的完整仪表盘信息，包括档案、统计数据、成就、待办事项等。

**接口**
```
GET /dashboard/{student_name}
```

**请求参数**
- `student_name` (string, 必填): 学生姓名

**响应示例**
```json
{
  "profile": {
    "id": 1,
    "name": "小明",
    "grade": "三年级",
    "class_name": "三年级二班",
    "school": "霍格沃茨小学",
    "nickname": "小明",
    "avatar_url": "",
    "magic_level": 2,
    "total_points": 150,
    "level_progress": 50,
    "next_level_points": 200
  },
  "stats": {
    "total_points": 150,
    "magic_level": 2,
    "completed_homeworks": 12,
    "pending_homeworks": 3,
    "total_exercises": 15,
    "total_exercise_minutes": 240,
    "total_achievements": 8,
    "featured_achievements": 5,
    "homework_completion_rate": 80.0
  },
  "recent_achievements": [...],
  "todos": [
    {
      "id": 5,
      "title": "数学练习题",
      "subject": "数学",
      "due_date": "2025-01-20",
      "days_left": 2,
      "urgency": "medium",
      "type": "homework"
    }
  ],
  "suggestions": [...],
  "week_stats": {
    "total_points": 45,
    "breakdown": {
      "homework": 30,
      "exercise": 15,
      "reading": 0,
      "other": 0
    }
  },
  "generated_at": "2025-01-18 15:30:00"
}
```

**字段说明**
- `profile`: 学生档案信息
  - `level_progress`: 当前等级进度（0-100）
  - `next_level_points`: 下一等级所需积分
- `stats`: 统计数据
  - `homework_completion_rate`: 作业完成率（百分比）
- `todos`: 待办事项
  - `urgency`: 优先级（high/medium/low）

---

#### 1.2 获取学生档案摘要

获取学生的简化档案信息，用于展示卡片。

**接口**
```
GET /profile/{student_name}
```

**请求参数**
- `student_name` (string, 必填): 学生姓名

**响应示例**
```json
{
  "id": 1,
  "name": "小明",
  "nickname": "小明",
  "grade": "三年级",
  "class_name": "三年级二班",
  "school": "霍格沃茨小学",
  "avatar_url": "",
  "magic_level": 2,
  "total_points": 150,
  "level_progress": 50,
  "level_percentage": 50.0,
  "achievements_by_level": {
    "bronze": 3,
    "silver": 2,
    "gold": 2,
    "platinum": 1,
    "diamond": 0
  },
  "featured_count": 5,
  "total_achievement_points": 80
}
```

---

### 2. 课程表

#### 2.1 获取可视化课程表

获取学生的一周课程表数据，按星期分组。

**接口**
```
GET /schedule/{student_name}
```

**请求参数**
- `student_name` (string, 必填): 学生姓名

**响应示例**
```json
{
  "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
  "courses": {
    "周一": [
      {
        "id": 1,
        "name": "数学课",
        "type": "school",
        "time": "08:00-09:00",
        "location": "201教室",
        "teacher": "张老师",
        "classroom": "201教室",
        "notes": ""
      }
    ],
    "周二": [...],
    ...
  },
  "statistics": {
    "total_courses": 15,
    "school_courses": 10,
    "extra_courses": 5,
    "course_count_by_day": {
      "周一": 3,
      "周二": 3,
      ...
    }
  },
  "generated_at": "2025-01-18 15:30:00"
}
```

**字段说明**
- `type`: 课程类型（school/extra）

---

### 3. 积分图表

#### 3.1 获取积分趋势数据

获取指定天数内的积分增长趋势，用于绘制折线图。

**接口**
```
GET /points-trend/{student_name}?days=30
```

**请求参数**
- `student_name` (string, 必填): 学生姓名
- `days` (integer, 可选): 查询天数，默认30天

**响应示例**
```json
{
  "date_list": ["2025-01-01", "2025-01-02", ...],
  "daily_points": [10, 15, 0, 20, ...],
  "cumulative_points": [10, 25, 25, 45, ...],
  "breakdown": {
    "homework": 120,
    "exercise": 60,
    "reading": 30,
    "course_complete": 20,
    "other": 10
  },
  "summary": {
    "total_points": 240,
    "average_daily": 8.0,
    "max_daily": 25,
    "days_with_points": 20
  },
  "generated_at": "2025-01-18 15:30:00"
}
```

**字段说明**
- `daily_points`: 每日获得积分
- `cumulative_points`: 累计积分（用于绘制增长曲线）
- `breakdown`: 积分来源分布（用于绘制饼图）

---

### 4. 成就墙

#### 4.1 获取成就墙数据

获取学生的成就墙展示数据，按类型和等级分类。

**接口**
```
GET /achievement-wall/{student_name}
```

**请求参数**
- `student_name` (string, 必填): 学生姓名

**响应示例**
```json
{
  "featured": [
    {
      "id": 1,
      "title": "作业小能手",
      "description": "完成10个作业",
      "points": 20,
      "level": "gold",
      "icon_url": "",
      "achieved_date": "2025-01-15"
    }
  ],
  "by_type": {
    "homework_goal": [...],
    "exercise_goal": [...],
    "reading_goal": [...]
  },
  "by_level": {
    "bronze": [...],
    "silver": [...],
    "gold": [...],
    "platinum": [...],
    "diamond": [...]
  },
  "recent": [
    {
      "id": 8,
      "title": "朗读达人",
      "description": "朗读评分达到90分以上",
      "type": "reading_goal",
      "points": 20,
      "level": "gold",
      "icon_url": "",
      "achieved_date": "2025-01-18"
    }
  ],
  "summary": {
    "total_count": 8,
    "featured_count": 5,
    "total_points": 150,
    "type_distribution": {
      "homework_goal": 3,
      "exercise_goal": 2,
      "reading_goal": 2,
      "other": 1
    },
    "level_distribution": {
      "bronze": 3,
      "silver": 2,
      "gold": 2,
      "platinum": 1,
      "diamond": 0
    }
  },
  "generated_at": "2025-01-18 15:30:00"
}
```

**字段说明**
- `featured`: 精选成就（用于展示墙）
- `level`: 成就等级（bronze/silver/gold/platinum/diamond）

---

### 5. 作业进度

#### 5.1 获取作业进度数据

获取学生的作业完成情况，用于进度展示。

**接口**
```
GET /homework-progress/{student_name}
```

**请求参数**
- `student_name` (string, 必填): 学生姓名

**响应示例**
```json
{
  "statistics": {
    "total": 15,
    "completed": 12,
    "pending": 3,
    "overdue": 0,
    "completion_rate": 80.0
  },
  "week_statistics": {
    "total": 5,
    "completed": 4,
    "completion_rate": 80.0
  },
  "pending": [
    {
      "id": 15,
      "title": "数学练习题",
      "subject": "数学",
      "due_date": "2025-01-20",
      "days_left": 2,
      "is_urgent": true,
      "priority": "high",
      "description": "完成第1-10页"
    }
  ],
  "completed": [
    {
      "id": 10,
      "title": "语文朗读",
      "subject": "语文",
      "completed_date": "2025-01-17",
      "points": 15,
      "feedback": ""
    }
  ],
  "generated_at": "2025-01-18 15:30:00"
}
```

**字段说明**
- `is_urgent`: 是否紧急（2天内到期）
- `priority`: 优先级（low/medium/high）

---

## 🔐 认证

当前版本暂未实现用户认证，后续将添加JWT Token认证机制。

---

## 📡 响应格式

### 成功响应
```json
{
  "data": {
    // 数据内容
  },
  "message": "success",
  "code": 200
}
```

### 错误响应
```json
{
  "error": "错误描述",
  "code": 400
}
```

**常见错误码**
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器内部错误

---

## 🔄 实时更新（WebSocket）

### WebSocket 连接

用于实时接收数据更新通知。

**连接地址**
```
ws://your-server-ip:port/ws/{student_name}
```

**消息格式**

**客户端发送**
```json
{
  "type": "subscribe",
  "channels": ["dashboard", "achievements", "homework"]
}
```

**服务端推送**
```json
{
  "type": "update",
  "channel": "dashboard",
  "data": {
    "updated_at": "2025-01-18 15:30:00",
    "changes": ["profile", "stats"]
  }
}
```

**消息类型**
- `dashboard`: 仪表盘数据更新
- `achievements`: 新成就解锁
- `homework`: 作业状态变更
- `points`: 积分更新

---

## 🎨 前端使用建议

### 1. 学生档案卡片

使用 `/profile/{student_name}` 接口获取数据，展示：

- **头像和基本信息**：avatar_url, name, nickname, grade
- **魔法等级**：magic_level, level_progress（进度条）
- **成就统计**：achievements_by_level（不同等级徽章数量）

### 2. 周课程表

使用 `/schedule/{student_name}` 接口获取数据，展示：

- **时间轴视图**：按星期排列课程
- **课程类型标识**：school用蓝色，extra用绿色
- **详细信息**：点击可查看时间、地点、老师等

### 3. 积分图表

使用 `/points-trend/{student_name}` 接口获取数据，展示：

- **折线图**：使用 `date_list` 和 `cumulative_points` 绘制累计积分曲线
- **柱状图**：使用 `date_list` 和 `daily_points` 绘制每日积分
- **饼图**：使用 `breakdown` 绘制积分来源分布

推荐图表库：
- **ECharts**: 功能强大，适合复杂图表
- **Chart.js**: 轻量级，易上手
- **Recharts**: React生态，组件化

### 4. 成就墙

使用 `/achievement-wall/{student_name}` 接口获取数据，展示：

- **徽章展示**：使用 `featured` 数组，按 `level` 区分颜色
- **分类查看**：使用 `by_type` 按成就类型分组
- **时间轴**：使用 `recent` 展示最新成就

成就等级颜色建议：
- 🥉 Bronze: #CD7F32
- 🥈 Silver: #C0C0C0
- 🥇 Gold: #FFD700
- 💎 Platinum: #E5E4E2
- 💠 Diamond: #B9F2FF

---

## 📊 数据可视化示例

### ECharts 折线图配置

```javascript
// 获取积分趋势数据
fetch('/api/v1/points-trend/小明?days=30')
  .then(res => res.json())
  .then(data => {
    const option = {
      title: { text: '积分增长趋势' },
      xAxis: { data: data.date_list },
      yAxis: { type: 'value' },
      series: [{
        type: 'line',
        data: data.cumulative_points,
        smooth: true,
        lineStyle: { color: '#4CAF50' },
        areaStyle: { color: 'rgba(76, 175, 80, 0.1)' }
      }]
    };
    myChart.setOption(option);
  });
```

### ECharts 饼图配置

```javascript
// 获取积分趋势数据，绘制来源分布
fetch('/api/v1/points-trend/小明?days=30')
  .then(res => res.json())
  .then(data => {
    const breakdown = data.breakdown;
    const option = {
      title: { text: '积分来源分布' },
      series: [{
        type: 'pie',
        data: [
          { value: breakdown.homework, name: '作业' },
          { value: breakdown.exercise, name: '运动' },
          { value: breakdown.reading, name: '朗读' },
          { value: breakdown.course_complete, name: '课程' },
          { value: breakdown.other, name: '其他' }
        ]
      }]
    };
    myChart.setOption(option);
  });
```

---

## 🚀 部署说明

完整的部署指南请参考 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)。

---

## 📞 联系支持

如有问题，请联系开发团队。
