-- ============================================
-- 回滚: 关联 students 表到 auth.users
-- ID: 003_link_students_to_users
-- ============================================

-- 步骤 1: 删除外键约束
ALTER TABLE students DROP CONSTRAINT IF EXISTS fk_student_user;

-- 步骤 2: 删除索引
DROP INDEX IF EXISTS idx_students_user_id;

-- 步骤 3: 可选：删除关联的 user 记录（谨慎操作）
-- 注意：这会删除与 students 关联的用户记录
-- 如果需要保留用户记录，请注释掉以下代码
/*
DELETE FROM auth.users
WHERE user_id IN (
    SELECT user_id FROM students
);
*/

-- 步骤 4: 删除 user_id 字段（可选，谨慎操作）
-- 注意：这会永久删除 students 表的 user_id 数据
-- 如果需要保留字段但只是删除关联，请注释掉以下代码
/*
ALTER TABLE students DROP COLUMN IF EXISTS user_id;
*/
