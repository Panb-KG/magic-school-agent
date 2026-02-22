#!/usr/bin/env python3
"""
业务表初始化脚本
执行顺序：
1. 执行 init_business_tables.sql 创建业务表
2. 验证表创建成功
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


def execute_sql_script(engine, sql_script: str):
    """执行 SQL 脚本"""
    try:
        with engine.connect() as conn:
            # 直接执行整个脚本，PostgreSQL 能正确处理 $$ 符号
            conn.execute(text(sql_script))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"执行 SQL 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_tables(engine):
    """验证业务表是否创建成功"""
    expected_tables = ['students', 'courses', 'homeworks', 'coursewares', 'exercises', 'achievements']
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename;
            """))
            existing_tables = [row[0] for row in result.fetchall()]
            
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if missing_tables:
            logger.warning(f"缺少的表: {', '.join(missing_tables)}")
            return False
        
        logger.info("✅ 所有业务表创建成功")
        for table in existing_tables:
            if table in expected_tables:
                logger.info(f"  ✓ {table}")
        return True
    except Exception as e:
        logger.error(f"验证表失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始初始化业务数据库表...")
    logger.info("=" * 60)

    # 获取数据库引擎
    try:
        engine = get_engine()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False

    # 读取业务表 SQL 初始化脚本
    script_path = os.path.join(os.path.dirname(__file__), 'init_business_tables.sql')
    if not os.path.exists(script_path):
        logger.error(f"❌ SQL 脚本不存在: {script_path}")
        return False

    logger.info(f"📖 读取 SQL 脚本: {script_path}")
    sql_script = read_sql_file(script_path)

    # 执行 SQL 脚本
    logger.info("🚀 执行业务表创建脚本...")
    if not execute_sql_script(engine, sql_script):
        logger.error("❌ 业务表创建失败")
        return False

    # 验证表创建
    logger.info("🔍 验证表创建...")
    if not verify_tables(engine):
        logger.error("❌ 表验证失败")
        return False

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ 业务表初始化成功！")
    logger.info("=" * 60)
    logger.info("")
    logger.info("创建的业务表:")
    logger.info("  📚 students      - 学生信息表")
    logger.info("  📖 courses       - 课程表")
    logger.info("  📝 homeworks     - 作业任务表")
    logger.info("  📎 coursewares   - 课件表")
    logger.info("  🏃 exercises     - 运动记录表")
    logger.info("  🏆 achievements  - 成就表")
    logger.info("")
    logger.info("创建的功能:")
    logger.info("  ✓ 索引优化 - 为常用查询字段创建索引")
    logger.info("  ✓ 自动更新 - updated_at 字段自动更新")
    logger.info("  ✓ 数据完整性 - 外键约束和检查约束")
    logger.info("  ✓ 级联删除 - 删除学生时自动删除关联数据")
    logger.info("")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
