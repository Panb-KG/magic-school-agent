#!/bin/bash

# 项目清理脚本
# 用于删除开发过程中产生的中间文件和不需要的文件

PROJECT_ROOT="/workspace/projects"
cd "$PROJECT_ROOT"

echo "========================================="
echo "开始清理项目文件..."
echo "========================================="

# 1. 删除 Python 缓存文件
echo "1. 清理 Python 缓存文件..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type f -name ".coverage" -delete 2>/dev/null
echo "   ✅ Python 缓存文件已清理"

# 2. 删除日志文件
echo "2. 清理日志文件..."
rm -rf logs/*.log 2>/dev/null
rm -rf magic-school-frontend/logs/*.log 2>/dev/null
echo "   ✅ 日志文件已清理"

# 3. 删除测试缓存
echo "3. 清理测试缓存..."
rm -rf .pytest_cache 2>/dev/null
echo "   ✅ 测试缓存已清理"

# 4. 删除测试中间文件
echo "4. 清理测试中间文件..."
rm -f scripts/strategy1_functionality_check.json 2>/dev/null
rm -f scripts/strategy2_technical_check.json 2>/dev/null
rm -f scripts/strategy3_data_flow_check.json 2>/dev/null
echo "   ✅ 测试中间文件已清理"

# 5. 删除临时 SQL 文件（保留重要的）
echo "5. 清理临时 SQL 文件..."
rm -f scripts/create_migration_tables.sql 2>/dev/null
rm -f scripts/fix_student_table_structure.sql 2>/dev/null
rm -f scripts/migrate_students_to_users.sql 2>/dev/null
echo "   ✅ 临时 SQL 文件已清理"

# 6. 删除测试 HTML 文件
echo "6. 清理测试 HTML 文件..."
rm -f assets/test_chat.html 2>/dev/null
echo "   ✅ 测试 HTML 文件已清理"

# 7. 删除临时测试脚本（保留重要的）
echo "7. 清理临时测试脚本..."
rm -f scripts/auto_fix_tools.py 2>/dev/null
rm -f scripts/batch_fix_permissions.py 2>/dev/null
rm -f scripts/check_students_table.py 2>/dev/null
rm -f scripts/fix_students_table.py 2>/dev/null
rm -f scripts/migrate_students_to_users.py 2>/dev/null
rm -f scripts/release_migration_lock.py 2>/dev/null
rm -f scripts/test_migration_system.py 2>/dev/null
rm -f scripts/test_permissions_check.py 2>/dev/null
echo "   ✅ 临时测试脚本已清理"

# 8. 删除旧的检查脚本
echo "8. 清理旧的检查脚本..."
rm -f scripts/check_strategy1_functionality.py 2>/dev/null
rm -f scripts/check_strategy2_technical.py 2>/dev/null
rm -f scripts/check_strategy3_data_flow.py 2>/dev/null
echo "   ✅ 旧的检查脚本已清理"

# 9. 删除 .DS_Store 文件（macOS）
echo "9. 清理系统文件..."
find . -name ".DS_Store" -delete 2>/dev/null
echo "   ✅ 系统文件已清理"

# 10. 删除临时图片
echo "10. 清理临时图片..."
rm -f assets/e37e8f14-4c8d-4963-b98a-f3b72221e003.png 2>/dev/null
echo "    ✅ 临时图片已清理"

echo ""
echo "========================================="
echo "清理完成！"
echo "========================================="
echo ""
echo "已删除："
echo "  - Python 缓存文件 (__pycache__, *.pyc)"
echo "  - 日志文件"
echo "  - 测试缓存"
echo "  - 测试中间文件"
echo "  - 临时 SQL 文件"
echo "  - 测试 HTML 文件"
echo "  - 临时测试脚本"
echo "  - 旧的检查脚本"
echo "  - 系统文件 (.DS_Store)"
echo "  - 临时图片"
echo ""
echo "保留的重要文件："
echo "  - 源代码 (src/)"
echo "  - 测试代码 (tests/)"
echo "  - 配置文件 (config/)"
echo "  - 核心脚本 (scripts/)"
echo "  - 文档 (docs/)"
echo "  - 前端代码 (magic-school-frontend/)"
echo ""
