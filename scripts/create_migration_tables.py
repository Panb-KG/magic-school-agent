#!/usr/bin/env python3
"""
创建迁移管理表
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.database.db import get_engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("创建迁移管理表...")
    
    # 读取 SQL 脚本
    script_path = os.path.join(os.path.dirname(__file__), 'create_migration_tables.sql')
    if not os.path.exists(script_path):
        logger.error(f"SQL 脚本不存在: {script_path}")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # 执行 SQL
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text(sql_script))
            conn.commit()
        
        logger.info("✅ 迁移管理表创建成功")
        return True
    except Exception as e:
        logger.error(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
