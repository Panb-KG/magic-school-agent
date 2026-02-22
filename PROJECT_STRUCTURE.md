# 魔法课桌学习助手智能体 - 项目结构

## 目录结构

```
magic-school-agent/
├── .coze                          # 扣子IDE配置文件
├── .git/                          # Git版本控制
├── .gitignore                     # Git忽略文件配置
├── pytest.ini                     # pytest测试配置
├── requirements.txt               # Python依赖包列表
├── README.md                      # 项目说明文档
│
├── API_DOCUMENTATION.md           # API文档
├── DEPLOYMENT_GUIDE.md            # 部署指南
├── DOWNLOAD_INSTRUCTIONS.md       # 下载说明
├── FRONTEND_DEPLOYMENT.md         # 前端部署指南
├── FRONTEND_UPDATE_SUMMARY.md     # 前端更新摘要
│
├── src/                           # 源代码目录
│   ├── agents/                    # Agent代码
│   │   └── agent.py              # 主Agent逻辑
│   ├── auth/                      # 认证模块
│   │   ├── auth_utils.py         # 认证工具
│   │   ├── permissions.py        # 权限管理
│   │   ├── permissions_enhanced.py # 增强权限管理
│   │   └── user_manager.py       # 用户管理
│   ├── storage/                   # 存储模块
│   │   ├── database/             # 数据库相关
│   │   │   ├── db.py             # 数据库连接
│   │   │   ├── student_manager.py # 学生管理
│   │   │   ├── homework_manager.py # 作业管理
│   │   │   ├── course_manager.py   # 课程管理
│   │   │   ├── achievement_manager.py # 成就管理
│   │   │   ├── exercise_manager.py  # 运动管理
│   │   │   ├── courseware_manager.py # 课件管理
│   │   │   └── shared/           # 共享模型
│   │   │       └── model.py      # 数据库模型
│   │   └── memory/               # 记忆存储
│   │       └── memory_saver.py   # 记忆保存器
│   ├── tools/                     # 工具函数
│   │   ├── student_db_tool.py    # 学生数据库工具
│   │   ├── homework_db_tool.py   # 作业数据库工具
│   │   ├── course_db_tool.py     # 课程数据库工具
│   │   ├── achievement_db_tool.py # 成就数据库工具
│   │   ├── parent_tool.py        # 家长工具
│   │   ├── memory_tool.py        # 记忆工具
│   │   ├── time_tool.py          # 时间工具
│   │   ├── dashboard_tool.py     # 仪表盘工具
│   │   ├── file_storage_tool.py  # 文件存储工具
│   │   ├── voice_assessment_tool.py # 语音评估工具
│   │   ├── visualization_tool.py # 可视化工具
│   │   ├── logging_config.py     # 日志配置
│   │   └── tool_utils_fixed.py  # 工具辅助函数
│   ├── utils/                     # 工具类
│   │   ├── helper/               # 辅助函数
│   │   ├── error/                # 错误处理
│   │   ├── messages/             # 消息处理
│   │   └── log/                  # 日志处理
│   ├── main.py                    # 主入口文件
│   └── config.py                  # 配置文件
│
├── tests/                         # 测试目录
│   ├── conftest.py                # pytest全局配置
│   ├── test_base.py               # 测试基类
│   ├── README.md                  # 测试指南
│   └── tools/                     # 工具测试
│       └── test_student_db_tool.py # 学生工具测试
│
├── scripts/                       # 脚本目录
│   ├── cleanup_project.sh         # 项目清理脚本
│   ├── create_migration_tables.py  # 创建迁移表
│   ├── init_all_tables.py         # 初始化所有表
│   ├── init_business_tables.py    # 初始化业务表
│   ├── init_database.py           # 初始化数据库
│   ├── init_multiuser_schema.sql  # 多用户架构SQL
│   ├── init_business_tables.sql   # 业务表SQL
│   ├── init_test_data.py          # 初始化测试数据
│   ├── load_env.py               # 加载环境变量
│   ├── load_env.sh               # 加载环境变量脚本
│   ├── local_run.sh              # 本地运行脚本
│   ├── manage_agent.sh           # Agent管理脚本
│   ├── migrate.py                # 数据库迁移脚本
│   ├── mock_api_server.py        # Mock API服务器
│   ├── setup.sh                  # 安装脚本
│   ├── start_all_services.sh     # 启动所有服务
│   ├── start_all_services.bat    # 启动所有服务(Windows)
│   ├── start_frontend_dev.sh     # 启动前端开发服务器
│   ├── start_frontend_dev.bat    # 启动前端开发服务器(Windows)
│   ├── start_test_server.py      # 启动测试服务器
│   ├── test_agent.sh             # 测试Agent
│   ├── test_agent_api.sh         # 测试Agent API
│   ├── test_chat_api.sh          # 测试聊天API
│   ├── test_chat_api.bat         # 测试聊天API(Windows)
│   ├── test_full_functionality.py # 完整功能测试
│   ├── test_services.sh          # 测试服务
│   └── test_simple.sh            # 简单测试
│
├── config/                        # 配置目录
│   └── agent_llm_config.json     # Agent LLM配置
│
├── docs/                          # 文档目录
│   ├── Agent服务接入问题修复报告.md
│   ├── Agent软件完备性检查报告.md
│   ├── ECS部署调试指南.md
│   ├── GITHUB推送指南.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── MULTIUSER_GUIDE.md
│   ├── Mac访问服务器前端指南.md
│   ├── agent_software_error_handling_fix_report.md
│   ├── full_functionality_test_report.md
│   ├── students表关联修复指南.md
│   ├── 代码导出方案.md
│   ├── 公网访问问题完整解决方案.md
│   ├── 前后端连接架构图.md
│   ├── 前端界面访问指南.md
│   ├── 前端访问问题解决方案.md
│   ├── 前端调用智能体API示例.md
│   ├── 前端调用魔法课桌智能体快速开始.md
│   ├── 前端调用魔法课桌智能体指南.md
│   ├── 前端调试环境搭建完成.md
│   ├── 前端连接后端API指南.md
│   ├── 功能完备性评估报告.md
│   ├── 功能说明文档.md
│   ├── 后端API完整文档-Figma设计用.md
│   ├── 后端服务启动快速指南.md
│   ├── 后端服务启动指南.md
│   ├── 快速部署指南.md
│   ├── 扣子IDE与ECS部署说明.md
│   ├── 扣子平台快速部署.md
│   ├── 扣子平台部署指南.md
│   ├── 扣子平台配置模板.json
│   ├── 扣子编程Agent快速发布.md
│   ├── 扣子编程Agent部署快速指南.md
│   ├── 扣子编程Agent部署操作手册.md
│   ├── 扣子编程项目部署实际操作指南.md
│   ├── 数据库初始化指南.md
│   ├── 数据库迁移机制完善总结报告.md
│   ├── 数据库迁移机制问题分析.md
│   ├── 数据库迁移系统使用指南.md
│   ├── 数据隔离修复总结报告.md
│   ├── 数据隔离修复执行指南.md
│   ├── 本地运行前端应用指南.md
│   ├── 权限检查完善总结报告.md
│   ├── 测试执行报告与修复计划.md
│   ├── 测试评估报告-20260122.md
│   ├── 阿里云百炼API配置指南.md
│   ├── 项目打包完成-GitHub推送.md
│   └── 魔法课桌智能体部署方案分析.md
│
├── assets/                        # 资源目录
│   └── 魔法课桌学习助手_测试问题集-07920a228d.md
│
├── logs/                          # 日志目录（已清理）
│
├── migrations/                    # 数据库迁移
│   ├── 001_initial_schema.sql
│   ├── 002_add_user_auth.sql
│   ├── 003_add_parent_student_mapping.sql
│   └── migration_lock.sql
│
└── magic-school-frontend/          # 前端项目
    ├── node_modules/              # Node依赖
    ├── public/                    # 公共资源
    ├── src/                       # 源代码
    │   ├── components/           # 组件
    │   ├── pages/                # 页面
    │   ├── services/             # 服务
    │   ├── styles/               # 样式
    │   └── utils/                # 工具
    ├── .env                       # 环境变量
    ├── .gitignore                 # Git忽略
    ├── index.html                 # 入口HTML
    ├── package.json               # 项目配置
    ├── vite.config.js             # Vite配置
    └── tsconfig.json              # TypeScript配置
```

