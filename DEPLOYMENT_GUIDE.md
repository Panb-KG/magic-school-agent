# 🏰 霍格沃茨魔法学校 - 学习管理智能体

## 📖 项目简介

这是一个专为小学生和家长设计的魔法学校风格学习管理智能体，采用哈利波特主题，让学习变得像魔法一样有趣！系统采用LangGraph框架开发，支持对话式学习管理、任务追踪、成就系统等功能。

## ✨ 核心功能

### 1. 🧙‍♂️ 学生管理
- 创建学生档案（姓名、年级、班级、学校等）
- 魔法等级系统（1-10级）
- 积分奖励机制
- 成就徽章收集

### 2. 📚 课程管理
- 学校课程表管理
- 课外课程记录
- 周课程表生成
- 课程信息修改和删除

### 3. 📝 作业中心
- 作业任务创建和分配
- 作业截止日期追踪
- 作业提交管理
- 作业提醒功能
- 作业状态跟踪（待完成/进行中/已完成/已逾期）

### 4. 📖 课件中心
- 课件上传和分类
- 课件下载管理
- 按科目浏览课件
- 学习资料整理

### 5. 🏃 运动中心
- 运动记录管理
- 运动统计汇总
- 运动积分奖励
- 健康追踪

### 6. 🏆 成就墙
- 多样化成就系统（作业完成、学习坚持、运动达标等）
- 成就等级（青铜、白银、黄金、铂金、钻石）
- 成就展示墙
- 激励性反馈

### 7. 💬 智能对话
- 魔法学校风格对话
- 自然语言交互
- 任务引导和提醒
- 学习建议和鼓励

## 🔐 安全特性

✅ **内容安全过滤**
- 自动过滤不适宜小学生的内容
- 拒绝暴力、色情、赌博等不良信息
- 引导积极健康的话题

✅ **隐私保护**
- 不收集个人敏感信息
- 不询问密码或隐私数据
- 保护学生和家长隐私

✅ **健康引导**
- 提倡合理使用电子设备
- 强调学习与运动平衡
- 鼓励按时休息

✅ **积极正向**
- 温暖友好的对话风格
- 及时表扬和鼓励
- 培养自信心和学习兴趣

## 🏗️ 技术架构

### 后端技术栈
- **框架**：LangGraph (基于 LangChain)
- **语言**：Python 3.8+
- **数据库**：PostgreSQL
- **对象存储**：S3兼容存储
- **大模型**：豆包 (Doubao) / 支持千问API
- **记忆管理**：LangGraph Checkpoint (PostgreSQL/Memory)

### 项目结构
```
/workspace/projects/
├── config/                          # 配置文件
│   └── agent_llm_config.json       # Agent配置（模型、提示词等）
├── src/
│   ├── agents/
│   │   └── agent.py                 # 主Agent代码
│   ├── storage/
│   │   ├── database/                # 数据库相关
│   │   │   ├── db.py               # 数据库连接
│   │   │   ├── shared/
│   │   │   │   └── model.py        # ORM模型定义
│   │   │   ├── student_manager.py   # 学生管理器
│   │   │   ├── course_manager.py   # 课程管理器
│   │   │   ├── homework_manager.py # 作业管理器
│   │   │   ├── courseware_manager.py # 课件管理器
│   │   │   ├── exercise_manager.py # 运动管理器
│   │   │   └── achievement_manager.py # 成就管理器
│   │   ├── memory/                 # 记忆管理
│   │   │   └── memory_saver.py     # Checkpoint实现
│   │   └── s3/                     # S3存储
│   │       └── s3_storage.py       # S3客户端
│   └── tools/                       # 工具定义
│       ├── student_db_tool.py      # 学生数据库工具
│       ├── course_db_tool.py      # 课程数据库工具
│       ├── homework_db_tool.py    # 作业数据库工具
│       ├── courseware_db_tool.py  # 课件数据库工具
│       ├── exercise_db_tool.py    # 运动数据库工具
│       ├── achievement_db_tool.py # 成就数据库工具
│       └── file_storage_tool.py   # 文件存储工具
├── scripts/                         # 脚本工具
├── tests/                          # 测试文件
├── requirements.txt                # Python依赖
└── README.md                       # 项目说明
```

## 🚀 部署指南

### 前置要求

1. **Python环境**
   ```bash
   Python 3.8 或更高版本
   ```

