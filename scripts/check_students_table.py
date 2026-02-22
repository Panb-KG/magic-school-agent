#!/usr/bin/env python3
"""
检查 students 表关联状态
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


def check_students_table():
    """检查 students 表结构"""
    engine = get_engine()
    
    logger.info("=" * 70)
    logger.info("检查 students 表结构")
    logger.info("=" * 70)
    
    # 1. 检查表是否存在
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'students'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.warning("❌ students 表不存在！")
            return False
        
        logger.info("✅ students 表存在")
    
    # 2. 检查表结构
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'students'
            ORDER BY ordinal_position;
        """))
        
        logger.info("\n表结构:")
        columns = result.fetchall()
        has_user_id = False
        for col in columns:
            column_name, data_type, is_nullable, column_default = col
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default = f" DEFAULT {column_default}" if column_default else ""
            logger.info(f"  {column_name:20} {data_type:15} {nullable:8}{default}")
            if column_name == "user_id":
                has_user_id = True
        
        if has_user_id:
            logger.info("\n✅ user_id 字段存在")
        else:
            logger.warning("\n❌ user_id 字段不存在！")
    
    # 3. 检查外键约束
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = 'students';
        """))
        
        fks = result.fetchall()
        if fks:
            logger.info("\n外键约束:")
            for fk in fks:
                constraint_name, column_name, foreign_table, foreign_column = fk
                logger.info(f"  {constraint_name}: {column_name} -> {foreign_table}.{foreign_column}")
        else:
            logger.warning("\n❌ 没有外键约束！")
    
    # 4. 检查索引
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'students'
            ORDER BY indexname;
        """))
        
        indexes = result.fetchall()
        if indexes:
            logger.info("\n索引:")
            for idx in indexes:
                index_name, index_def = idx
                logger.info(f"  {index_name}")
        else:
            logger.warning("\n⚠️  没有索引")
    
    # 5. 检查数据
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM students;
        """))
        count = result.scalar()
        logger.info(f"\n数据行数: {count}")
        
        if count > 0:
            # 检查有多少行有 user_id
            result = conn.execute(text("""
                SELECT COUNT(*) FROM students WHERE user_id IS NOT NULL;
            """))
            with_user_id = result.scalar()
            logger.info(f"有 user_id 的行数: {with_user_id}")
            logger.info(f"无 user_id 的行数: {count - with_user_id}")
            
            if with_user_id < count:
                logger.warning(f"⚠️  有 {count - with_user_id} 行数据未关联用户！")
    
    # 6. 检查 auth schema 是否存在
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.schemata
                WHERE schema_name = 'auth'
            );
        """))
        auth_exists = result.scalar()
        
        if auth_exists:
            logger.info("\n✅ auth schema 存在")
            
            # 检查 auth.users 表
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'auth' AND table_name = 'users'
                );
            """))
            users_exists = result.scalar()
            
            if users_exists:
                logger.info("✅ auth.users 表存在")
                
                # 检查用户数量
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM auth.users;
                """))
                user_count = result.scalar()
                logger.info(f"用户数量: {user_count}")
            else:
                logger.warning("❌ auth.users 表不存在")
        else:
            logger.warning("\n❌ auth schema 不存在！")
    
    logger.info("\n" + "=" * 70)
    
    return True


if __name__ == '__main__':
    check_students_table()
