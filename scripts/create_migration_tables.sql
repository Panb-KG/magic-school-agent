-- ============================================
-- 迁移历史表
-- 用于记录已执行的数据库迁移
-- ============================================

-- 创建迁移历史表
CREATE SCHEMA IF NOT EXISTS db_migrations;

CREATE TABLE IF NOT EXISTS db_migrations.schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_id VARCHAR(255) UNIQUE NOT NULL,
    migration_name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    checksum VARCHAR(64),  -- SHA256 checksum of the migration script
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_time_ms INTEGER,  -- Execution time in milliseconds
    status VARCHAR(20) DEFAULT 'success' CHECK (status IN ('success', 'failed', 'rolled_back')),
    rollback_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_schema_migrations_id ON db_migrations.schema_migrations(migration_id);
CREATE INDEX IF NOT EXISTS idx_schema_migrations_version ON db_migrations.schema_migrations(version);
CREATE INDEX IF NOT EXISTS idx_schema_migrations_status ON db_migrations.schema_migrations(status);
CREATE INDEX IF NOT EXISTS idx_schema_migrations_executed_at ON db_migrations.schema_migrations(executed_at DESC);

-- 添加注释
COMMENT ON SCHEMA db_migrations IS '数据库迁移管理';
COMMENT ON TABLE db_migrations.schema_migrations IS '迁移历史记录表';
COMMENT ON COLUMN db_migrations.schema_migrations.migration_id IS '迁移唯一标识';
COMMENT ON COLUMN db_migrations.schema_migrations.migration_name IS '迁移名称';
COMMENT ON COLUMN db_migrations.schema_migrations.version IS '迁移版本号';
COMMENT ON COLUMN db_migrations.schema_migrations.description IS '迁移描述';
COMMENT ON COLUMN db_migrations.schema_migrations.checksum IS '迁移脚本校验和（SHA256）';
COMMENT ON COLUMN db_migrations.schema_migrations.executed_at IS '执行时间';
COMMENT ON COLUMN db_migrations.schema_migrations.execution_time_ms IS '执行耗时（毫秒）';
COMMENT ON COLUMN db_migrations.schema_migrations.status IS '执行状态';
COMMENT ON COLUMN db_migrations.schema_migrations.rollback_at IS '回滚时间';
COMMENT ON COLUMN db_migrations.schema_migrations.error_message IS '错误信息';

-- ============================================
-- 创建迁移锁表（防止并发迁移）
-- ============================================

CREATE TABLE IF NOT EXISTS db_migrations.migration_lock (
    id INTEGER PRIMARY KEY DEFAULT 1,
    locked_at TIMESTAMP WITH TIME ZONE,
    locked_by VARCHAR(255),
    lock_reason VARCHAR(255)
);

-- 插入默认锁记录
INSERT INTO db_migrations.migration_lock (id) VALUES (1)
ON CONFLICT (id) DO NOTHING;

COMMENT ON TABLE db_migrations.migration_lock IS '迁移锁表';
COMMENT ON COLUMN db_migrations.migration_lock.locked_at IS '锁定时间';
COMMENT ON COLUMN db_migrations.migration_lock.locked_by IS '锁定者';
COMMENT ON COLUMN db_migrations.migration_lock.lock_reason IS '锁定原因';