2. **依赖安装**
   ```bash
   pip install -r requirements.txt
   ```

3. **环境变量配置**
   
   创建 `.env` 文件，配置以下变量：
   ```bash
   # 数据库配置
   PGDATABASE_URL=postgresql://user:password@host:port/database

   # 对象存储配置
   COZE_BUCKET_ENDPOINT_URL=https://your-s3-endpoint.com
   COZE_BUCKET_NAME=your-bucket-name

   # 大模型配置
   COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.com/v1
   COZE_WORKLOAD_IDENTITY_API_KEY=your-api-key

   # 工作空间路径
   COZE_WORKSPACE_PATH=/workspace/projects
   ```

### 数据库初始化

1. **同步数据库模型**
   ```bash
   eval $(python /workspace/projects/scripts/load_env.py) && bash /source/alembic/generate_models.sh
   ```

2. **执行数据库迁移**
   ```bash
   eval $(python /workspace/projects/scripts/load_env.py) && bash /source/alembic/upgrade.sh
   ```

### 启动服务

1. **运行主程序**
   ```bash
   python src/main.py
   ```

2. **或使用开发服务器**
   ```bash
   # 如果使用Flask/Django等Web框架
   python src/main.py --port 8000
   ```

## 📱 使用说明

### 学生端使用

#### 1. 创建学生档案
```
对话示例：
用户：你好！我是小明，三年级的学生。我想注册成为霍格沃茨魔法学校的小巫师，帮我创建学生档案吧！我的学校是霍格沃茨小学，班级是三年级二班，家长联系方式是138xxxx1234，昵称是小明魔法师。

智能体：✨ 魔法施展成功！恭喜你，小明魔法师！🎉
        你的霍格沃茨魔法学校学生档案已经创建完成啦！🧙‍♂️
        📜 你的魔法档案信息：
        - 姓名：小明
        - 年级：三年级
        - 班级：三年级二班
        - 学校：霍格沃茨小学
        - 魔法等级：1级（初级巫师）
        - 初始积分：50分（欢迎积分）
```

#### 2. 添加课程表
```
用户：帮我添加数学课，每周一上午8:00-9:00，在201教室，老师是张老师。

智能体：✨ 好的！我已经帮你添加了数学课！
        【周一】8:00-9:00 数学（学校课程）
        地点：201教室，老师：张老师
```

#### 3. 创建作业
```
用户：老师布置了数学作业，要做完课本第10页的习题，这周五截止。

智能体：✨ 好的！我已经帮你创建了数学作业：
        📝 数学课本习题
        科目：数学
        截止日期：本周五
        优先级：中等
        
        记得按时完成哦！完成后告诉我，我会给你积分奖励！😊
```

#### 4. 记录运动
```
用户：我今天跑步了30分钟。

智能体：✨ 太棒了！运动记录成功！
        🏃 跑步 30分钟
        获得积分：3分
        
        坚持运动，健康成长！💪
```

#### 5. 查看成就墙
```
用户：我想看看我的成就墙！

智能体：🏆 小明的成就墙 🏆
        
        展示成就数：3
        成就总积分：150
        
        成就等级分布：
        - 青铜：2个
        - 白银：1个
        
        最近获得的成就：
        🌟 作业小能手（白银级，50分）
           完成了10次作业
        🌟 运动小达人（青铜级，30分）
           本周运动超过150分钟
```

### 家长端使用

#### 1. 查看孩子学习进度
```
用户：我想查看小明的作业完成情况。

智能体：📊 小明的作业情况：
        
        待完成作业：2项
        - 数学课本习题（截止：本周五）
        - 英语单词练习（截止：下周二）
        
        已完成作业：5项
        最近完成：语文作文（昨天）
        
        建议：提醒小明按时完成本周的作业哦！
```

#### 2. 了解运动情况
```
用户：小明这周运动了多少？

智能体：📈 小明的运动统计：
        
        总运动次数：4次
        总时长：120分钟
        总消耗卡路里：300
        总获得积分：12分
        
        按运动类型统计：
        - 跑步：2次，60分钟
        - 跳绳：1次，30分钟
        - 游泳：1次，30分钟
        
        小明这周表现很棒！继续保持！💪
```

