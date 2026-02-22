#!/usr/bin/env python3
"""
完整数据库初始化脚本
执行顺序：
1. 初始化多用户架构（auth schema）
2. 初始化业务表（students, courses, homeworks等）
3. 验证所有表创建成功
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database.db import get_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_sql_file(file_path: str) -> str:
    """读取 SQL 文件内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def execute_sql_script(engine, sql_script: str, script_name: str):
    """执行 SQL 脚本"""
    try:
        logger.info(f"执行 {script_name}...")
        with engine.connect() as conn:
            conn.execute(text(sql_script))
            conn.commit()
        logger.info(f"✅ {script_name} 执行成功")
        return True
    except Exception as e:
        logger.error(f"❌ {script_name} 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_all_tables(engine):
    """验证所有表是否创建成功"""
    multiuser_tables = ['users', 'parent_student_mapping', 'permissions', 'user_sessions']
    memory_tables = ['user_profile', 'conversation_summary', 'knowledge_mastery', 'behavior_preferences', 'important_conversations']
    business_tables = ['students', 'courses', 'homeworks', 'coursewares', 'exercises', 'achievements']
    
    all_tables = {
        'auth': multiuser_tables,
        'memory': memory_tables,
        'public': business_tables
    }
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE schemaname IN ('public', 'auth', 'memory')
                ORDER BY schemaname, tablename;
            """))
            existing = {}
            for row in result.fetchall():
                schema, table = row[0], row[1]
                if schema not in existing:
                    existing[schema] = []
                existing[schema].append(table)
        
        all_success = True
        for schema, expected_tables in all_tables.items():
            logger.info(f"\n验证 {schema} schema 的表:")
            if schema in existing:
                missing = [t for t in expected_tables if t not in existing[schema]]
                if missing:
                    logger.warning(f"  ❌ 缺少的表: {', '.join(missing)}")
                    all_success = False
                else:
                    for table in expected_tables:
                        if table in existing[schema]:
                            logger.info(f"  ✓ {table}")
            else:
                logger.warning(f"  ❌ {schema} schema 不存在")
                all_success = False
        
        return all_success
    except Exception as e:
        logger.error(f"验证表失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("魔法课桌 - 完整数据库初始化")
    logger.info("=" * 70)
    logger.info("")

    # 获取数据库引擎
    try:
        engine = get_engine()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False

    scripts = [
        ('init_multiuser_schema.sql', '多用户架构表'),
        ('init_business_tables.sql', '业务表')
    ]

    success = True
    for script_file, script_name in scripts:
        script_path = os.path.join(os.path.dirname(__file__), script_file)
        if not os.path.exists(script_path):
            logger.error(f"❌ SQL 脚本不存在: {script_path}")
            success = False
            continue
        
        sql_script = read_sql_file(script_path)
        if not execute_sql_script(engine, sql_script, script_name):
            success = False

    # 验证所有表
    logger.info("")
    logger.info("🔍 验证所有表创建...")
    if not verify_all_tables(engine):
        logger.error("❌ 表验证失败")
        success = False

    if success:
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ 数据库初始化成功！")
        logger.info("=" * 70)
        logger.info("")
        logger.info("初始化的 schema:")
        logger.info("  🔐 auth    - 用户认证和权限管理")
        logger.info("  🧠 memory  - 长期记忆存储")
        logger.info("  📊 public  - 业务数据（学生、课程、作业等）")
        logger.info("")
        logger.info("创建的主要表:")
        logger.info("  auth.users                 - 用户表")
        logger.info("  auth.parent_student_mapping - 家长-学生关联表")
        logger.info("  auth.permissions            - 权限定义表")
        logger.info("  auth.user_sessions          - 用户会话表")
        logger.info("  memory.user_profile         - 用户画像")
        logger.info("  memory.conversation_summary - 对话摘要")
        logger.info("  memory.knowledge_mastery    - 知识掌握度")
        logger.info("  memory.behavior_preferences - 行为偏好")
        logger.info("  memory.important_conversations - 重要对话")
        logger.info("  students                    - 学生信息表")
        logger.info("  courses                     - 课程表")
        logger.info("  homeworks                   - 作业任务表")
        logger.info("  coursewares                 - 课件表")
        logger.info("  exercises                   - 运动记录表")
        logger.info("  achievements                - 成就表")
        logger.info("")
        logger.info("下一步:")
        logger.info("  运行 'python scripts/init_test_data.py' 初始化测试数据")
        logger.info("")
    else:
        logger.error("")
        logger.error("=" * 70)
        logger.error("❌ 数据库初始化失败，请检查错误信息")
        logger.error("=" * 70)
        logger.error("")

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
