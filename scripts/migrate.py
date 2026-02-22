#!/usr/bin/env python3
"""
统一的数据库迁移管理入口
支持迁移的执行、回滚、状态查看等功能
"""

import sys
import os
import argparse
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.database.migration_manager import MigrationManager, Migration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_migrations(migration_dir: Path) -> list:
    """
    从迁移目录加载所有迁移
    
    Args:
        migration_dir: 迁移目录路径
    
    Returns:
        迁移列表
    """
    migrations = []
    
    if not migration_dir.exists():
        logger.warning(f"迁移目录不存在: {migration_dir}")
        return migrations
    
    # 查找所有迁移文件
    migration_files = sorted(migration_dir.glob("*.json"))
    
    for migration_file in migration_files:
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 读取 up 和 down 脚本
            up_script_path = migration_file.parent / migration_file.stem / "up.sql"
            down_script_path = migration_file.parent / migration_file.stem / "down.sql"
            
            up_script = ""
            down_script = ""
            
            if up_script_path.exists():
                with open(up_script_path, 'r', encoding='utf-8') as f:
                    up_script = f.read()
            
            if down_script_path.exists():
                with open(down_script_path, 'r', encoding='utf-8') as f:
                    down_script = f.read()
            
            migration = Migration(
                migration_id=data['migration_id'],
                migration_name=data['migration_name'],
                version=data['version'],
                description=data['description'],
                up_script=up_script,
                down_script=down_script,
                dependencies=data.get('dependencies', [])
            )
            
            migrations.append(migration)
            logger.info(f"加载迁移: {migration.migration_id} - {migration.migration_name}")
        
        except Exception as e:
            logger.error(f"加载迁移文件 {migration_file} 失败: {e}")
    
    return migrations


def cmd_status(args):
    """显示迁移状态"""
    manager = MigrationManager()
    manager.status()


def cmd_migrate(args):
    """执行迁移"""
    manager = MigrationManager()
    
    # 获取迁移锁
    if not manager._acquire_lock("执行迁移"):
        logger.error("无法获取迁移锁，可能已有其他进程在执行迁移")
        return False
    
    try:
        # 加载所有可用的迁移
        migration_dir = Path(args.migration_dir) if args.migration_dir else None
        available_migrations = load_migrations(migration_dir or manager.migration_dir)
        
        if not available_migrations:
            logger.warning("没有可用的迁移")
            return True
        
        # 获取待执行的迁移
        pending_migrations = manager.get_pending_migrations(available_migrations)
        
        if not pending_migrations:
            logger.info("所有迁移已执行完毕")
            return True
        
        logger.info(f"发现 {len(pending_migrations)} 个待执行的迁移")
        
        # 执行迁移
        success_count = 0
        for migration in pending_migrations:
            if manager.execute_migration(migration):
                success_count += 1
            else:
                logger.error(f"迁移 {migration.migration_id} 执行失败，停止后续迁移")
                return False
        
        logger.info(f"迁移执行完成: {success_count}/{len(pending_migrations)} 成功")
        return True
    
    finally:
        manager._release_lock()


def cmd_rollback(args):
    """回滚迁移"""
    manager = MigrationManager()
    
    # 获取迁移锁
    if not manager._acquire_lock("回滚迁移"):
        logger.error("无法获取迁移锁，可能已有其他进程在执行迁移")
        return False
    
    try:
        migration_id = args.migration_id
        
        if not migration_id:
            logger.error("请指定要回滚的迁移ID")
            return False
        
        success = manager.rollback_migration(migration_id)
        return success
    
    finally:
        manager._release_lock()


def cmd_init_migration(args):
    """初始化新的迁移"""
    migration_id = args.migration_id
    migration_name = args.migration_name
    version = args.version or "1.0.0"
    description = args.description or ""
    
    if not migration_id or not migration_name:
        logger.error("请提供迁移ID和迁移名称")
        return False
    
    # 创建迁移目录结构
    manager = MigrationManager()
    migration_dir = manager.migration_dir
    migration_dir.mkdir(exist_ok=True)
    
    migration_subdir = migration_dir / migration_id
    migration_subdir.mkdir(exist_ok=True)
    
    # 创建迁移定义文件
    migration_data = {
        "migration_id": migration_id,
        "migration_name": migration_name,
        "version": version,
        "description": description,
        "dependencies": []
    }
    
    json_path = migration_dir / f"{migration_id}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(migration_data, f, indent=2, ensure_ascii=False)
    
    # 创建 up.sql 和 down.sql 模板
    up_sql_path = migration_subdir / "up.sql"
    with open(up_sql_path, 'w', encoding='utf-8') as f:
        f.write(f"-- ============================================\n")
        f.write(f"-- 迁移: {migration_name}\n")
        f.write(f"-- ID: {migration_id}\n")
        f.write(f"-- 版本: {version}\n")
        f.write(f"-- 描述: {description}\n")
        f.write(f"-- ============================================\n\n")
        f.write(f"-- 在这里编写迁移 SQL\n\n")
    
    down_sql_path = migration_subdir / "down.sql"
    with open(down_sql_path, 'w', encoding='utf-8') as f:
        f.write(f"-- ============================================\n")
        f.write(f"-- 回滚: {migration_name}\n")
        f.write(f"-- ID: {migration_id}\n")
        f.write(f"-- ============================================\n\n")
        f.write(f"-- 在这里编写回滚 SQL\n\n")
    
    logger.info(f"✅ 迁移初始化成功")
    logger.info(f"  定义文件: {json_path}")
    logger.info(f"  UP 脚本: {up_sql_path}")
    logger.info(f"  DOWN 脚本: {down_sql_path}")
    logger.info(f"\n下一步:")
    logger.info(f"  1. 编辑 {up_sql_path} 编写迁移 SQL")
    logger.info(f"  2. 编辑 {down_sql_path} 编写回滚 SQL（可选）")
    logger.info(f"  3. 运行: python scripts/migrate.py migrate")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据库迁移管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='显示迁移状态')
    status_parser.set_defaults(func=cmd_status)
    
    # migrate 命令
    migrate_parser = subparsers.add_parser('migrate', help='执行迁移')
    migrate_parser.add_argument('--migration-dir', help='迁移目录路径')
    migrate_parser.set_defaults(func=cmd_migrate)
    
    # rollback 命令
    rollback_parser = subparsers.add_parser('rollback', help='回滚迁移')
    rollback_parser.add_argument('migration_id', help='要回滚的迁移ID')
    rollback_parser.set_defaults(func=cmd_rollback)
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化新迁移')
    init_parser.add_argument('--migration-id', required=True, help='迁移ID（如: 001_init_schema）')
    init_parser.add_argument('--migration-name', required=True, help='迁移名称')
    init_parser.add_argument('--version', help='迁移版本号（默认: 1.0.0）')
    init_parser.add_argument('--description', help='迁移描述')
    init_parser.set_defaults(func=cmd_init_migration)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'init':
        return 0 if cmd_init_migration(args) else 1
    
    # 其他命令需要迁移管理器
    if args.func(args):
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
