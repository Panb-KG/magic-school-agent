#!/usr/bin/env python3
"""
一键修复 students 表关联问题
自动检测并修复所有可能的问题
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


def check_all_issues(engine):
    """检查所有可能的问题"""
    issues = []
    
    logger.info("检查 students 表问题...")
    
    with engine.connect() as conn:
        # 1. 检查表是否存在
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'students'
            );
        """))
        if not result.scalar():
            issues.append("students 表不存在")
            return issues
        
        # 2. 检查 user_id 字段
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'students' AND column_name = 'user_id'
            );
        """))
        if not result.scalar():
            issues.append("user_id 字段不存在")
        
        # 3. 检查外键约束
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_student_user'
                AND table_name = 'students'
            );
        """))
        if not result.scalar():
            issues.append("外键约束 fk_student_user 不存在")
        
        # 4. 检查索引
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes
                WHERE indexname = 'idx_students_user_id'
                AND tablename = 'students'
            );
        """))
        if not result.scalar():
            issues.append("索引 idx_students_user_id 不存在")
        
        # 5. 检查未关联的数据
        result = conn.execute(text("""
            SELECT COUNT(*) FROM students WHERE user_id IS NULL;
        """))
        unlinked_count = result.scalar()
        if unlinked_count > 0:
            issues.append(f"有 {unlinked_count} 个学生数据未关联到 users")
        
        # 6. 检查 auth schema
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.schemata
                WHERE schema_name = 'auth'
            );
        """))
        if not result.scalar():
            issues.append("auth schema 不存在")
        else:
            # 检查 auth.users 表
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'auth' AND table_name = 'users'
                );
            """))
            if not result.scalar():
                issues.append("auth.users 表不存在")
    
    return issues


def fix_table_structure(engine):
    """修复表结构"""
    logger.info("修复表结构...")
    
    script_path = os.path.join(os.path.dirname(__file__), 'fix_student_table_structure.sql')
    if not os.path.exists(script_path):
        logger.error(f"❌ 修复脚本不存在: {script_path}")
        return False
    
    sql_script = read_sql_file(script_path)
    
    try:
        with engine.connect() as conn:
            conn.execute(text(sql_script))
            conn.commit()
        logger.info("✅ 表结构修复成功")
        return True
    except Exception as e:
        logger.error(f"❌ 表结构修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def migrate_data(engine):
    """数据迁移"""
    logger.info("迁移数据...")
    
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


def verify_fix(engine):
    """验证修复结果"""
    logger.info("验证修复结果...")
    
    with engine.connect() as conn:
        # 检查表结构
        result = conn.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM information_schema.columns
                 WHERE table_name = 'students' AND column_name = 'user_id') AS has_user_id,
                (SELECT COUNT(*) FROM information_schema.table_constraints
                 WHERE constraint_name = 'fk_student_user'
                 AND table_name = 'students') AS has_fk,
                (SELECT COUNT(*) FROM pg_indexes
                 WHERE indexname = 'idx_students_user_id'
                 AND tablename = 'students') AS has_index;
        """))
        row = result.fetchone()
        has_user_id, has_fk, has_index = row
        
        # 检查数据关联
        result = conn.execute(text("""
            SELECT
                COUNT(*) AS total,
                COUNT(CASE WHEN user_id IS NOT NULL THEN 1 END) AS linked
            FROM students;
        """))
        total, linked = result.fetchone()
        
        logger.info(f"表结构检查:")
        logger.info(f"  user_id 字段: {'✅' if has_user_id else '❌'}")
        logger.info(f"  外键约束: {'✅' if has_fk else '❌'}")
        logger.info(f"  user_id 索引: {'✅' if has_index else '❌'}")
        
        logger.info(f"数据关联检查:")
        logger.info(f"  总学生数: {total}")
        logger.info(f"  已关联数: {linked}")
        logger.info(f"  未关联数: {total - linked}")
        
        if has_user_id and has_fk and has_index and linked == total:
            logger.info("✅ 所有检查通过！")
            return True
        else:
            logger.warning("⚠️  存在未完成的问题")
            return False


def main():
    """主函数"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("Students 表关联问题一键修复")
    logger.info("=" * 70)
    logger.info("")
    
    # 获取数据库引擎
    try:
        engine = get_engine()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False
    
    # 检查问题
    issues = check_all_issues(engine)
    
    if not issues:
        logger.info("✅ 未发现任何问题，students 表状态良好！")
        return True
    
    logger.info(f"发现 {len(issues)} 个问题:")
    for i, issue in enumerate(issues, 1):
        logger.info(f"  {i}. {issue}")
    logger.info("")
    
    # 确认修复
    response = input("是否开始修复？(yes/no): ")
    if response.lower() not in ['yes', 'y']:
        logger.info("修复已取消")
        return False
    
    # 修复表结构
    structure_issues = [i for i in issues if '字段' in i or '约束' in i or '索引' in i]
    if structure_issues:
        logger.info("\n开始修复表结构...")
        if not fix_table_structure(engine):
            logger.error("表结构修复失败，停止")
            return False
    
    # 数据迁移
    if '未关联' in ' '.join(issues):
        logger.info("\n开始数据迁移...")
        if not migrate_data(engine):
            logger.error("数据迁移失败，停止")
            return False
    
    # 验证修复
    logger.info("\n" + "=" * 70)
    logger.info("验证修复结果")
    logger.info("=" * 70)
    
    if verify_fix(engine):
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ 所有问题已修复！")
        logger.info("=" * 70)
        logger.info("")
        logger.info("后续步骤:")
        logger.info("  1. 运行 python scripts/check_students_table.py 进行详细检查")
        logger.info("  2. 测试用户登录和数据访问")
        logger.info("  3. 运行单元测试验证功能")
        logger.info("")
        return True
    else:
        logger.error("\n❌ 修复未完成，请检查错误信息")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
