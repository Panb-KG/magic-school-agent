#!/usr/bin/env python3
"""
数据迁移脚本：将 students 关联到 auth.users
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


def check_prerequisites(engine):
    """检查前置条件"""
    logger.info("检查前置条件...")
    
    # 检查 auth schema 和 users 表
    with engine.connect() as conn:
        # 检查 auth schema
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.schemata
                WHERE schema_name = 'auth'
            );
        """))
        if not result.scalar():
            logger.error("❌ auth schema 不存在！请先运行 python scripts/init_database.py")
            return False
        
        # 检查 auth.users 表
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'auth' AND table_name = 'users'
            );
        """))
        if not result.scalar():
            logger.error("❌ auth.users 表不存在！请先运行 python scripts/init_database.py")
            return False
        
        # 检查 students 表
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'students'
            );
        """))
        if not result.scalar():
            logger.error("❌ students 表不存在！请先运行 python scripts/init_business_tables.py")
            return False
        
        # 检查 user_id 字段
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'students' AND column_name = 'user_id'
            );
        """))
        if not result.scalar():
            logger.error("❌ students.user_id 字段不存在！请先运行 scripts/fix_student_table_structure.sql")
            return False
    
    logger.info("✅ 前置条件检查通过")
    return True


def get_migration_stats(engine):
    """获取迁移前统计信息"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                COUNT(*) AS total_count,
                COUNT(CASE WHEN user_id IS NOT NULL THEN 1 END) AS linked_count
            FROM students;
        """))
        row = result.fetchone()
        return {
            'total': row[0],
            'linked': row[1],
            'unlinked': row[0] - row[1]
        }


def perform_migration(engine):
    """执行数据迁移"""
    logger.info("\n开始数据迁移...")
    
    # 读取迁移脚本
    script_path = os.path.join(os.path.dirname(__file__), 'migrate_students_to_users.sql')
    if not os.path.exists(script_path):
        logger.error(f"❌ 迁移脚本不存在: {script_path}")
        return False
    
    sql_script = read_sql_file(script_path)
    
    try:
        with engine.connect() as conn:
            conn.execute(text(sql_script))
            conn.commit()
        
        logger.info("✅ 数据迁移成功")
        return True
    except Exception as e:
        logger.error(f"❌ 数据迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_migration(engine):
    """验证迁移结果"""
    logger.info("\n验证迁移结果...")
    
    with engine.connect() as conn:
        # 获取迁移后统计
        result = conn.execute(text("""
            SELECT
                COUNT(*) AS total_count,
                COUNT(CASE WHEN user_id IS NOT NULL THEN 1 END) AS linked_count
            FROM students;
        """))
        row = result.fetchone()
        total, linked = row[0], row[1]
        unlinked = total - linked
        
        logger.info(f"总学生数: {total}")
        logger.info(f"已关联数: {linked}")
        logger.info(f"未关联数: {unlinked}")
        
        if unlinked == 0:
            logger.info("✅ 所有学生已成功关联！")
            
            # 显示关联的用户信息
            result = conn.execute(text("""
                SELECT
                    s.id AS student_id,
                    s.name AS student_name,
                    s.user_id,
                    u.username,
                    u.role
                FROM students s
                JOIN auth.users u ON s.user_id = u.user_id
                ORDER BY s.id
                LIMIT 10;
            """))
            
            logger.info("\n关联的学生用户（前10个）:")
            for row in result.fetchall():
                student_id, student_name, user_id, username, role = row
                logger.info(f"  学生ID: {student_id:3} | 姓名: {student_name:15} | user_id: {user_id:20} | 用户名: {username:20} | 角色: {role}")
            
            return True
        else:
            logger.warning(f"⚠️  仍有 {unlinked} 个学生未关联")
            return False


def main():
    """主函数"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("Students 表数据关联迁移")
    logger.info("=" * 70)
    logger.info("此脚本将把未关联的 students 数据关联到 auth.users")
    logger.info("")
    
    # 获取数据库引擎
    try:
        engine = get_engine()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False
    
    # 检查前置条件
    if not check_prerequisites(engine):
        return False
    
    # 获取迁移前统计
    logger.info("\n迁移前统计:")
    before_stats = get_migration_stats(engine)
    logger.info(f"  总学生数: {before_stats['total']}")
    logger.info(f"  已关联数: {before_stats['linked']}")
    logger.info(f"  未关联数: {before_stats['unlinked']}")
    
    if before_stats['unlinked'] == 0:
        logger.info("\n✅ 没有需要迁移的数据，所有学生已关联！")
        return True
    
    # 执行迁移
    if not perform_migration(engine):
        return False
    
    # 验证迁移结果
    if not verify_migration(engine):
        return False
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ 数据迁移完成！")
    logger.info("=" * 70)
    logger.info("")
    logger.info("后续步骤:")
    logger.info("  1. 运行 python scripts/check_students_table.py 验证表结构")
    logger.info("  2. 测试用户登录和数据访问权限")
    logger.info("  3. 确认数据隔离正常工作")
    logger.info("")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
