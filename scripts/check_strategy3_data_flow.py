#!/usr/bin/env python3
"""
策略三：数据流检查
从数据角度检查数据模型的完整性、数据流转的正确性和数据一致性
"""

import sys
import os
from pathlib import Path
import re
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


# 定义预期的数据表结构
EXPECTED_TABLES = {
    "auth": {
        "users": ["user_id", "username", "password_hash", "role", "student_name", "grade", "created_at", "updated_at"],
        "parent_student_mapping": ["mapping_id", "parent_id", "student_id", "relationship", "created_at"],
        "permissions": ["permission_id", "permission_name", "description", "category"],
        "role_permissions": ["role", "permission_id"],
        "user_sessions": ["session_id", "user_id", "thread_id", "created_at", "last_active_at", "is_active"]
    },
    "memory": {
        "user_profile": ["profile_id", "user_id", "preferences", "learning_goals", "learning_style", "favorite_subjects", "weak_subjects", "created_at", "updated_at"],
        "conversation_summary": ["summary_id", "user_id", "thread_id", "topic", "summary_text", "key_points", "emotion", "importance_score", "conversation_date", "created_at"],
        "knowledge_mastery": ["mastery_id", "user_id", "subject", "topic", "mastery_level", "last_reviewed_at", "practice_count", "correct_rate", "created_at", "updated_at"],
        "behavior_preferences": ["preference_id", "user_id", "chat_style", "preferred_response_length", "question_types", "feedback_records", "created_at", "updated_at"],
        "important_conversations": ["conversation_id", "user_id", "thread_id", "conversation_type", "conversation_content", "summary", "tags", "saved_at"]
    },
    "public": {
        "students": ["id", "user_id", "name", "grade", "class_name", "school", "parent_contact", "nickname", "avatar_url", "is_active", "magic_level", "total_points", "created_at", "updated_at"],
        "courses": ["id", "student_id", "course_name", "course_type", "weekday", "start_time", "end_time", "location", "teacher", "classroom", "is_recurring", "notes", "created_at", "updated_at"],
        "homeworks": ["id", "student_id", "title", "subject", "description", "due_date", "status", "priority", "attachment_url", "submission_url", "points", "feedback", "category", "reminder_sent", "created_at", "updated_at"],
        "coursewares": ["id", "student_id", "title", "subject", "file_type", "file_url", "description", "created_at", "updated_at"],
        "exercises": ["id", "student_id", "exercise_type", "duration", "date", "notes", "created_at"],
        "achievements": ["id", "student_id", "achievement_name", "achievement_type", "icon_url", "description", "points", "earned_at"]
    }
}


def check_data_model():
    """检查数据模型的完整性"""
    print("1️⃣ 数据模型完整性检查")
    print("-" * 80)
    
    model_dir = Path(__file__).parent.parent / "src" / "storage" / "database"
    issues = []
    
    # 检查每个 schema 的模型文件
    for schema, tables in EXPECTED_TABLES.items():
        if schema == "auth":
            model_file = model_dir / "shared" / "model.py"
        elif schema == "public":
            # 检查各个 manager 文件
            pass
        else:
            model_file = model_dir / schema / "model.py" if schema != "public" else None
        
        if model_file and not model_file.exists():
            issues.append(f"{schema} schema 的模型文件不存在")
    
    # 检查 Pydantic 模型
    for manager_file in ["student_manager.py", "homework_manager.py", "course_manager.py"]:
        file_path = model_dir / manager_file
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有 Create 和 Update 模型
            if "Create(" not in content:
                issues.append(f"{manager_file} 缺少 Create 模型")
            if "Update(" not in content:
                issues.append(f"{manager_file} 缺少 Update 模型")
    
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ 数据模型完整")
    
    return issues


