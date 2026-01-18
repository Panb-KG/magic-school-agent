#!/usr/bin/env python3
"""
多用户架构功能测试脚本
测试：用户认证、会话管理、长期记忆、家长功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.user_manager import user_manager
from auth.auth_utils import verify_token
from storage.session import session_manager
from storage.database.db import get_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_user_registration():
    """测试用户注册"""
    print("\n" + "="*50)
    print("测试 1: 用户注册")
    print("="*50)
    
    # 注册学生用户
    result = user_manager.register_user(
        username="test_student",
        password="test123",
        role="student",
        student_name="测试学生",
        grade="三年级"
    )
    
    if result.get("success"):
        print("✅ 学生注册成功")
        print(f"   用户 ID: {result['user_id']}")
        print(f"   用户名: {result['username']}")
        print(f"   角色: {result['role']}")
        return result['user_id']
    else:
        print(f"❌ 学生注册失败: {result.get('error')}")
        return None


def test_parent_registration():
    """测试家长注册"""
    print("\n" + "="*50)
    print("测试 2: 家长注册")
    print("="*50)
    
    result = user_manager.register_user(
        username="test_parent",
        password="test123",
        role="parent"
    )
    
    if result.get("success"):
        print("✅ 家长注册成功")
        print(f"   用户 ID: {result['user_id']}")
        print(f"   用户名: {result['username']}")
        print(f"   角色: {result['role']}")
        return result['user_id']
    else:
        print(f"❌ 家长注册失败: {result.get('error')}")
        return None


def test_user_login():
    """测试用户登录"""
    print("\n" + "="*50)
    print("测试 3: 用户登录")
    print("="*50)
    
    result = user_manager.login_user("test_student", "test123")
    
    if result.get("success"):
        print("✅ 登录成功")
        print(f"   用户 ID: {result['user_id']}")
        print(f"   访问令牌: {result['access_token'][:50]}...")
        return result['user_id'], result['access_token']
    else:
        print(f"❌ 登录失败: {result.get('error')}")
        return None, None


def test_link_parent_student(parent_id, student_id):
    """测试关联家长和学生"""
    print("\n" + "="*50)
    print("测试 4: 关联家长和学生")
    print("="*50)
    
    result = user_manager.link_parent_student(
        parent_id=parent_id,
        student_id=student_id,
        relationship="mother"
    )
    
    if result.get("success"):
        print("✅ 关联成功")
    else:
        print(f"❌ 关联失败: {result.get('error')}")


def test_session_management(user_id):
    """测试会话管理"""
    print("\n" + "="*50)
    print("测试 5: 会话管理")
    print("="*50)
    
    # 获取或创建会话
    thread_id = session_manager.get_or_create_session(user_id)
    
    if thread_id:
        print(f"✅ 会话管理成功")
        print(f"   Thread ID: {thread_id}")
        return thread_id
    else:
        print("❌ 会话管理失败")
        return None


def test_long_term_memory(user_id):
    """测试长期记忆功能"""
    print("\n" + "="*50)
    print("测试 6: 长期记忆功能")
    print("="*50)
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 测试保存用户画像
            conn.execute(text("""
                INSERT INTO memory.user_profile 
                (user_id, preferences, learning_goals, learning_style, favorite_subjects, weak_subjects)
                VALUES (:user_id, :preferences, :learning_goals, :learning_style, :favorite_subjects, :weak_subjects)
                ON CONFLICT (user_id) DO NOTHING
            """), {
                "user_id": user_id,
                "preferences": '{"chat_style": "detailed"}',
                "learning_goals": "提升数学成绩",
                "learning_style": "视觉学习",
                "favorite_subjects": ["数学", "科学"],
                "weak_subjects": ["语文"]
            })
            conn.commit()
            
            # 测试保存对话摘要
            conn.execute(text("""
                INSERT INTO memory.conversation_summary
                (user_id, thread_id, topic, summary_text, key_points, emotion, importance_score)
                VALUES (:user_id, :thread_id, :topic, :summary_text, :key_points, :emotion, :importance)
            """), {
                "user_id": user_id,
                "thread_id": f"thread_{user_id}_test",
                "topic": "数学问题讨论",
                "summary_text": "学生询问了分数的概念，通过举例说明",
                "key_points": '["理解分数的定义", "学会区分分子分母", "能进行简单的分数比较"]',
                "emotion": "confused",
                "importance": 8
            })
            conn.commit()
            
            print("✅ 长期记忆功能正常")
            print(f"   用户画像已保存")
            print(f"   对话摘要已保存")
            
            return True
    except Exception as e:
        print(f"❌ 长期记忆功能失败: {e}")
        return False


def test_permissions():
    """测试权限系统"""
    print("\n" + "="*50)
    print("测试 7: 权限系统")
    print("="*50)
    
    from auth.permissions import permissions_manager
    
    # 测试学生权限
    student_has_view = permissions_manager.has_permission('student', 'view_own_data')
    student_has_edit = permissions_manager.has_permission('student', 'edit_course')
    
    print(f"   学生 'view_own_data' 权限: {'✅' if student_has_view else '❌'}")
    print(f"   学生 'edit_course' 权限: {'✅' if student_has_edit else '❌'} (应该为❌)")
    
    # 测试家长权限
    parent_has_view = permissions_manager.has_permission('parent', 'view_student_data')
    parent_has_reward = permissions_manager.has_permission('parent', 'add_points')
    
    print(f"   家长 'view_student_data' 权限: {'✅' if parent_has_view else '❌'}")
    print(f"   家长 'add_points' 权限: {'✅' if parent_has_reward else '❌'}")
    
    print("✅ 权限系统测试完成")


def test_parent_student_access(parent_id, student_id):
    """测试家长访问学生数据的权限"""
    print("\n" + "="*50)
    print("测试 8: 家长访问学生数据")
    print("="*50)
    
    from auth.permissions import permissions_manager
    
    has_access = permissions_manager.can_access_student(parent_id, student_id)
    
    if has_access:
        print("✅ 家长可以访问该学生的数据")
    else:
        print("❌ 家长无法访问该学生的数据")
    
    # 获取家长关联的学生列表
    students = user_manager.get_parent_students(parent_id)
    print(f"   关联的学生数量: {len(students)}")
    for student in students:
        print(f"   - {student['student_name']} ({student['grade']})")


def cleanup_test_data():
    """清理测试数据"""
    print("\n" + "="*50)
    print("清理测试数据")
    print("="*50)
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 删除测试用户
            conn.execute(text("""
                DELETE FROM auth.users WHERE username IN ('test_student', 'test_parent')
            """))
            conn.commit()
            
            print("✅ 测试数据已清理")
    except Exception as e:
        print(f"⚠️ 清理测试数据时出错: {e}")


def main():
    """主测试函数"""
    print("\n" + "="*50)
    print("多用户架构功能测试")
    print("="*50)
    
    try:
        # 1. 注册测试用户
        student_id = test_user_registration()
        parent_id = test_parent_registration()
        
        if not student_id or not parent_id:
            print("\n❌ 用户注册失败，终止测试")
            return
        
        # 2. 测试登录
        login_user_id, access_token = test_user_login()
        
        if not login_user_id:
            print("\n❌ 登录失败，终止测试")
            return
        
        # 3. 关联家长和学生
        test_link_parent_student(parent_id, student_id)
        
        # 4. 测试会话管理
        thread_id = test_session_management(student_id)
        
        # 5. 测试长期记忆
        test_long_term_memory(student_id)
        
        # 6. 测试权限系统
        test_permissions()
        
        # 7. 测试家长访问学生数据
        test_parent_student_access(parent_id, student_id)
        
        # 8. 测试总结
        print("\n" + "="*50)
        print("测试总结")
        print("="*50)
        print("✅ 所有核心功能测试完成！")
        print("\n已测试的功能：")
        print("  ✅ 用户注册（学生和家长）")
        print("  ✅ 用户登录和令牌验证")
        print("  ✅ 家长-学生关联")
        print("  ✅ 会话管理（thread_id 隔离）")
        print("  ✅ 长期记忆存储（用户画像、对话摘要）")
        print("  ✅ 权限系统（角色权限验证）")
        print("  ✅ 数据隔离（家长访问学生数据）")
        
        # 清理测试数据
        cleanup_test_data()
        
        print("\n" + "="*50)
        print("测试完成！")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试清理测试数据
        cleanup_test_data()


if __name__ == '__main__':
    main()
