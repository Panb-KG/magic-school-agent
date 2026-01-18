-- ============================================
-- 魔法学校学习管理系统 - 多用户架构初始化脚本
-- 包含：用户认证、角色权限、家长关联、长期记忆
-- ============================================

-- 1. 创建认证相关的 schema
CREATE SCHEMA IF NOT EXISTS auth;

-- 2. 用户表
CREATE TABLE IF NOT EXISTS auth.users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'parent')),
    student_name VARCHAR(50),
    grade VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. 家长-学生关联表
CREATE TABLE IF NOT EXISTS auth.parent_student_mapping (
    mapping_id SERIAL PRIMARY KEY,
    parent_id VARCHAR(50) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    relationship VARCHAR(20) NOT NULL CHECK (relationship IN ('father', 'mother', 'guardian', 'other')),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (parent_id) REFERENCES auth.users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES auth.users(user_id) ON DELETE CASCADE,
    UNIQUE(parent_id, student_id)
);

-- 4. 权限定义表
CREATE TABLE IF NOT EXISTS auth.permissions (
    permission_id VARCHAR(50) PRIMARY KEY,
    permission_name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50)  -- 'basic', 'homework', 'course', 'monitoring', 'reward'
);

-- 5. 角色权限关联表
CREATE TABLE IF NOT EXISTS auth.role_permissions (
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'parent')),
    permission_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (role, permission_id),
    FOREIGN KEY (permission_id) REFERENCES auth.permissions(permission_id)
);

-- 6. 用户会话表
CREATE TABLE IF NOT EXISTS auth.user_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    thread_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE
);

-- ============================================
-- 创建长期记忆相关的 schema
-- ============================================
CREATE SCHEMA IF NOT EXISTS memory;

-- 7. 用户画像表
CREATE TABLE IF NOT EXISTS memory.user_profile (
    profile_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    preferences JSONB DEFAULT '{}',
    learning_goals TEXT,
    learning_style VARCHAR(50),
    favorite_subjects TEXT[],
    weak_subjects TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

-- 8. 对话摘要表
CREATE TABLE IF NOT EXISTS memory.conversation_summary (
    summary_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    thread_id VARCHAR(50) NOT NULL,
    topic VARCHAR(200),
    summary_text TEXT NOT NULL,
    key_points JSONB DEFAULT '[]',
    emotion VARCHAR(50),
    importance_score INTEGER DEFAULT 0 CHECK (importance_score >= 0 AND importance_score <= 10),
    conversation_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE
);

-- 9. 知识掌握度表
CREATE TABLE IF NOT EXISTS memory.knowledge_mastery (
    mastery_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    mastery_level INTEGER DEFAULT 0 CHECK (mastery_level >= 0 AND mastery_level <= 100),
    last_reviewed_at TIMESTAMP,
    practice_count INTEGER DEFAULT 0,
    correct_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, subject, topic)
);

-- 10. 行为偏好表
CREATE TABLE IF NOT EXISTS memory.behavior_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    chat_style VARCHAR(50),  -- 'concise', 'detailed', 'story'
    preferred_response_length VARCHAR(50),
    question_types TEXT[],  -- 常问的问题类型
    feedback_records JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

-- 11. 重要对话表（用于长期保存关键对话）
CREATE TABLE IF NOT EXISTS memory.important_conversations (
    conversation_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    thread_id VARCHAR(50) NOT NULL,
    conversation_type VARCHAR(50),  -- 'breakthrough', 'problem_solved', 'milestone'
    conversation_content TEXT NOT NULL,
    summary TEXT,
    tags TEXT[],
    saved_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE
);

-- ============================================
-- 初始化权限数据
-- ============================================
INSERT INTO auth.permissions (permission_id, permission_name, description, category) VALUES
('view_own_data', '查看自己的数据', '用户可以查看自己的数据', 'basic'),
('view_student_data', '查看关联学生的数据', '家长可以查看孩子的数据', 'basic'),
('edit_own_homework', '提交自己的作业', '学生可以提交作业', 'homework'),
('edit_student_homework', '修改学生的作业', '家长可以修改作业', 'homework'),
('edit_course', '编辑课程信息', '家长可以修改课程', 'course'),
('edit_homework', '编辑作业信息', '家长可以修改作业', 'homework'),
('view_chat_history', '查看对话历史', '家长可以查看孩子与AI的对话', 'monitoring'),
('view_dashboard', '查看学习仪表盘', '查看学习统计', 'monitoring'),
('approve_homework', '批准作业', '家长可以审核作业', 'homework'),
('add_points', '添加魔法积分', '家长可以奖励积分', 'reward'),
('manage_achievements', '管理成就', '家长可以管理成就', 'reward'),
('create_student', '创建学生账号', '家长可以为学生创建账号', 'basic')
ON CONFLICT (permission_id) DO NOTHING;

