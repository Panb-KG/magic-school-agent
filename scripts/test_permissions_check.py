"""
测试权限检查是否生效
"""
import sys
import os

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_root = os.path.join(project_root, 'src')
sys.path.insert(0, src_root)
sys.path.insert(0, project_root)
print(f"Project root: {project_root}")
print(f"Src root: {src_root}")
print(f"Python path: {sys.path[:3]}")  # 打印前3个路径

from langchain.tools import ToolRuntime
from tools.file_storage_tool import list_student_files
from tools.student_db_tool import get_student_info


def test_without_permission():
    """测试没有权限时是否能访问"""
    print("测试1: 没有权限时尝试访问学生数据")
    print("-" * 50)
    
    # 创建一个没有权限的上下文
    from coze_coding_utils.runtime_ctx.context import Context
    
    ctx = Context(
        method="test",
        headers={},
        configurable={
            "user_id": "999",  # 不存在的用户
            "user_role": "student"
        }
    )
    
    runtime = ToolRuntime(context=ctx)
    
    # 尝试访问 student_id=1 的数据
    result = get_student_info(student_id=1, runtime=runtime)
    print(f"结果: {result}")
    print()
    
    # 尝试列出文件
    result = list_student_files(student_id=1, file_type="homework", runtime=runtime)
    print(f"结果: {result}")
    print()


def test_with_valid_permission():
    """测试有权限时是否能正常访问"""
    print("测试2: 有权限时访问学生数据")
    print("-" * 50)
    
    # 首先检查数据库中是否存在测试数据
    from storage.database.db import get_session
    from storage.database.student_manager import StudentManager
    from coze_coding_utils.runtime_ctx.context import Context
    
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, 1)
        
        if not student:
            print("警告: 数据库中没有 student_id=1 的数据，请先创建测试数据")
            print("跳过此测试")
            return
        
        # 创建一个有权限的上下文
        ctx = Context(
            method="test",
            headers={},
            configurable={
                "user_id": str(student.user_id),  # 使用该学生的 user_id
                "user_role": "student"
            }
        )
        
        runtime = ToolRuntime(context=ctx)
        
        # 尝试访问数据
        result = get_student_info(student_id=1, runtime=runtime)
        print(f"结果: {result}")
        print()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("权限检查测试")
    print("=" * 50)
    print()
    
    test_without_permission()
    test_with_valid_permission()
    
    print("=" * 50)
    print("测试完成")
    print("=" * 50)
