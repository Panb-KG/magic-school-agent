#!/usr/bin/env python3
"""
策略一：功能完整性检查
从用户需求和业务功能角度检查 Agent 软件的完备性
"""

import sys
import os
from pathlib import Path
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 定义需要检查的功能模块
REQUIRED_FEATURES = {
    "智能对话中心": {
        "tools": ["memory_tool"],
        "description": "魔法助手聊天、学习问题咨询、日常对话交互、长期记忆对话",
        "status": "pending"
    },
    "课程日历": {
        "tools": ["course_db_tool"],
        "description": "课程时间管理、时间魔法查看、课程提醒",
        "status": "pending"
    },
    "作业中心": {
        "tools": ["homework_db_tool", "file_storage_tool"],
        "description": "作业记录、作业进度、作业提醒、历史作业、附件上传",
        "status": "pending"
    },
    "课件中心": {
        "tools": ["courseware_db_tool", "file_storage_tool"],
        "description": "课件管理、课件检索、时间标注、分类管理",
        "status": "pending"
    },
    "成就墙": {
        "tools": ["achievement_db_tool"],
        "description": "成就徽章、积分系统、等级晋升、成就展示",
        "status": "pending"
    },
    "运动中心": {
        "tools": ["exercise_db_tool"],
        "description": "运动记录、运动目标、运动提醒、运动统计",
        "status": "pending"
    },
    "教辅工具": {
        "tools": ["time_tool"],
        "description": "计算器、单位转换、公式查询、时间工具",
        "status": "pending"
    },
    "家长管理中心": {
        "tools": ["parent_tool"],
        "description": "学习监控、对话记录、成就查看、数据统计、长期记忆查看",
        "status": "pending"
    },
    "数据可视化": {
        "tools": ["visualization_tool", "dashboard_tool"],
        "description": "数据可视化、仪表盘、图表展示",
        "status": "pending"
    },
    "语音评估": {
        "tools": ["voice_assessment_tool"],
        "description": "朗读练习和评估",
        "status": "pending"
    },
    "学生管理": {
        "tools": ["student_db_tool"],
        "description": "学生信息管理、积分管理、等级管理",
        "status": "pending"
    },
    "长期记忆": {
        "tools": ["memory_tool"],
        "description": "用户画像、对话摘要、知识掌握度、个性化推荐",
        "status": "pending"
    }
}

REQUIRED_ROLES = ["student", "parent"]

REQUIRED_API_ENDPOINTS = [
    "用户认证（登录/注册/登出）",
    "学生管理（CRUD）",
    "课程管理（CRUD）",
    "作业管理（CRUD）",
    "课件管理（CRUD）",
    "成就管理（CRUD）",
    "运动记录（CRUD）",
    "家长-学生关联（CRUD）",
    "长期记忆（CRUD）",
    "对话接口（WebSocket）"
]


def check_tools():
    """检查工具文件的完整性"""
    tools_dir = Path(__file__).parent.parent / "src" / "tools"
    existing_tools = set()
    
    if tools_dir.exists():
        for file in tools_dir.glob("*_tool.py"):
            if not file.name.startswith("_") and file.name != "tool_utils.py":
                existing_tools.add(file.stem)
    
    return existing_tools


def check_agent():
    """检查 Agent 文件"""
    agent_file = Path(__file__).parent.parent / "src" / "agents" / "agent.py"
    return agent_file.exists()


def check_config():
    """检查配置文件"""
    config_file = Path(__file__).parent.parent / "config" / "agent_llm_config.json"
    if not config_file.exists():
        return False, "配置文件不存在"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必需字段
        required_fields = ['config', 'sp', 'tools']
        missing_fields = [f for f in required_fields if f not in config]
        
        if missing_fields:
            return False, f"配置文件缺少字段: {', '.join(missing_fields)}"
        
        # 检查 config 中的必需字段
        config_required = ['model', 'temperature', 'top_p', 'max_completion_tokens', 'timeout', 'thinking']
        missing_config = [f for f in config_required if f not in config['config']]
        
        if missing_config:
            return False, f"config 缺少字段: {', '.join(missing_config)}"
        
        return True, "配置文件完整"
    
    except Exception as e:
        return False, f"配置文件解析错误: {str(e)}"


def check_database_models():
    """检查数据库模型"""
    storage_dir = Path(__file__).parent.parent / "src" / "storage" / "database"
    
    # 检查模型文件
    model_files = [
        "shared/model.py",
        "student_manager.py",
        "homework_manager.py",
        "course_manager.py",
        "courseware_manager.py",
        "achievement_manager.py",
        "exercise_manager.py"
    ]
    
    missing_models = []
    for model_file in model_files:
        if not (storage_dir / model_file).exists():
            missing_models.append(model_file)
    
    return len(missing_models) == 0, missing_models


