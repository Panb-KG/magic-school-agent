"""
数据库迁移管理器
提供迁移版本管理、执行、回滚等功能
"""

import os
import sys
import hashlib
import json
import time
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.storage.database.db import get_engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MigrationRecord:
    """迁移记录"""
    id: int
    migration_id: str
    migration_name: str
    version: str
    description: Optional[str]
    checksum: Optional[str]
    executed_at: datetime
    execution_time_ms: Optional[int]
    status: str
    rollback_at: Optional[datetime]
    error_message: Optional[str]


@dataclass
class Migration:
    """迁移定义"""
    migration_id: str
    migration_name: str
    version: str
    description: str
    up_script: str
    down_script: Optional[str]
    dependencies: List[str]  # 依赖的迁移ID列表


class MigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self, migration_dir: str = None):
        """
        初始化迁移管理器
        
        Args:
            migration_dir: 迁移脚本目录
        """
        if migration_dir is None:
            # 默认迁移脚本目录（项目根目录下的 migrations）
            # migration_manager.py 在 src/storage/database/ 目录下
            self.migration_dir = Path(__file__).parent.parent.parent.parent / "migrations"
        else:
            self.migration_dir = Path(migration_dir)
        
        self.engine = get_engine()
        self._ensure_migration_tables()
    
    def _ensure_migration_tables(self):
        """确保迁移历史表存在"""
        with self.engine.connect() as conn:
            # 检查 db_migrations schema 是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.schemata
                    WHERE schema_name = 'db_migrations'
                );
            """))
            
            if not result.scalar():
                logger.info("创建迁移管理表...")
                schema_sql_path = Path(__file__).parent / "create_migration_tables.sql"
                if schema_sql_path.exists():
                    with open(schema_sql_path, 'r', encoding='utf-8') as f:
                        conn.execute(text(f.read()))
                    conn.commit()
                    logger.info("✅ 迁移管理表创建成功")
                else:
                    logger.warning("⚠️  迁移管理表 SQL 脚本不存在，请手动创建")
    
    def _calculate_checksum(self, script: str) -> str:
        """计算脚本的 SHA256 校验和"""
        return hashlib.sha256(script.encode('utf-8')).hexdigest()
    
    def _acquire_lock(self, reason: str = "执行迁移") -> bool:
        """获取迁移锁"""
        try:
            with self.engine.connect() as conn:
                # 使用 advisory lock 确保并发安全
                result = conn.execute(text("SELECT pg_try_advisory_lock(12345);"))
                acquired = result.scalar()
                
                if acquired:
                    # 更新锁表记录
                    conn.execute(text("""
                        UPDATE db_migrations.migration_lock
                        SET locked_at = NOW(), locked_by = CURRENT_USER, lock_reason = :reason
                        WHERE id = 1;
                    """), {"reason": reason})
                    conn.commit()
                    logger.info("✅ 成功获取迁移锁")
                    return True
                else:
                    conn.rollback()
                    logger.error("❌ 无法获取迁移锁（advisory lock），可能已有其他进程在执行迁移")
                    return False
        except Exception as e:
            logger.error(f"获取锁失败: {e}")
            return False
    
    def _release_lock(self):
        """释放迁移锁"""
        try:
            with self.engine.connect() as conn:
                # 更新锁表记录
                conn.execute(text("""
                    UPDATE db_migrations.migration_lock
                    SET locked_at = NULL, locked_by = NULL, lock_reason = NULL
                    WHERE id = 1;
                """))
                
                # 释放 advisory lock
                conn.execute(text("SELECT pg_advisory_unlock(12345);"))
                
                conn.commit()
                logger.info("✅ 迁移锁已释放")
        except Exception as e:
            logger.error(f"释放锁失败: {e}")
    
    def get_executed_migrations(self) -> List[MigrationRecord]:
        """获取已执行的迁移列表"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, migration_id, migration_name, version, description, checksum,
                       executed_at, execution_time_ms, status, rollback_at, error_message
                FROM db_migrations.schema_migrations
                ORDER BY executed_at ASC;
            """))
            
            migrations = []
            for row in result.fetchall():
                migrations.append(MigrationRecord(
                    id=row[0],
                    migration_id=row[1],
                    migration_name=row[2],
                    version=row[3],
                    description=row[4],
                    checksum=row[5],
                    executed_at=row[6],
                    execution_time_ms=row[7],
                    status=row[8],
                    rollback_at=row[9],
                    error_message=row[10]
                ))
            
            return migrations
    
    def get_pending_migrations(self, available_migrations: List[Migration]) -> List[Migration]:
        """获取待执行的迁移"""
        executed_ids = {m.migration_id for m in self.get_executed_migrations()}
        return [m for m in available_migrations if m.migration_id not in executed_ids]
    
    def execute_migration(self, migration: Migration, force: bool = False) -> bool:
        """
        执行单个迁移
        
        Args:
            migration: 迁移对象
            force: 是否强制执行（即使已经执行过）
        
        Returns:
            是否执行成功
        """
        # 检查是否已经执行过
        executed_migrations = self.get_executed_migrations()
        executed_ids = {m.migration_id for m in executed_migrations if m.status == 'success'}
        
        if migration.migration_id in executed_ids and not force:
            logger.warning(f"迁移 {migration.migration_id} 已经执行过，跳过")
            return True
        
        # 检查依赖
        pending_deps = [dep for dep in migration.dependencies if dep not in executed_ids]
        if pending_deps:
            logger.error(f"迁移 {migration.migration_id} 的依赖尚未执行: {pending_deps}")
            return False
        
        logger.info(f"执行迁移: {migration.migration_id} - {migration.migration_name}")
        
        start_time = time.time()
        checksum = self._calculate_checksum(migration.up_script)
        
        try:
            with self.engine.connect() as conn:
                # 使用事务
                trans = conn.begin()
                try:
                    # 执行迁移脚本
                    conn.execute(text(migration.up_script))
                    
                    # 记录迁移历史
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    
                    conn.execute(text("""
                        INSERT INTO db_migrations.schema_migrations
                        (migration_id, migration_name, version, description, checksum, executed_at, execution_time_ms, status)
                        VALUES (:migration_id, :migration_name, :version, :description, :checksum, NOW(), :execution_time_ms, 'success')
                    """), {
                        "migration_id": migration.migration_id,
                        "migration_name": migration.migration_name,
                        "version": migration.version,
                        "description": migration.description,
                        "checksum": checksum,
                        "execution_time_ms": execution_time_ms
                    })
                    
                    trans.commit()
                    logger.info(f"✅ 迁移 {migration.migration_id} 执行成功，耗时 {execution_time_ms}ms")
                    return True
                
                except Exception as e:
                    trans.rollback()
                    # 记录失败
                    conn.execute(text("""
                        INSERT INTO db_migrations.schema_migrations
                        (migration_id, migration_name, version, description, checksum, executed_at, execution_time_ms, status, error_message)
                        VALUES (:migration_id, :migration_name, :version, :description, :checksum, NOW(), :execution_time_ms, 'failed', :error_message)
                    """), {
                        "migration_id": migration.migration_id,
                        "migration_name": migration.migration_name,
                        "version": migration.version,
                        "description": migration.description,
                        "checksum": checksum,
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "error_message": str(e)
                    })
                    conn.commit()
                    raise
        
        except Exception as e:
            logger.error(f"❌ 迁移 {migration.migration_id} 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def rollback_migration(self, migration_id: str) -> bool:
        """
        回滚单个迁移
        
        Args:
            migration_id: 迁移ID
        
        Returns:
            是否回滚成功
        """
        # 查找迁移记录
        executed_migrations = self.get_executed_migrations()
        migration_record = None
        for m in executed_migrations:
            if m.migration_id == migration_id and m.status == 'success':
                migration_record = m
                break
        
        if not migration_record:
            logger.error(f"未找到迁移 {migration_id} 或迁移未成功执行")
            return False
        
        # 检查是否有其他迁移依赖此迁移
        executed_ids = [m.migration_id for m in executed_migrations if m.status == 'success']
        for m in executed_migrations:
            if m.status == 'success' and m.migration_id != migration_id:
                # 这里需要检查迁移依赖关系，暂时跳过
                pass
        
        logger.info(f"回滚迁移: {migration_id}")
        
        # 加载迁移定义
        migration = self._load_migration_by_id(migration_id)
        if not migration or not migration.down_script:
            logger.error(f"迁移 {migration_id} 没有回滚脚本")
            return False
        
        try:
            with self.engine.connect() as conn:
                trans = conn.begin()
                try:
                    # 执行回滚脚本
                    conn.execute(text(migration.down_script))
                    
                    # 更新迁移记录
                    conn.execute(text("""
                        UPDATE db_migrations.schema_migrations
                        SET status = 'rolled_back', rollback_at = NOW()
                        WHERE migration_id = :migration_id
                    """), {"migration_id": migration_id})
                    
                    trans.commit()
                    logger.info(f"✅ 迁移 {migration_id} 回滚成功")
                    return True
                
                except Exception as e:
                    trans.rollback()
                    raise
        
        except Exception as e:
            logger.error(f"❌ 迁移 {migration_id} 回滚失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_migration_by_id(self, migration_id: str) -> Optional[Migration]:
        """根据 ID 加载迁移定义"""
        # 这里需要从文件系统加载迁移定义
        # 暂时返回 None，需要在 load_migrations 方法中实现
        return None
    
    def status(self):
        """显示迁移状态"""
        executed = self.get_executed_migrations()
        
        print("\n" + "=" * 70)
        print("数据库迁移状态")
        print("=" * 70)
        
        if not executed:
            print("还没有执行任何迁移")
        else:
            print(f"已执行的迁移数量: {len(executed)}")
            print("\n迁移历史:")
            print(f"{'ID':<30} {'版本':<10} {'名称':<30} {'状态':<15} {'执行时间'}")
            print("-" * 120)
            
            for m in executed:
                status_icon = "✅" if m.status == 'success' else ("⏪" if m.status == 'rolled_back' else "❌")
                executed_time = m.executed_at.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{m.migration_id:<30} {m.version:<10} {m.migration_name:<30} {status_icon} {m.status:<12} {executed_time}")
        
        print("=" * 70 + "\n")