-- 学生权限
INSERT INTO auth.role_permissions (role, permission_id) VALUES
('student', 'view_own_data'),
('student', 'edit_own_homework'),
('student', 'view_dashboard')
ON CONFLICT (role, permission_id) DO NOTHING;

-- 家长权限
INSERT INTO auth.role_permissions (role, permission_id) VALUES
('parent', 'view_own_data'),
('parent', 'view_student_data'),
('parent', 'edit_student_homework'),
('parent', 'edit_course'),
('parent', 'edit_homework'),
('parent', 'view_chat_history'),
('parent', 'view_dashboard'),
('parent', 'approve_homework'),
('parent', 'add_points'),
('parent', 'manage_achievements'),
('parent', 'create_student')
ON CONFLICT (role, permission_id) DO NOTHING;

-- ============================================
-- 创建索引以提升查询性能
-- ============================================
-- auth schema 索引
CREATE INDEX IF NOT EXISTS idx_users_username ON auth.users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON auth.users(role);
CREATE INDEX IF NOT EXISTS idx_parent_student_parent ON auth.parent_student_mapping(parent_id);
CREATE INDEX IF NOT EXISTS idx_parent_student_student ON auth.parent_student_mapping(student_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON auth.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_thread ON auth.user_sessions(thread_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON auth.user_sessions(is_active, last_active_at);

-- memory schema 索引
CREATE INDEX IF NOT EXISTS idx_conv_summary_user ON memory.conversation_summary(user_id, conversation_date DESC);
CREATE INDEX IF NOT EXISTS idx_conv_summary_topic ON memory.conversation_summary(topic);
CREATE INDEX IF NOT EXISTS idx_knowledge_mastery_user ON memory.knowledge_mastery(user_id, subject);
CREATE INDEX IF NOT EXISTS idx_important_conv_user ON memory.important_conversations(user_id, saved_at DESC);
CREATE INDEX IF NOT EXISTS idx_behavior_pref_user ON memory.behavior_preferences(user_id);

-- ============================================
-- 创建触发器：自动更新 updated_at 字段
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profile_updated_at BEFORE UPDATE ON memory.user_profile
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_mastery_updated_at BEFORE UPDATE ON memory.knowledge_mastery
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_behavior_preferences_updated_at BEFORE UPDATE ON memory.behavior_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 创建视图：家长关联学生信息视图
-- ============================================
CREATE OR REPLACE VIEW auth.parent_students_view AS
SELECT
    p.parent_id,
    p.student_id,
    u.student_name,
    u.username,
    u.grade,
    p.relationship,
    p.created_at AS linked_at
FROM auth.parent_student_mapping p
JOIN auth.users u ON p.student_id = u.user_id
WHERE u.role = 'student';

-- ============================================
-- 创建视图：用户综合信息视图
-- ============================================
CREATE OR REPLACE VIEW auth.user_comprehensive_view AS
SELECT
    u.user_id,
    u.username,
    u.role,
    u.student_name,
    u.grade,
    u.created_at,
    CASE
        WHEN u.role = 'student' THEN (
            SELECT COUNT(*) FROM auth.parent_student_mapping WHERE student_id = u.user_id
        )
        WHEN u.role = 'parent' THEN (
            SELECT COUNT(*) FROM auth.parent_student_mapping WHERE parent_id = u.user_id
        )
        ELSE 0
    END AS related_count
FROM auth.users u;

COMMENT ON SCHEMA auth IS '用户认证和权限管理';
COMMENT ON SCHEMA memory IS '长期记忆存储';

-- 完成
SELECT 'Multi-user schema initialization completed!' AS status;
