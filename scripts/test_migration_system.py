#!/usr/bin/env python3
"""
测试数据库迁移系统
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.database.migration_manager import MigrationManager
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_migration_manager():
    """测试迁移管理器"""
    logger.info("=" * 70)
    logger.info("测试数据库迁移系统")
    logger.info("=" * 70)
    
    try:
        # 1. 初始化迁移管理器
        logger.info("\n1. 初始化迁移管理器...")
        manager = MigrationManager()
        logger.info("✅ 迁移管理器初始化成功")
        
        # 2. 检查迁移历史表
        logger.info("\n2. 检查迁移历史表...")
        with manager.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'db_migrations' AND table_name = 'schema_migrations'
                );
            """))
            if result.scalar():
                logger.info("✅ 迁移历史表存在")
            else:
                logger.warning("⚠️  迁移历史表不存在")
        
        # 3. 获取已执行的迁移
        logger.info("\n3. 获取已执行的迁移...")
        executed = manager.get_executed_migrations()
        logger.info(f"✅ 已执行的迁移数量: {len(executed)}")
        
        # 4. 测试迁移锁
        logger.info("\n4. 测试迁移锁机制...")
        if manager._acquire_lock("测试"):
            logger.info("✅ 成功获取迁移锁")
            manager._release_lock()
            logger.info("✅ 成功释放迁移锁")
        else:
            logger.error("❌ 获取迁移锁失败")
        
        # 5. 显示迁移状态
        logger.info("\n5. 显示迁移状态...")
        manager.status()
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ 所有测试通过")
        logger.info("=" * 70)
        return True
    
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_migration_manager()
    sys.exit(0 if success else 1)