def check_frontend():
    """检查前端文件"""
    frontend_dir = Path(__file__).parent.parent / "magic-school-frontend"
    
    if not frontend_dir.exists():
        return False, "前端目录不存在"
    
    required_files = [
        "package.json",
        "src/App.tsx",
        "src/main.tsx"
    ]
    
    missing_files = []
    for file in required_files:
        if not (frontend_dir / file).exists():
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files


def run_functionality_check():
    """执行功能完整性检查"""
    print("=" * 80)
    print("策略一：功能完整性检查")
    print("=" * 80)
    print()
    
    # 1. 检查工具文件
    print("1️⃣ 工具文件检查")
    print("-" * 80)
    existing_tools = check_tools()
    print(f"已实现的工具数量: {len(existing_tools)}")
    print(f"已实现的工具: {', '.join(sorted(existing_tools))}")
    print()
    
    # 2. 功能模块检查
    print("2️⃣ 功能模块检查")
    print("-" * 80)
    
    feature_results = {}
    for feature_name, feature_info in REQUIRED_FEATURES.items():
        required_tools = feature_info["tools"]
        
        # 检查是否所有必需的工具都已实现
        implemented_tools = [t for t in required_tools if t in existing_tools]
        missing_tools = [t for t in required_tools if t not in existing_tools]
        
        if len(implemented_tools) == len(required_tools):
            status = "✅ 完成"
            feature_info["status"] = "completed"
        elif len(implemented_tools) > 0:
            status = f"⚠️  部分完成 (缺少: {', '.join(missing_tools)})"
            feature_info["status"] = "partial"
        else:
            status = f"❌ 未实现"
            feature_info["status"] = "missing"
        
        feature_results[feature_name] = {
            "status": feature_info["status"],
            "required_tools": required_tools,
            "implemented_tools": implemented_tools,
            "missing_tools": missing_tools
        }
        
        print(f"  {feature_name}: {status}")
        if missing_tools:
            print(f"    描述: {feature_info['description']}")
    
    print()
    
    # 3. Agent 配置检查
    print("3️⃣ Agent 配置检查")
    print("-" * 80)
    config_ok, config_msg = check_config()
    print(f"配置文件: {'✅' if config_ok else '❌'} {config_msg}")
    print()
    
    # 4. 数据库模型检查
    print("4️⃣ 数据库模型检查")
    print("-" * 80)
    models_ok, missing_models = check_database_models()
    if models_ok:
        print("✅ 所有数据库模型文件都存在")
    else:
        print(f"❌ 缺少数据库模型文件: {', '.join(missing_models)}")
    print()
    
    # 5. 前端检查
    print("5️⃣ 前端检查")
    print("-" * 80)
    frontend_ok, missing_frontend = check_frontend()
    if frontend_ok:
        print("✅ 前端文件完整")
    else:
        print(f"❌ 前端文件问题: {', '.join(missing_frontend)}")
    print()
    
    # 6. 统计结果
    print("6️⃣ 统计结果")
    print("-" * 80)
    
    completed_features = sum(1 for r in feature_results.values() if r["status"] == "completed")
    partial_features = sum(1 for r in feature_results.values() if r["status"] == "partial")
    missing_features = sum(1 for r in feature_results.values() if r["status"] == "missing")
    total_features = len(feature_results)
    
    print(f"功能模块总数: {total_features}")
    print(f"✅ 完成的功能: {completed_features} ({completed_features/total_features*100:.1f}%)")
    print(f"⚠️  部分完成的功能: {partial_features} ({partial_features/total_features*100:.1f}%)")
    print(f"❌ 未实现的功能: {missing_features} ({missing_features/total_features*100:.1f}%)")
    print()
    
    # 7. 生成建议
    print("7️⃣ 改进建议")
    print("-" * 80)
    
    if partial_features > 0:
        print("建议补充以下功能模块:")
        for feature_name, result in feature_results.items():
            if result["status"] == "partial":
                print(f"  - {feature_name}: 缺少工具 {', '.join(result['missing_tools'])}")
    
    if missing_features > 0:
        print("\n建议实现以下功能模块:")
        for feature_name, result in feature_results.items():
            if result["status"] == "missing":
                print(f"  - {feature_name}: {REQUIRED_FEATURES[feature_name]['description']}")
    
    print()
    print("=" * 80)
    
    return {
        "feature_results": feature_results,
        "config_ok": config_ok,
        "models_ok": models_ok,
        "frontend_ok": frontend_ok,
        "completed_features": completed_features,
        "partial_features": partial_features,
        "missing_features": missing_features
    }


if __name__ == "__main__":
    results = run_functionality_check()
    
    # 保存结果
    output_file = Path(__file__).parent / "strategy1_functionality_check.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n检查结果已保存到: {output_file}")
