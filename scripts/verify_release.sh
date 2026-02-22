#!/bin/bash

# 项目发布前验证脚本

PROJECT_ROOT="/workspace/projects"
cd "$PROJECT_ROOT"

echo "========================================="
echo "项目发布前验证"
echo "========================================="
echo ""

# 统计变量
ERRORS=0
WARNINGS=0

# 1. 检查必要文件
echo "1. 检查必要文件..."
REQUIRED_FILES=(
    "README.md"
    "requirements.txt"
    "pytest.ini"
    "config/agent_llm_config.json"
    ".gitignore"
    ".coze"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
        ((ERRORS++))
    fi
done

# 2. 检查必要目录
echo ""
echo "2. 检查必要目录..."
REQUIRED_DIRS=(
    "src"
    "tests"
    "scripts"
    "docs"
    "config"
    "migrations"
    "magic-school-frontend"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir"
    else
        echo "   ❌ $dir (缺失)"
        ((ERRORS++))
    fi
done

# 3. 检查中间文件
echo ""
echo "3. 检查中间文件（应该不存在）..."
TEMP_FILES=(
    "__pycache__"
    "*.pyc"
    "*.pyo"
    "*.log"
    ".coverage"
    ".pytest_cache"
)

for pattern in "${TEMP_FILES[@]}"; do
    count=$(find . -name "$pattern" 2>/dev/null | wc -l)
    if [ $count -eq 0 ]; then
        echo "   ✅ $pattern (不存在)"
    else
        echo "   ⚠️  $pattern (存在 $count 个)"
        ((WARNINGS++))
    fi
done

# 4. 检查核心源代码
echo ""
echo "4. 检查核心源代码..."
CORE_FILES=(
    "src/agents/agent.py"
    "src/auth/user_manager.py"
    "src/storage/database/db.py"
    "src/main.py"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
        ((ERRORS++))
    fi
done

# 5. 检查测试文件
echo ""
echo "5. 检查测试文件..."
TEST_FILES=(
    "tests/conftest.py"
    "tests/test_base.py"
    "pytest.ini"
)

for file in "${TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ⚠️  $file (缺失，测试可能不完整)"
        ((WARNINGS++))
    fi
done

# 6. 检查文档
echo ""
echo "6. 检查关键文档..."
DOCS=(
    "README.md"
    "API_DOCUMENTATION.md"
    "DEPLOYMENT_GUIDE.md"
    "PROJECT_STRUCTURE.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "   ✅ $doc"
    else
        echo "   ⚠️  $doc (缺失，文档不完整)"
        ((WARNINGS++))
    fi
done

# 7. 检查脚本
echo ""
echo "7. 检查关键脚本..."
SCRIPTS=(
    "scripts/start_all_services.sh"
    "scripts/cleanup_project.sh"
    "scripts/init_database.py"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo "   ✅ $script"
        if [ -x "$script" ] && [[ "$script" == *.sh ]]; then
            echo "      (可执行)"
        fi
    else
        echo "   ⚠️  $script (缺失)"
        ((WARNINGS++))
    fi
done

# 8. 统计文件数量
echo ""
echo "8. 统计文件数量..."
PY_COUNT=$(find src/ -name "*.py" 2>/dev/null | wc -l)
TEST_COUNT=$(find tests/ -name "*.py" 2>/dev/null | wc -l)
DOC_COUNT=$(find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l)

echo "   Python文件: $PY_COUNT"
echo "   测试文件: $TEST_COUNT"
echo "   文档文件: $DOC_COUNT"

if [ $PY_COUNT -lt 50 ]; then
    echo "   ⚠️  Python文件数量偏少"
    ((WARNINGS++))
fi

# 9. 检查 .gitignore
echo ""
echo "9. 检查 .gitignore 配置..."
if [ -f ".gitignore" ]; then
    echo "   ✅ .gitignore 存在"
    
    # 检查关键忽略项
    IGNORED_PATTERNS=(
        "__pycache__"
        "*.pyc"
        "*.log"
        ".coverage"
        "node_modules"
    )
    
    for pattern in "${IGNORED_PATTERNS[@]}"; do
        if grep -q "$pattern" .gitignore; then
            echo "      ✅ $pattern 已忽略"
        else
            echo "      ⚠️  $pattern 未在 .gitignore 中"
            ((WARNINGS++))
        fi
    done
else
    echo "   ❌ .gitignore 缺失"
    ((ERRORS++))
fi

# 10. 检查 requirements.txt
echo ""
echo "10. 检查 requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "   ✅ requirements.txt 存在"
    
    LINE_COUNT=$(wc -l < requirements.txt)
    echo "      包含 $LINE_COUNT 个依赖"
    
    if [ $LINE_COUNT -lt 10 ]; then
        echo "      ⚠️  依赖数量偏少"
        ((WARNINGS++))
    fi
else
    echo "   ❌ requirements.txt 缺失"
    ((ERRORS++))
fi

# 总结
echo ""
echo "========================================="
echo "验证结果"
echo "========================================="
echo ""
echo "错误数: $ERRORS"
echo "警告数: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ 项目已准备好发布！"
    echo ""
    echo "下一步操作："
    echo "  1. 运行测试: pytest"
    echo "  2. 初始化数据库: python scripts/init_database.py"
    echo "  3. 启动服务: ./scripts/start_all_services.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  项目基本可以发布，但有 $WARNINGS 个警告需要检查"
    exit 0
else
    echo "❌ 项目未准备好发布，存在 $ERRORS 个错误"
    exit 1
fi
