-- ============================================
-- 数据迁移脚本：将 students 关联到 auth.users
-- ============================================

-- 说明：
-- 1. 为没有 user_id 的 students 创建对应的 auth.users 记录
-- 2. 将 students.user_id 设置为新创建用户的 user_id
-- 3. 创建 parent_student_mapping 关联（如果需要）
-- ============================================

-- 步骤 1: 为每个没有 user_id 的 student 创建对应的 user 记录
INSERT INTO auth.users (user_id, username, student_name, role, is_active, created_at)
SELECT
    'student_' || s.id::text AS user_id,  -- 生成唯一的 user_id
    'student_' || s.id::text AS username, -- 使用相同的值作为 username
    s.name AS student_name,               -- 学生姓名
    'student' AS role,                    -- 角色为学生
    TRUE AS is_active,                    -- 激活状态
    NOW() AS created_at                   -- 创建时间
FROM students s
WHERE s.user_id IS NULL
ON CONFLICT (user_id) DO NOTHING;

-- 步骤 2: 更新 students 表，将 user_id 设置为新创建的 user_id
UPDATE students s
SET user_id = 'student_' || s.id::text
WHERE s.user_id IS NULL;

-- 步骤 3: 验证更新结果
-- 检查是否还有未关联的 students
DO $$
DECLARE
    unlinked_count INTEGER;
    linked_count INTEGER;
    total_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM students;
    SELECT COUNT(*) INTO linked_count FROM students WHERE user_id IS NOT NULL;
    unlinked_count := total_count - linked_count;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '数据迁移结果';
    RAISE NOTICE '========================================';
    RAISE NOTICE '总学生数: %', total_count;
    RAISE NOTICE '已关联数: %', linked_count;
    RAISE NOTICE '未关联数: %', unlinked_count;
    
    IF unlinked_count = 0 THEN
        RAISE NOTICE '✅ 所有学生已成功关联到 users！';
    ELSE
        RAISE NOTICE '⚠️  仍有 % 个学生未关联', unlinked_count;
    END IF;
    
    RAISE NOTICE '========================================';
END $$;

-- 步骤 4: 显示关联的用户信息
SELECT
    s.id AS student_id,
    s.name AS student_name,
    s.user_id,
    u.username,
    u.role,
    u.created_at AS user_created_at
FROM students s
JOIN auth.users u ON s.user_id = u.user_id
ORDER BY s.id;

-- ============================================
-- 注意事项：
-- 1. 此脚本假设 students.id 是唯一的且可以用来生成 user_id
-- 2. 如果需要不同的 user_id 生成规则，请修改步骤 1 中的逻辑
-- 3. 执行前建议先备份数据库
-- 4. 如果 students 表已有数据但没有对应的 user，此脚本会自动创建
-- ============================================
