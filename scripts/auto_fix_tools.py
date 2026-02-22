#!/usr/bin/env python3
"""
自动修复工具脚本
用于批量修复工具文件，将 student_name 改为 student_id 并添加权限检查
"""

import os
import re
from pathlib import Path

# 工具文件列表
TOOL_FILES = [
    'src/tools/course_db_tool.py',
    'src/tools/exercise_db_tool.py',
    'src/tools/achievement_db_tool.py',
    'src/tools/courseware_db_tool.py',
    'src/tools/student_db_tool.py',
]

# 需要替换的函数签名
FUNCTION_SIGNATURES = {
    'course_db_tool.py': [
        'add_course',
        'get_weekly_schedule',
    ],
    'exercise_db_tool.py': [
        'add_exercise',
        'get_exercise_list',
        'get_weekly_exercise_stats',
    ],
    'achievement_db_tool.py': [
        'add_achievement',
        'get_achievement_wall',
        'get_all_achievements',
    ],
    'courseware_db_tool.py': [
        'add_courseware',
        'get_courseware_list',
    ],
    'student_db_tool.py': [
        # 这个文件可能需要特殊处理
    ],
}

# 导入语句模板
IMPORT_TEMPLATE = """from tools.tool_utils_fixed import get_user_context, check_student_access, require_student_access, get_student_name_by_id
"""

# 权限检查模板
PERMISSION_CHECK_TEMPLATE = """
    # 权限检查
    error = require_student_access(runtime, student_id)
    if error:
        return error
"""


def backup_file(filepath):
    """备份文件"""
    backup_path = filepath.replace('.py', '_backup.py')
    if not os.path.exists(backup_path):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已备份: {backup_path}")


def add_imports(filepath, content):
    """添加必要的导入语句"""
    if 'from tools.tool_utils_fixed import' in content:
        return content
    
    # 在第一个导入语句后添加
    lines = content.split('\n')
    new_lines = []
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        if not added and line.startswith('from') and 'import' in line and 'ToolRuntime' in line:
            new_lines.append(IMPORT_TEMPLATE.strip())
            added = True
    
    return '\n'.join(new_lines)


def modify_function_signature(content, function_name):
    """修改函数签名，将 student_name 改为 student_id"""
    # 匹配函数定义
    pattern = rf'def {function_name}\(\s*student_name:\s*str'
    
    if re.search(pattern, content):
        # 替换函数签名
        content = re.sub(
            pattern,
            f'def {function_name}(\n        student_id: int',
            content
        )
        print(f"  ✅ 修改函数签名: {function_name}")
    
    return content


def add_permission_check(content, function_name):
    """添加权限检查"""
    # 查找函数定义后的第一个可执行语句
    pattern = rf'(def {function_name}\([^)]+\)[^:]*:.*?""")'
    
    def replacement(match):
        func_def = match.group(0)
        # 在函数定义后添加权限检查
        return func_def + '\n' + PERMISSION_CHECK_TEMPLATE
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    return content


def modify_student_name_usage(content):
    """修改 student_name 的使用"""
    # 将 student_name 改为 student_id（在查询时）
    content = re.sub(
        r'student_mgr\.get_student_by_name\(db, student_name\)',
        'student_mgr.get_student_by_id(db, student_id)',
        content
    )
    
    # 将参数 student_name 改为 student_id
    content = re.sub(
        r'student_name,\s*runtime',
        'student_id, runtime',
        content
    )
    
    # 将显示的 student_name 改为从 student 对象获取
    content = re.sub(
        r'f"未找到姓名为\{student_name\}的学生"',
        'f"未找到ID为{student_id}的学生"',
        content
    )
    
    # 添加获取学生姓名的逻辑
    content = re.sub(
        r'student_name = student_name',
        'student_name = student.name or "学生"',
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
    content = add_imports(filepath, content)
    
    # 获取文件名
    filename = os.path.basename(filepath)
    
    # 修改函数签名
    if filename in FUNCTION_SIGNATURES:
        for func_name in FUNCTION_SIGNATURES[filename]:
            content = modify_function_signature(content, func_name)
            # content = add_permission_check(content, func_name)
    
    # 修改 student_name 的使用
    content = modify_student_name_usage(content)
    
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
    print("🚀 开始自动修复工具文件")
    print("=" * 60)
    
    for tool_file in TOOL_FILES:
        filepath = os.path.join(os.getcwd(), tool_file)
        if os.path.exists(filepath):
            fix_tool_file(filepath)
        else:
            print(f"⚠️  文件不存在: {tool_file}")
    
    print("\n" + "=" * 60)
    print("✨ 修复完成！")
    print("=" * 60)
    print("\n⚠️  请检查修复后的文件，确认：")
    print("  1. 函数签名是否正确")
    print("  2. 权限检查是否添加")
    print("  3. student_name 的使用是否正确替换")
    print("\n💡 手动测试修复后的文件功能是否正常")
    print("=" * 60)


if __name__ == "__main__":
    main()
