-- ============================================
-- 迁移: 关联 students 表到 auth.users
-- ID: 003_link_students_to_users
-- ============================================

-- 步骤 1: 添加 user_id 字段（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'students' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE students ADD COLUMN user_id VARCHAR(50) UNIQUE;
    END IF;
END $$;

-- 步骤 2: 为没有 user_id 的 students 创建对应的 user 记录
INSERT INTO auth.users (user_id, username, student_name, role, is_active, created_at)
SELECT
    'student_' || s.id::text AS user_id,
    'student_' || s.id::text AS username,
    s.name AS student_name,
    'student' AS role,
    TRUE AS is_active,
    NOW() AS created_at
FROM students s
WHERE s.user_id IS NULL
ON CONFLICT (user_id) DO NOTHING;

-- 步骤 3: 更新 students 表，将 user_id 设置为新创建的 user_id
UPDATE students s
SET user_id = 'student_' || s.id::text
WHERE s.user_id IS NULL;

-- 步骤 4: 添加外键约束
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_student_user'
    ) THEN
        ALTER TABLE students
        ADD CONSTRAINT fk_student_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(user_id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- 步骤 5: 创建索引
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