def check_data_isolation():
    """检查数据隔离机制"""
    print("\n2️⃣ 数据隔离机制检查")
    print("-" * 80)
    
    issues = []
    
    # 检查 students 表是否有 user_id
    student_manager = Path(__file__).parent.parent / "src" / "storage" / "database" / "student_manager.py"
    if student_manager.exists():
        with open(student_manager, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "user_id" not in content:
            issues.append("students 表模型缺少 user_id 字段")
        else:
            print("  ✅ students 表包含 user_id 字段")
    else:
        issues.append("student_manager.py 不存在")
    
    # 检查权限检查系统
    permissions_file = Path(__file__).parent.parent / "src" / "auth" / "permissions_enhanced.py"
    if permissions_file.exists():
        print("  ✅ 权限检查系统存在")
    else:
        issues.append("权限检查系统不存在")
    
    # 检查工具是否使用 student_id 而不是 student_name
    tools_dir = Path(__file__).parent.parent / "src" / "tools"
    tools_with_name = []
    
    for tool_file in tools_dir.glob("*_tool.py"):
        if tool_file.name.startswith("_"):
            continue
        
        with open(tool_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查函数签名中是否还有 student_name 参数
        matches = re.findall(r'def\s+\w+\([^)]*student_name[^)]*\)', content)
        if matches:
            tools_with_name.append(tool_file.name)
    
    if tools_with_name:
        issues.append(f"以下工具仍使用 student_name 参数: {', '.join(tools_with_name)}")
    else:
        print("  ✅ 所有工具都已使用 student_id")
    
    # 检查权限检查装饰器的使用
    tools_without_check = []
    for tool_file in tools_dir.glob("*_tool.py"):
        if tool_file.name.startswith("_") or tool_file.name.endswith("fixed.py"):
            continue
        
        with open(tool_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有 @tool 装饰器但没有权限检查
        has_tool = '@tool' in content
        has_permission_check = '@require_student_access' in content or 'check_student_access' in content
        
        if has_tool and not has_permission_check and 'student_id' in content:
            tools_without_check.append(tool_file.name)
    
    if tools_without_check:
        issues.append(f"以下工具缺少权限检查: {', '.join(tools_without_check)}")
    else:
        print("  ✅ 所有需要权限检查的工具都已添加")
    
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    
    return issues


def check_data_consistency():
    """检查数据一致性"""
    print("\n3️⃣ 数据一致性检查")
    print("-" * 80)
    
    issues = []
    
    # 检查外键约束
    migration_files = list((Path(__file__).parent.parent / "migrations").glob("**/*.sql"))
    
    has_foreign_keys = False
    for migration_file in migration_files:
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'FOREIGN KEY' in content:
            has_foreign_keys = True
            break
    
    if has_foreign_keys:
        print("  ✅ 定义了外键约束")
    else:
        issues.append("未定义外键约束")
    
    # 检查索引
    has_indexes = False
    for migration_file in migration_files:
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'CREATE INDEX' in content or 'idx_' in content:
            has_indexes = True
            break
    
    if has_indexes:
        print("  ✅ 定义了索引")
    else:
        issues.append("未定义索引")
    
    # 检查触发器
    has_triggers = False
    for migration_file in migration_files:
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'CREATE TRIGGER' in content:
            has_triggers = True
            break
    
    if has_triggers:
        print("  ✅ 定义了触发器（如自动更新 updated_at）")
    else:
        print("  ⚠️  未定义触发器")
    
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    
    return issues


def check_data_flow():
    """检查数据流转"""
    print("\n4️⃣ 数据流转检查")
    print("-" * 80)
    
    issues = []
    
    # 检查工具之间的数据流
    tools_dir = Path(__file__).parent.parent / "src" / "tools"
    
    # 检查 homework_db_tool 中的数据流
    homework_tool = tools_dir / "homework_db_tool.py"
    if homework_tool.exists():
        with open(homework_tool, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查作业创建流程
        if 'create_homework' in content:
            print("  ✅ 作业创建流程存在")
        else:
            issues.append("作业创建流程不存在")
        
        # 检查作业提交流程
        if 'submit_homework' in content:
            print("  ✅ 作业提交流程存在")
        else:
            issues.append("作业提交流程不存在")
    
    # 检查成就系统的数据流
    achievement_tool = tools_dir / "achievement_db_tool.py"
    if achievement_tool.exists():
        with open(achievement_tool, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'add_achievement' in content:
            print("  ✅ 成就添加流程存在")
        else:
            issues.append("成就添加流程不存在")
    
    # 检查学生积分系统的数据流
    student_tool = tools_dir / "student_db_tool.py"
    if student_tool.exists():
        with open(student_tool, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'add_student_points' in content:
            print("  ✅ 学生积分添加流程存在")
        else:
            issues.append("学生积分添加流程不存在")
    
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    
    return issues


def check_data_security():
    """检查数据安全性"""
    print("\n5️⃣ 数据安全性检查")
    print("-" * 80)
    
    issues = []
    
    # 检查密码哈希
    auth_utils = Path(__file__).parent.parent / "src" / "auth" / "auth_utils.py"
    if auth_utils.exists():
        with open(auth_utils, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'bcrypt' in content or 'hash_password' in content:
            print("  ✅ 使用密码哈希")
        else:
            issues.append("未使用密码哈希")
        
        if 'JWT' in content or 'jwt' in content:
            print("  ✅ 使用 JWT 认证")
        else:
            issues.append("未使用 JWT 认证")
    else:
        issues.append("auth_utils.py 不存在")
    
    # 检查文件存储路径隔离
    storage_tool = Path(__file__).parent.parent / "src" / "tools" / "file_storage_tool.py"
    if storage_tool.exists():
        with open(storage_tool, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'students/' in content and '{student_id}' in content:
            print("  ✅ 文件存储路径包含 student_id 隔离")
        else:
            issues.append("文件存储路径未正确隔离")
    
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    
    return issues


def run_data_flow_check():
    """执行数据流检查"""
    print("=" * 80)
    print("策略三：数据流检查")
    print("=" * 80)
    print()
    
    model_issues = check_data_model()
    isolation_issues = check_data_isolation()
    consistency_issues = check_data_consistency()
    flow_issues = check_data_flow()
    security_issues = check_data_security()
    
    total_issues = (
        len(model_issues) + len(isolation_issues) + 
        len(consistency_issues) + len(flow_issues) + 
        len(security_issues)
    )
    
    print("\n6️⃣ 统计结果")
    print("-" * 80)
    print(f"数据模型问题: {len(model_issues)}")
    print(f"数据隔离问题: {len(isolation_issues)}")
    print(f"数据一致性问题: {len(consistency_issues)}")
    print(f"数据流转问题: {len(flow_issues)}")
    print(f"数据安全问题: {len(security_issues)}")
    print(f"\n总计问题数: {total_issues}")
    print()
    
    # 评分
    print("7️⃣ 数据流评分")
    print("-" * 80)
    
    scores = {
        "数据模型完整性": max(0, 100 - len(model_issues) * 10),
        "数据隔离": max(0, 100 - len(isolation_issues) * 15),
        "数据一致性": max(0, 100 - len(consistency_issues) * 10),
        "数据流转": max(0, 100 - len(flow_issues) * 10),
        "数据安全": max(0, 100 - len(security_issues) * 15)
    }
    
    for category, score in scores.items():
        status = "✅" if score >= 80 else ("⚠️" if score >= 60 else "❌")
        print(f"  {status} {category}: {score}/100")
    
    avg_score = sum(scores.values()) / len(scores)
    print(f"\n  📊 综合评分: {avg_score:.1f}/100")
    
    if avg_score >= 90:
        overall_status = "优秀"
    elif avg_score >= 80:
        overall_status = "良好"
    elif avg_score >= 70:
        overall_status = "中等"
    elif avg_score >= 60:
        overall_status = "及格"
    else:
        overall_status = "需要改进"
    
    print(f"  📈 整体评级: {overall_status}")
    
    print()
    print("=" * 80)
    
    return {
        "model_issues": model_issues,
        "isolation_issues": isolation_issues,
        "consistency_issues": consistency_issues,
        "flow_issues": flow_issues,
        "security_issues": security_issues,
        "total_issues": total_issues,
        "scores": scores,
        "avg_score": avg_score,
        "overall_status": overall_status
    }


if __name__ == "__main__":
    results = run_data_flow_check()
    
    # 保存结果
    output_file = Path(__file__).parent / "strategy3_data_flow_check.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n检查结果已保存到: {output_file}")
