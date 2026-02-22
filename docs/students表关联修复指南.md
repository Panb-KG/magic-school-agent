# Students 表关联修复指南

## 问题说明

students 表需要通过 `user_id` 字段关联到 `auth.users` 表，以实现：
1. 多用户数据隔离
2. 权限控制
3. 用户身份管理

## 问题诊断

### 检查当前状态

```bash
# 检查 students 表结构
python scripts/check_students_table.py
```

该脚本会检查：
- ✅ students 表是否存在
- ✅ user_id 字段是否存在
- ✅ 外键约束是否正确
- ✅ 索引是否完整
- ✅ 数据关联状态

### 常见问题

1. **user_id 字段不存在**
   - 原因：表结构未更新
   - 解决：运行 `scripts/fix_student_table_structure.sql`

2. **外键约束缺失**
   - 原因：约束未创建
   - 解决：运行 `scripts/fix_student_table_structure.sql`

3. **数据未关联**
   - 原因：现有数据没有 user_id
   - 解决：运行数据迁移脚本

## 修复流程

### 方法 1：完全重新初始化（推荐用于新环境）

```bash
# 1. 初始化所有表
python scripts/init_all_tables.py

# 2. 初始化测试数据
python scripts/init_test_data.py

# 3. 验证
python scripts/check_students_table.py
```

### 方法 2：修复现有数据库（推荐用于生产环境）

#### 步骤 1：修复表结构

```bash
# 执行表结构修复脚本
psql -d your_database -f scripts/fix_student_table_structure.sql

# 或使用 Python（推荐）
python -c "
from storage.database.db import get_engine
from sqlalchemy import text
import os

engine = get_engine()
with open('scripts/fix_student_table_structure.sql', 'r') as f:
    sql = f.read()
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
print('表结构修复完成')
"
```

#### 步骤 2：数据迁移

```bash
# 执行数据迁移
python scripts/migrate_students_to_users.py
```

该脚本会：
- 为每个没有 user_id 的 student 创建对应的 auth.users 记录
- 将 students.user_id 设置为新创建用户的 user_id
- 验证迁移结果

#### 步骤 3：验证修复

```bash
python scripts/check_students_table.py
```

## 权限检查机制

### 工具层权限检查

所有访问学生数据的工具都应使用 `@require_student_access()` 装饰器：

```python
from tools.tool_utils_fixed import require_student_access, get_student_name_by_id

@require_student_access()
def get_student_info(student_id: int, runtime: ToolRuntime = None) -> str:
    """获取学生信息"""
    student = student_mgr.get_student_by_id(db, student_id)
    student_name = get_student_name_by_id(student_id) or "学生"
    return f"{student_name}的信息..."
```

### 权限检查逻辑

```python
def check_student_access(runtime: ToolRuntime, student_id: int) -> bool:
    user_id, user_role, _, _ = get_user_context(runtime)
    
    # 学生只能访问自己的数据
    if user_role == 'student':
        student = student_mgr.get_student_by_id(db, student_id)
        return student.user_id == user_id
    
    # 家长可以访问关联学生的数据
    elif user_role == 'parent':
        return permissions_manager.can_access_student(user_id, str(student_id))
    
    return False
```

## 数据模型

### Students 表结构

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE,           -- 关联到 auth.users
    name VARCHAR(128) NOT NULL,
    grade VARCHAR(32),
    class_name VARCHAR(64),
    ...
    CONSTRAINT fk_student_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(user_id)
        ON DELETE CASCADE
);
```

### Python 模型

```python
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=True)  # 关联字段
    name = Column(String(128), nullable=False)
    ...
```

## 常见问题排查

### 问题 1：权限检查失败

**症状**: 工具返回 "错误：无权访问该学生的数据"

**排查步骤**:
1. 检查 student_id 是否正确
2. 检查 student.user_id 是否存在
3. 检查当前用户的 user_id
4. 运行 `python scripts/check_students_table.py`

**解决方法**:
```python
# 检查关联
student = student_mgr.get_student_by_id(db, student_id)
print(f"student.user_id: {student.user_id}")
print(f"current user_id: {user_id}")

# 如果未关联，运行迁移
python scripts/migrate_students_to_users.py
```

### 问题 2：外键约束错误

**症状**: "insert or update on table violates foreign key constraint"

**原因**: students.user_id 引用的 user_id 在 auth.users 中不存在

**解决方法**:
```sql
-- 检查孤立的 students
SELECT s.id, s.name, s.user_id
FROM students s
WHERE s.user_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM auth.users u WHERE u.user_id = s.user_id
  );

-- 修复：删除或更新孤立的记录
DELETE FROM students
WHERE user_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM auth.users u WHERE u.user_id = students.user_id
  );
```

### 问题 3：迁移后仍有未关联数据

**原因**:
1. auth.users 表不存在或未初始化
2. students.id 为 NULL 或无效
3. 外键约束阻止更新

**解决方法**:
```bash
# 1. 确保 auth.users 存在
python scripts/init_database.py

# 2. 重新运行迁移
python scripts/migrate_students_to_users.py

# 3. 手动检查和修复
python -c "
from storage.database.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # 查看未关联的学生
    result = conn.execute(text('''
        SELECT id, name, user_id
        FROM students
        WHERE user_id IS NULL
    '''))
    for row in result:
        print(f'ID: {row[0]}, Name: {row[1]}, user_id: {row[2]}')
"
```

## 验证清单

完成修复后，请验证以下项目：

- [ ] students.user_id 字段存在
- [ ] 外键约束 fk_student_user 存在
- [ ] 索引 idx_students_user_id 存在
- [ ] 所有学生数据已关联到 users
- [ ] 权限检查正常工作
- [ ] 学生只能访问自己的数据
- [ ] 家长可以访问关联学生的数据
- [ ] 级联删除正常工作

## 维护建议

### 定期检查

```bash
# 每月检查一次未关联的数据
python scripts/check_students_table.py
```

### 数据一致性检查

```sql
-- 检查数据一致性
SELECT 
    (SELECT COUNT(*) FROM students) AS total_students,
    (SELECT COUNT(*) FROM students WHERE user_id IS NOT NULL) AS linked_students,
    (SELECT COUNT(*) FROM auth.users WHERE role = 'student') AS student_users;
```

### 性能监控

```sql
-- 检查外键约束性能
EXPLAIN ANALYZE
SELECT * FROM students s
JOIN auth.users u ON s.user_id = u.user_id
WHERE s.id = 1;
```

## 相关脚本

| 脚本 | 功能 |
|------|------|
| `scripts/check_students_table.py` | 检查 students 表状态 |
| `scripts/migrate_students_to_users.py` | 数据迁移 |
| `scripts/fix_student_table_structure.sql` | 修复表结构 |
| `scripts/init_database.py` | 初始化多用户架构 |
| `scripts/init_all_tables.py` | 完整初始化 |

## 支持和帮助

如有问题，请查看：
- 错误日志: `/app/work/logs/bypass/app.log`
- 数据库日志: PostgreSQL 日志
- 权限文档: `docs/多用户架构设计.md`