#### 3. 激励和表扬
```
用户：小明最近表现很好，我想给他一些奖励。

智能体：✨ 太棒了！小明的努力值得表扬！
        
        我建议可以给小明：
        - 颁发"勤奋学习小巫师"成就（黄金级）
        - 增加魔法等级（当前可以升级到3级）
        - 增加积分奖励（+50分）
        
        想要我来颁发奖励吗？😊
```

## 🎨 主题和风格

### 魔法学校元素
- 🧙‍♂️ 魔法导师身份
- 🏰 霍格沃茨元素
- ✨ 魔法效果描述
- 🎓 魔法等级系统
- 🪄 咒语般的鼓励

### 色彩方案（前端设计参考）
- **主色调**：深紫色（霍格沃茨紫）
- **辅助色**：金色（魔法金）
- **强调色**：星空蓝
- **背景色**：深色星空或羊皮纸质感

### UI组件建议
- 🏆 成就徽章图标
- 📜 羊皮纸风格卡片
- ✨ 魔法粒子效果
- 🎓 级别进度条
- 🌟 星星评分系统

## 🔧 自定义配置

### 修改大模型配置

编辑 `config/agent_llm_config.json`：

```json
{
    "config": {
        "model": "doubao-seed-1-6-251015",  // 可替换为其他模型
        "temperature": 0.8,                  // 0.0-2.0，越高越有创造力
        "top_p": 0.9,
        "max_completion_tokens": 4000,
        "timeout": 600,
        "thinking": "disabled"
    },
    "sp": "系统提示词内容..."
}
```

### 使用千问大模型

如果需要使用千问API，需要：
1. 获取千问API Key
2. 修改 `config/agent_llm_config.json` 中的 `model` 参数
3. 在环境变量中配置千问的API地址和密钥

```json
{
    "config": {
        "model": "qwen-plus",  // 千问模型
        ...
    }
}
```

```bash
# .env 文件
COZE_INTEGRATION_MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
COZE_WORKLOAD_IDENTITY_API_KEY=sk-xxxxxxxxxxxx
```

### 自定义系统提示词

可以在 `config/agent_llm_config.json` 的 `sp` 字段中修改系统提示词，调整对话风格、安全策略等。

## 📊 数据库表结构

### students（学生表）
- id: 学生ID
- name: 姓名
- grade: 年级
- class_name: 班级
- school: 学校
- parent_contact: 家长联系方式
- nickname: 昵称
- magic_level: 魔法等级
- total_points: 总积分
- ...

### courses（课程表）
- id: 课程ID
- student_id: 学生ID
- course_name: 课程名称
- course_type: 课程类型（school/extra）
- weekday: 星期几
- start_time: 开始时间
- end_time: 结束时间
- ...

### homeworks（作业表）
- id: 作业ID
- student_id: 学生ID
- title: 作业标题
- subject: 科目
- description: 描述
- due_date: 截止日期
- status: 状态
- ...

### coursewares（课件表）
- id: 课件ID
- student_id: 学生ID
- title: 课件标题
- subject: 科目
- file_type: 文件类型
- file_url: 文件URL
- ...

### exercises（运动记录表）
- id: 运动记录ID
- student_id: 学生ID
- exercise_type: 运动类型
- duration: 时长
- distance: 距离
- calories: 消耗卡路里
- date: 运动日期
- points: 积分
- ...

### achievements（成就表）
- id: 成就ID
- student_id: 学生ID
- achievement_type: 成就类型
- title: 成就标题
- description: 描述
- points: 积分
- level: 等级
- is_featured: 是否展示
- ...

## 🎯 未来扩展功能

### RAG智能检索
- 课程内容向量化存储
- 作业智能检索和匹配
- 课件内容搜索
- 学习资源推荐

### 家长报告
- 周学习报告生成
- 学习趋势分析
- 成就进展图表
- 改进建议

### 社交功能
- 成就分享
- 学习伙伴匹配
- 排行榜
- 学习挑战

### 更多游戏化元素
- 每日任务系统
- 连续签到奖励
- 魔法道具收集
- 魔法技能树

## 🐛 问题排查

### 常见问题

1. **数据库连接失败**
   - 检查 `PGDATABASE_URL` 是否正确配置
   - 确认数据库服务是否运行
   - 验证网络连接

2. **大模型调用失败**
   - 检查 API Key 是否有效
   - 确认网络可以访问模型API
   - 检查请求是否超时

