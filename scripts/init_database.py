#!/usr/bin/env python3
"""
初始化多用户架构数据库表
执行顺序：
1. 创建 schema 和表
2. 初始化权限数据
3. 创建索引和触发器
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


def main():
    """主函数"""
    logger.info("开始初始化多用户架构数据库...")

    # 获取数据库引擎
    try:
        engine = get_engine()
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False

    # 读取 SQL 初始化脚本
    script_path = os.path.join(os.path.dirname(__file__), 'init_multiuser_schema.sql')
    if not os.path.exists(script_path):
        logger.error(f"SQL 脚本不存在: {script_path}")
        return False

    sql_script = read_sql_file(script_path)
    logger.info(f"读取 SQL 脚本: {script_path}")

    # 执行 SQL 脚本
    if execute_sql_script(engine, sql_script):
        logger.info("✅ 数据库初始化成功！")
        logger.info("\n创建的 schema:")
        logger.info("  - auth: 用户认证和权限管理")
        logger.info("  - memory: 长期记忆存储")
        logger.info("\n创建的主要表:")
        logger.info("  - auth.users: 用户表")
        logger.info("  - auth.parent_student_mapping: 家长-学生关联表")
        logger.info("  - auth.permissions: 权限定义表")
        logger.info("  - auth.user_sessions: 用户会话表")
        logger.info("  - memory.user_profile: 用户画像")
        logger.info("  - memory.conversation_summary: 对话摘要")
        logger.info("  - memory.knowledge_mastery: 知识掌握度")
        logger.info("  - memory.behavior_preferences: 行为偏好")
        logger.info("  - memory.important_conversations: 重要对话")
        return True
    else:
        logger.error("❌ 数据库初始化失败")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
