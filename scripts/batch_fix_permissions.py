#!/usr/bin/env python3
"""
批量权限检查修复脚本
自动为所有工具文件添加权限检查
"""

import os
import re
from pathlib import Path

# 需要修复的工具文件
TOOL_FILES = [
    'src/tools/course_db_tool.py',
    'src/tools/exercise_db_tool.py',
    'src/tools/achievement_db_tool.py',
    'src/tools/courseware_db_tool.py',
    'src/tools/student_db_tool.py',
    'src/tools/file_storage_tool.py',
    'src/tools/dashboard_tool.py',
    'src/tools/visualization_tool.py',
]

# 函数配置：需要修改的函数及其参数
FUNCTION_CONFIG = {
    'course_db_tool.py': {
        'add_course': {'student_param': 'student_name', 'new_param': 'student_id'},
        'get_weekly_schedule': {'student_param': 'student_name', 'new_param': 'student_id'},
    },
    'exercise_db_tool.py': {
        'add_exercise': {'student_param': 'student_name', 'new_param': 'student_id'},
        'get_exercise_list': {'student_param': 'student_name', 'new_param': 'student_id'},
        'get_weekly_exercise_stats': {'student_param': 'student_name', 'new_param': 'student_id'},
    },
    'achievement_db_tool.py': {
        'add_achievement': {'student_param': 'student_name', 'new_param': 'student_id'},
        'get_achievement_wall': {'student_param': 'student_name', 'new_param': 'student_id'},
        'get_all_achievements': {'student_param': 'student_name', 'new_param': 'student_id'},
    },
    'courseware_db_tool.py': {
        'add_courseware': {'student_param': 'student_name', 'new_param': 'student_id'},
        'get_courseware_list': {'student_param': 'student_name', 'new_param': 'student_id'},
    },
    'student_db_tool.py': {
        'get_student_info': {'student_param': 'name', 'new_param': 'student_id'},
    },
    'dashboard_tool.py': {
        'get_student_dashboard': {'student_param': 'name', 'new_param': 'student_id'},
    },
}

# 导入语句
IMPORTS = """from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
"""

# 权限检查装饰器
PERMISSION_DECORATOR = """@require_student_access()"""

# 权限检查代码
PERMISSION_CHECK = """    # 权限检查
    if not check_student_access(runtime, student_id):
        return "错误：无权访问该学生的数据"

"""


def backup_file(filepath):
    """备份文件"""
    backup_path = filepath.replace('.py', '_backup2.py')
    if not os.path.exists(backup_path):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已备份: {backup_path}")


def add_imports(content):
    """添加导入语句"""
    if 'from tools.tool_utils_fixed import' in content:
        return content
    
    # 在第一个导入后添加
    lines = content.split('\n')
    new_lines = []
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        if not added and line.startswith('from langchain.tools import'):
            new_lines.append(IMPORTS.strip())
            added = True
    
    return '\n'.join(new_lines)


def modify_function(content, func_name, config):
    """修改单个函数"""
    old_param = config['student_param']
    new_param = config['new_param']
    
    # 1. 修改函数签名
    pattern = r'(def ' + re.escape(func_name) + r'\([^)]*' + re.escape(old_param) + r':\s*str)'
    replacement = r'def ' + re.escape(func_name) + r'(\n        ' + re.escape(new_param) + r': int'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print(f"  ✅ 修改函数签名: {func_name}({old_param} -> {new_param})")
    
    # 2. 修改函数文档字符串中的参数说明
    doc_pattern = r'(Args:[^}]*' + re.escape(old_param) + r':\s*学生姓名[^}]*)'
    doc_replacement = r'Args:\n        ' + re.escape(new_param) + r': 学生ID'
    
    content = re.sub(doc_pattern, doc_replacement, content, flags=re.DOTALL)
    
    # 3. 添加装饰器（如果没有）
    decorator_pattern = r'(@require_student_access\(\)\s*\n)?\s*(def ' + re.escape(func_name) + r'\([^)]+\))'
    if '@require_student_access()' not in content:
        content = re.sub(
            r'(def ' + re.escape(func_name) + r'\([^)]+\))',
            PERMISSION_DECORATOR + '\n\g<0>',
            content
        )
        print(f"  ✅ 添加装饰器: {func_name}")
    
    # 4. 添加权限检查代码（如果没有）
    # 查找函数定义后的第一个可执行语句
    func_body_pattern = r'(def ' + re.escape(func_name) + r'\([^)]+\)[^:]*:.*?""")'
    
    def add_permission_check(match):
        func_def = match.group(0)
        # 检查是否已经有权限检查
        if 'check_student_access' in func_def or 'require_student_access' in func_def:
            return func_def
        return func_def + '\n' + PERMISSION_CHECK
    
    content = re.sub(func_body_pattern, add_permission_check, content, flags=re.DOTALL)
    
    # 5. 修改 student_name 的使用
    # 替换 get_student_by_name 为 get_student_by_id
    content = re.sub(
        r'student_mgr\.get_student_by_name\(db, ' + re.escape(old_param) + r'\)',
        r'student_mgr.get_student_by_id(db, ' + re.escape(new_param) + r')',
        content
    )
    
    # 替换错误信息中的参数名
    content = re.sub(
        r'f"未找到姓名为\{' + re.escape(old_param) + r'\}的学生"',
        r'f"未找到ID为\{' + re.escape(new_param) + r'\}的学生"',
        content
    )
    
    # 6. 添加获取学生姓名的逻辑（如果需要）
    content = re.sub(
        r'student_name = ' + re.escape(old_param),
        r'student_name = student.name or "学生"',
        content
    )
    
    # 7. 修改函数调用中的参数
    content = re.sub(
        re.escape(func_name) + r'\(\s*' + re.escape(old_param) + r'\s*,',
        re.escape(func_name) + r'(\n            ' + re.escape(new_param) + ',',
        content
    )
    
    return content


def fix_tool_file(filepath):
    """修复工具文件"""
    print(f"\n🔧 修复文件: {filepath}")
    
    # 备份文件
    backup_file(filepath)
    
    # 读取文件
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 添加导入
    content = add_imports(content)
    
    # 获取文件名和配置
    filename = os.path.basename(filepath)
    config = FUNCTION_CONFIG.get(filename, {})
    
    # 修改函数
    for func_name, func_config in config.items():
        content = modify_function(content, func_name, func_config)
    
    # 如果内容有变化，写入文件
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 文件修复完成: {filepath}")
    else:
        print(f"⚠️  文件无需修改: {filepath}")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始批量修复权限检查")
    print("=" * 60)
    
    fixed_count = 0
    for tool_file in TOOL_FILES:
        filepath = os.path.join(os.getcwd(), tool_file)
        if os.path.exists(filepath):
            fix_tool_file(filepath)
            fixed_count += 1
        else:
            print(f"⚠️  文件不存在: {tool_file}")
    
    print("\n" + "=" * 60)
    print(f"✨ 修复完成！共修复 {fixed_count} 个文件")
    print("=" * 60)
    print("\n⚠️  请检查修复后的文件，确认：")
    print("  1. 函数签名是否正确")
    print("  2. 权限检查是否添加")
    print("  3. 装饰器是否正确")
    print("  4. 参数使用是否正确")
    print("\n💡 手动测试修复后的文件功能是否正常")
    print("=" * 60)


if __name__ == "__main__":
    main()