## 核心文件说明

### 源代码

- **src/agents/agent.py**: 主Agent逻辑，处理用户请求和工具调用
- **src/auth/**: 认证和权限管理模块
- **src/storage/database/**: 数据库操作和模型定义
- **src/tools/**: LangChain工具定义
- **src/utils/**: 通用工具类和辅助函数

### 配置文件

- **requirements.txt**: Python依赖包
- **pytest.ini**: pytest测试配置
- **config/agent_llm_config.json**: Agent LLM配置

### 脚本

- **scripts/start_all_services.sh**: 启动所有服务
- **scripts/start_frontend_dev.sh**: 启动前端开发服务器
- **scripts/cleanup_project.sh**: 清理项目中间文件
- **scripts/init_database.py**: 初始化数据库

### 测试

- **tests/**: pytest测试用例
- **scripts/test_full_functionality.py**: 完整功能测试

### 文档

- **README.md**: 项目说明
- **docs/**: 详细文档集合

## 开发环境要求

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- Git

## 快速开始

### 1. 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端
cd magic-school-frontend
npm install
```

### 2. 初始化数据库

```bash
python scripts/init_database.py
```

### 3. 启动服务

```bash
# 启动所有服务
./scripts/start_all_services.sh

# 或分别启动
# 后端
python src/main.py

# 前端
./scripts/start_frontend_dev.sh
```

### 4. 运行测试

```bash
# 单元测试
pytest

# 完整功能测试
python scripts/test_full_functionality.py
```

### 5. 清理项目

```bash
./scripts/cleanup_project.sh
```

## 部署说明

详细的部署指南请参考：
- **DEPLOYMENT_GUIDE.md**: 完整部署指南
- **FRONTEND_DEPLOYMENT.md**: 前端部署指南
- **docs/扣子平台部署指南.md**: 扣子平台部署

## 文档索引

### 核心文档
- README.md - 项目概述
- API_DOCUMENTATION.md - API文档
- 功能说明文档.md - 功能详细说明

### 部署文档
- DEPLOYMENT_GUIDE.md - 后端部署
- FRONTEND_DEPLOYMENT.md - 前端部署
- 扣子平台部署指南.md - 扣子平台部署

### 开发文档
- MULTIUSER_GUIDE.md - 多用户架构
- 后端服务启动指南.md - 服务启动
- 数据库初始化指南.md - 数据库初始化

### 报告文档
- full_functionality_test_report.md - 功能测试报告
- Agent软件完备性检查报告.md - 完备性检查
- agent_software_error_handling_fix_report.md - 错误处理修复报告

## 维护说明

### 定期清理

运行清理脚本删除中间文件：

```bash
./scripts/cleanup_project.sh
```

### 数据库迁移

使用迁移脚本更新数据库：

```bash
python scripts/migrate.py
```

### 日志查看

日志文件位于 `logs/` 目录，定期清理。

## 注意事项

1. 不要提交敏感信息（如API密钥）到版本控制
2. 使用环境变量管理配置
3. 定期运行测试确保功能正常
4. 及时更新依赖包
5. 遵循代码规范和文档格式
