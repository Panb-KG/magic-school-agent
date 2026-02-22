-- ============================================
-- 业务表初始化脚本
-- 用于创建业务相关的所有数据表
-- ============================================

-- ============================================
-- 1. 学生信息表
-- ============================================
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE,
    name VARCHAR(128) NOT NULL,
    grade VARCHAR(32),
    class_name VARCHAR(64),
    school VARCHAR(128),
    parent_contact VARCHAR(32),
    nickname VARCHAR(64),
    avatar_url VARCHAR(512),
    is_active BOOLEAN DEFAULT TRUE,
    magic_level INTEGER DEFAULT 1 CHECK (magic_level >= 1 AND magic_level <= 10),
    total_points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_student_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(user_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE students IS '学生信息表';
COMMENT ON COLUMN students.id IS '学生ID';
COMMENT ON COLUMN students.user_id IS '关联的用户ID';
COMMENT ON COLUMN students.name IS '学生姓名';
COMMENT ON COLUMN students.grade IS '年级';
COMMENT ON COLUMN students.class_name IS '班级';
COMMENT ON COLUMN students.school IS '学校名称';
COMMENT ON COLUMN students.parent_contact IS '家长联系方式';
COMMENT ON COLUMN students.nickname IS '昵称';
COMMENT ON COLUMN students.avatar_url IS '头像URL';
COMMENT ON COLUMN students.is_active IS '是否活跃';
COMMENT ON COLUMN students.magic_level IS '魔法等级（1-10）';
COMMENT ON COLUMN students.total_points IS '总积分';

-- ============================================
-- 2. 课程表（学校和课外）
-- ============================================
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_name VARCHAR(128) NOT NULL,
    course_type VARCHAR(32) NOT NULL CHECK (course_type IN ('school', 'extra')),
    weekday VARCHAR(16),
    start_time VARCHAR(16),
    end_time VARCHAR(16),
    location VARCHAR(128),
    teacher VARCHAR(64),
    classroom VARCHAR(64),
    is_recurring BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_course_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE courses IS '课程表';
COMMENT ON COLUMN courses.id IS '课程ID';
COMMENT ON COLUMN courses.student_id IS '学生ID';
COMMENT ON COLUMN courses.course_name IS '课程名称';
COMMENT ON COLUMN courses.course_type IS '课程类型：school/extra';
COMMENT ON COLUMN courses.weekday IS '星期几';
COMMENT ON COLUMN courses.start_time IS '开始时间';
COMMENT ON COLUMN courses.end_time IS '结束时间';
COMMENT ON COLUMN courses.location IS '上课地点';
COMMENT ON COLUMN courses.teacher IS '老师姓名';
COMMENT ON COLUMN courses.classroom IS '教室';
COMMENT ON COLUMN courses.is_recurring IS '是否重复';
COMMENT ON COLUMN courses.notes IS '备注';

-- ============================================
-- 3. 作业任务表
-- ============================================
CREATE TABLE IF NOT EXISTS homeworks (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    title VARCHAR(256) NOT NULL,
    subject VARCHAR(64),
    description TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
    priority VARCHAR(16) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    attachment_url VARCHAR(512),
    submission_url VARCHAR(512),
    points INTEGER DEFAULT 0,
    feedback TEXT,
    category VARCHAR(64),
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_homework_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE homeworks IS '作业任务表';
COMMENT ON COLUMN homeworks.id IS '作业ID';
COMMENT ON COLUMN homeworks.student_id IS '学生ID';
COMMENT ON COLUMN homeworks.title IS '作业标题';
COMMENT ON COLUMN homeworks.subject IS '科目';
COMMENT ON COLUMN homeworks.description IS '作业描述';
COMMENT ON COLUMN homeworks.due_date IS '截止日期';
COMMENT ON COLUMN homeworks.status IS '状态';
COMMENT ON COLUMN homeworks.priority IS '优先级';
COMMENT ON COLUMN homeworks.attachment_url IS '附件URL';
COMMENT ON COLUMN homeworks.submission_url IS '提交文件URL';
COMMENT ON COLUMN homeworks.points IS '获得积分';
COMMENT ON COLUMN homeworks.feedback IS '老师反馈';
COMMENT ON COLUMN homeworks.category IS '分类标签';
COMMENT ON COLUMN homeworks.reminder_sent IS '是否已提醒';

-- ============================================
-- 4. 课件表
-- ============================================
CREATE TABLE IF NOT EXISTS coursewares (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    title VARCHAR(256) NOT NULL,
    subject VARCHAR(64),
    file_type VARCHAR(32) CHECK (file_type IN ('pdf', 'doc', 'ppt', 'image', 'video', 'other')),
    file_url VARCHAR(512) NOT NULL,
    file_size INTEGER,
    category VARCHAR(64),
    description TEXT,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_courseware_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE coursewares IS '课件表';
COMMENT ON COLUMN coursewares.id IS '课件ID';
COMMENT ON COLUMN coursewares.student_id IS '学生ID';
COMMENT ON COLUMN coursewares.title IS '课件标题';
COMMENT ON COLUMN coursewares.subject IS '科目';
COMMENT ON COLUMN coursewares.file_type IS '文件类型';
COMMENT ON COLUMN coursewares.file_url IS '文件URL';
COMMENT ON COLUMN coursewares.file_size IS '文件大小（字节）';
COMMENT ON COLUMN coursewares.category IS '分类标签';
COMMENT ON COLUMN coursewares.description IS '课件描述';
COMMENT ON COLUMN coursewares.download_count IS '下载次数';

-- ============================================
-- 5. 运动记录表
-- ============================================
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    exercise_type VARCHAR(64) NOT NULL CHECK (exercise_type IN ('run', 'swim', 'basketball', 'football', 'skip_rope', 'yoga', 'other')),
    duration INTEGER,
    distance FLOAT,
    calories INTEGER,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_exercise_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE exercises IS '运动记录表';
COMMENT ON COLUMN exercises.id IS '运动记录ID';
COMMENT ON COLUMN exercises.student_id IS '学生ID';
COMMENT ON COLUMN exercises.exercise_type IS '运动类型';
COMMENT ON COLUMN exercises.duration IS '时长（分钟）';
COMMENT ON COLUMN exercises.distance IS '距离（公里）';
COMMENT ON COLUMN exercises.calories IS '消耗卡路里';
COMMENT ON COLUMN exercises.date IS '运动日期';
COMMENT ON COLUMN exercises.notes IS '备注';
COMMENT ON COLUMN exercises.points IS '获得积分';

-- ============================================
-- 6. 成就表
-- ============================================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    achievement_type VARCHAR(64) NOT NULL CHECK (achievement_type IN ('homework_exercise', 'course_complete', 'reading_goal', 'study_effort', 'health_sport', 'creativity', 'persistence', 'other')),
    title VARCHAR(256) NOT NULL,
    description TEXT,
    icon_url VARCHAR(512),
    points INTEGER DEFAULT 0,
    level VARCHAR(32) DEFAULT 'bronze' CHECK (level IN ('bronze', 'silver', 'gold', 'platinum', 'diamond')),
    achieved_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_featured BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_achievement_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE achievements IS '成就表';
COMMENT ON COLUMN achievements.id IS '成就ID';
COMMENT ON COLUMN achievements.student_id IS '学生ID';
COMMENT ON COLUMN achievements.achievement_type IS '成就类型';
COMMENT ON COLUMN achievements.title IS '成就标题';
COMMENT ON COLUMN achievements.description IS '成就描述';
COMMENT ON COLUMN achievements.icon_url IS '图标URL';
COMMENT ON COLUMN achievements.points IS '获得积分';
COMMENT ON COLUMN achievements.level IS '等级';
COMMENT ON COLUMN achievements.achieved_date IS '获得时间';
COMMENT ON COLUMN achievements.is_featured IS '是否展示在成就墙';

-- ============================================
-- 创建索引以提升查询性能
-- ============================================

-- students 表索引
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_students_school ON students(school);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active);

-- courses 表索引
CREATE INDEX IF NOT EXISTS idx_courses_student ON courses(student_id);
CREATE INDEX IF NOT EXISTS idx_courses_type ON courses(course_type);
CREATE INDEX IF NOT EXISTS idx_courses_weekday ON courses(weekday);

-- homeworks 表索引
CREATE INDEX IF NOT EXISTS idx_homeworks_student ON homeworks(student_id);
CREATE INDEX IF NOT EXISTS idx_homeworks_status ON homeworks(status);
CREATE INDEX IF NOT EXISTS idx_homeworks_due_date ON homeworks(due_date);
CREATE INDEX IF NOT EXISTS idx_homeworks_student_status ON homeworks(student_id, status);

-- coursewares 表索引
CREATE INDEX IF NOT EXISTS idx_coursewares_student ON coursewares(student_id);
CREATE INDEX IF NOT EXISTS idx_coursewares_subject ON coursewares(subject);
CREATE INDEX IF NOT EXISTS idx_coursewares_category ON coursewares(category);

-- exercises 表索引
CREATE INDEX IF NOT EXISTS idx_exercises_student ON exercises(student_id);
CREATE INDEX IF NOT EXISTS idx_exercises_date ON exercises(date);
CREATE INDEX IF NOT EXISTS idx_exercises_type ON exercises(exercise_type);

-- achievements 表索引
CREATE INDEX IF NOT EXISTS idx_achievements_student ON achievements(student_id);
CREATE INDEX IF NOT EXISTS idx_achievements_type ON achievements(achievement_type);
CREATE INDEX IF NOT EXISTS idx_achievements_featured ON achievements(is_featured);

-- ============================================
-- 创建触发器：自动更新 updated_at 字段
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有表添加触发器
DROP TRIGGER IF EXISTS update_students_updated_at ON students;
CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_courses_updated_at ON courses;
CREATE TRIGGER update_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_homeworks_updated_at ON homeworks;
CREATE TRIGGER update_homeworks_updated_at
    BEFORE UPDATE ON homeworks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_coursewares_updated_at ON coursewares;
CREATE TRIGGER update_coursewares_updated_at
    BEFORE UPDATE ON coursewares
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_exercises_updated_at ON exercises;
CREATE TRIGGER update_exercises_updated_at
    BEFORE UPDATE ON exercises
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_achievements_updated_at ON achievements;
CREATE TRIGGER update_achievements_updated_at
    BEFORE UPDATE ON achievements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 验证表创建
-- ============================================

SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('students', 'courses', 'homeworks', 'coursewares', 'exercises', 'achievements')
ORDER BY tablename;

RAISE NOTICE '✅ 业务表初始化完成！';
