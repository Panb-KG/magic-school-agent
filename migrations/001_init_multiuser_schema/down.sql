-- ============================================
-- 回滚: 初始化多用户架构
-- ID: 001_init_multiuser_schema
-- ============================================

-- 删除记忆相关的表和 schema
DROP TABLE IF EXISTS memory.important_conversations CASCADE;
DROP TABLE IF EXISTS memory.behavior_preferences CASCADE;
DROP TABLE IF EXISTS memory.knowledge_mastery CASCADE;
DROP TABLE IF EXISTS memory.conversation_summary CASCADE;
DROP TABLE IF EXISTS memory.user_profile CASCADE;
DROP SCHEMA IF EXISTS memory CASCADE;

-- 删除认证相关的表和 schema
DROP TABLE IF EXISTS auth.user_sessions CASCADE;
DROP TABLE IF EXISTS auth.role_permissions CASCADE;
DROP TABLE IF EXISTS auth.permissions CASCADE;
DROP TABLE IF EXISTS auth.parent_student_mapping CASCADE;
DROP TABLE IF EXISTS auth.users CASCADE;
DROP SCHEMA IF EXISTS auth CASCADE;
