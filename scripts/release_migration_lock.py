#!/usr/bin/env python3
"""
释放迁移锁
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.database.db import get_engine
from sqlalchemy import text


def main():
    """主函数"""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE db_migrations.migration_lock
            SET locked_at = NULL, locked_by = NULL, lock_reason = NULL
            WHERE id = 1;
        """))
        conn.commit()
    
    print("✅ 迁移锁已释放")


if __name__ == '__main__':
    main()