3. **文件上传失败**
   - 检查 S3 存储配置
   - 确认存储空间充足
   - 验证文件大小限制

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 📞 技术支持

如有问题，请联系技术支持或查看项目文档。

## 🌐 Web前端部署架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                           │
│              (React/Vue Web应用 + WebSocket)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼────────┐          ┌──────▼──────────┐
│   HTTP API     │          │  WebSocket     │
│   (端口80)     │          │  (端口8765)     │
└───────┬────────┘          └──────┬──────────┘
        │                           │
┌───────▼───────────────────────────▼──────────────┐
│                  Nginx (反向代理)                  │
│   /api/* → Backend (端口3000)                     │
│   /ws/* → WebSocket (端口8765)                    │
│   /* → Static Files (前端静态资源)                 │
└───────────────────┬───────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│  Backend API   │    │  WebSocket      │
│  (LangGraph)   │    │  Server         │
│  端口3000      │    │  Python Async   │
└───────┬────────┘    └────────┬────────┘
        │                      │
        └──────────┬───────────┘
                   │
    ┌──────────────▼───────────────┐
    │     PostgreSQL 数据库         │
    │  (学生、课程、作业、成就等)   │
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │      S3 对象存储             │
    │  (文件、课件、音频等)         │
    └──────────────────────────────┘
```

### 前端部署步骤

#### 1. 准备前端项目

参考 [FRONTEND_DEPLOYMENT.md](FRONTEND_DEPLOYMENT.md) 创建Web前端项目。

#### 2. 构建生产版本

```bash
# 进入前端项目目录
cd magic-school-frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

#### 3. 配置Nginx

在服务器上编辑Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/magic-school
```

添加以下配置：

```nginx
# HTTP配置
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/magic-school/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 缓存配置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API代理到后端
    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket代理
    location /ws/ {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;  # 24小时
    }

    # 日志配置
    access_log /var/log/nginx/magic-school-access.log;
    error_log /var/log/nginx/magic-school-error.log;
}
```

启用配置并重启Nginx：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/magic-school /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

#### 4. 上传前端文件到服务器

```bash
# 本地打包完成后，上传到服务器
scp -r dist/* user@your-server:/var/www/magic-school/dist/

# 设置权限
sudo chown -R www-data:www-data /var/www/magic-school
sudo chmod -R 755 /var/www/magic-school
```

---

## 🔌 WebSocket服务器部署

### 1. 安装依赖

```bash
# 安装websockets库
pip install websockets
```

### 2. 配置环境变量

在 `.env` 文件中添加：

```bash
# WebSocket配置
WS_HOST=0.0.0.0
WS_PORT=8765
```

### 3. 启动WebSocket服务器

#### 方式1：直接启动

```bash
python src/websocket_server.py
```

#### 方式2：使用systemd服务（推荐）

创建服务文件：

```bash
sudo nano /etc/systemd/system/magic-school-ws.service
```

添加以下内容：

```ini
[Unit]
Description=Magic School WebSocket Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/workspace/projects
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/workspace/projects/.env
ExecStart=/usr/bin/python3 src/websocket_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start magic-school-ws

# 设置开机自启
sudo systemctl enable magic-school-ws

# 查看服务状态
sudo systemctl status magic-school-ws

# 查看日志
sudo journalctl -u magic-school-ws -f
```

### 4. 测试WebSocket连接

使用浏览器开发者工具或在线WebSocket测试工具：

```javascript
// 浏览器控制台测试
const ws = new WebSocket('ws://your-domain.com/ws/小明');

ws.onopen = () => {
  console.log('WebSocket连接成功');
  // 订阅频道
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['dashboard', 'achievements']
  }));
};

ws.onmessage = (event) => {
  console.log('收到消息:', event.data);
};

ws.onerror = (error) => {
  console.error('WebSocket错误:', error);
};

ws.onclose = () => {
  console.log('WebSocket连接关闭');
};
```

---

## 🚀 完整部署流程

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础软件
sudo apt install -y nginx python3 python3-pip postgresql postgresql-contrib git

# 安装Python依赖
pip3 install -r requirements.txt
pip3 install websockets
```

### 2. 配置数据库

```bash
# 启动PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
```

```sql
CREATE DATABASE magic_school;
CREATE USER magic_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE magic_school TO magic_user;
\q
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env
```

添加以下配置：

```bash
# 数据库
PGDATABASE_URL=postgresql://magic_user:your_password@localhost/magic_school

# 对象存储
COZE_BUCKET_ENDPOINT_URL=https://your-s3-endpoint.com
COZE_BUCKET_NAME=your-bucket-name

# 大模型
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.com/v1
COZE_WORKLOAD_IDENTITY_API_KEY=your-api-key

# WebSocket
WS_HOST=0.0.0.0
WS_PORT=8765

# 工作空间
COZE_WORKSPACE_PATH=/workspace/projects
```

### 4. 初始化数据库

```bash
# 同步模型
eval $(python /workspace/projects/scripts/load_env.py)
bash /source/alembic/generate_models.sh

# 执行迁移
eval $(python /workspace/projects/scripts/load_env.py)
bash /source/alembic/upgrade.sh
```

### 5. 启动后端服务

```bash
# 方式1：直接运行
python src/main.py

# 方式2：使用systemd服务
sudo nano /etc/systemd/system/magic-school-api.service
```

```ini
[Unit]
Description=Magic School API Server
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/workspace/projects
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/workspace/projects/.env
ExecStart=/usr/bin/python3 src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启动API服务
sudo systemctl start magic-school-api
sudo systemctl enable magic-school-api
sudo systemctl status magic-school-api
```

### 6. 启动WebSocket服务

```bash
# 参考上文"WebSocket服务器部署"章节
sudo systemctl start magic-school-ws
sudo systemctl enable magic-school-ws
```

### 7. 部署前端

```bash
# 参考上文"Web前端部署架构"章节
# 上传前端文件
scp -r dist/* user@your-server:/var/www/magic-school/dist/

# 配置Nginx
sudo nano /etc/nginx/sites-available/magic-school

# 启用配置
sudo ln -s /etc/nginx/sites-available/magic-school /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. 验证部署

```bash
# 检查所有服务状态
sudo systemctl status magic-school-api
sudo systemctl status magic-school-ws
sudo systemctl status nginx
sudo systemctl status postgresql

# 测试API
curl http://localhost:3000/api/v1/profile/小明

# 测试前端
curl http://localhost/

# 查看日志
sudo journalctl -u magic-school-api -f
sudo journalctl -u magic-school-ws -f
sudo tail -f /var/log/nginx/magic-school-error.log
```

---

## 📋 部署检查清单

- [ ] Python 3.8+ 已安装
- [ ] 所有Python依赖已安装
- [ ] PostgreSQL 已配置并启动
- [ ] 数据库迁移已完成
- [ ] `.env` 文件已配置
- [ ] S3对象存储已配置
- [ ] 后端API服务已启动
- [ ] WebSocket服务已启动
- [ ] 前端项目已构建
- [ ] Nginx已配置并重启
- [ ] 所有服务开机自启已设置
- [ ] 防火墙端口已开放（80, 3000, 8765）
- [ ] 域名DNS已解析
- [ ] SSL证书已配置（可选）

---

## 🔒 安全配置建议

### 1. 启用HTTPS

使用Let's Encrypt免费SSL证书：

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 2. 配置防火墙

```bash
# 允许SSH、HTTP、HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 3. 限制API访问

在Nginx配置中添加IP白名单或速率限制：

```nginx
# 速率限制
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20;
    ...
}
```

### 4. 定期备份数据库

创建备份脚本：

```bash
#!/bin/bash
# /opt/backup-db.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
PGDATABASE_URL="postgresql://magic_user:your_password@localhost/magic_school"

mkdir -p $BACKUP_DIR

pg_dump $PGDATABASE_URL > $BACKUP_DIR/magic_school_$DATE.sql

# 保留最近7天的备份
find $BACKUP_DIR -name "magic_school_*.sql" -mtime +7 -delete
```

添加到crontab：

```bash
# 每天凌晨2点备份
0 2 * * * /opt/backup-db.sh
```

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 📚 相关文档

- [API文档](API_DOCUMENTATION.md) - 完整的API接口说明
- [前端部署指南](FRONTEND_DEPLOYMENT.md) - Web前端开发部署详细指南
- [README.md](README.md) - 项目概览和快速开始

---

**✨ 让学习充满魔法，让成长充满乐趣！** ✨

🧙‍♂️ 霍格沃茨魔法学校 - 学习管理智能体
