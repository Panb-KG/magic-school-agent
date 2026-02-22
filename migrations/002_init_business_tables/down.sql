-- ============================================
-- 回滚: 初始化业务表
-- ID: 002_init_business_tables
-- ============================================

-- 删除业务表
DROP TABLE IF EXISTS achievements CASCADE;
DROP TABLE IF EXISTS exercises CASCADE;
DROP TABLE IF EXISTS coursewares CASCADE;
DROP TABLE IF EXISTS homeworks CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;
