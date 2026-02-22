#!/usr/bin/env python3
"""
策略二：技术架构检查
从代码质量、错误处理、安全性、性能等技术角度检查 Agent 软件的完备性
"""

import sys
import os
from pathlib import Path
import re
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_error_handling(file_path):
    """检查文件的错误处理"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 检查是否有 try-except 块
        if 'try:' not in content:
            issues.append("缺少 try-except 错误处理")
        
        # 检查是否使用了裸 except
        if re.search(r'except\s*:', content):
            issues.append("使用了裸 except (应该指定异常类型)")
        
        # 检查是否有日志记录
        if 'import logging' not in content and 'logger' not in content and 'print(' not in content:
            issues.append("缺少日志记录")
        
        # 检查是否捕获了所有异常但没有重新抛出
        if re.search(r'except\s+Exception.*:\s*\n(?!.*raise)(?!.*logging)', content):
            issues.append("捕获异常但未记录日志")
        
        return issues
    except Exception as e:
        return [f"检查错误处理时出错: {str(e)}"]


def check_security(file_path):
    """检查文件的安全性"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 检查 SQL 注入风险
        if re.search(r'execute\s*\(\s*f["\'].*{', content):
            issues.append("可能存在 SQL 注入风险 (使用 f-string 构建查询)")
        
        # 检查硬编码密码或密钥
        if re.search(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']{8,}["\']', content, re.IGNORECASE):
            issues.append("可能存在硬编码的敏感信息")
        
        # 检查是否验证用户输入
        if 'def ' in content and '@tool' in content:
            # 检查工具函数是否有参数验证
            functions = re.findall(r'@tool\s*\ndef\s+(\w+)\s*\([^)]+\)', content)
            for func in functions:
                # 简单检查：函数体中是否有验证逻辑
                func_match = re.search(rf'def\s+{func}\s*\([^)]+\):[^@]+(?=\n@|\ndef\s+\w|\Z)', content, re.DOTALL)
                if func_match:
                    func_body = func_match.group(0)
                    if 'if' not in func_body or 'check' not in func_body.lower():
                        issues.append(f"工具函数 {func} 可能缺少参数验证")
        
        # 检查权限检查
        if 'def ' in content and '@tool' in content:
            if '@require_student_access' not in content and '_check_student_access' not in content:
                issues.append("工具函数可能缺少权限检查")
        
        return issues
    except Exception as e:
        return [f"检查安全性时出错: {str(e)}"]


def check_code_quality(file_path):
    """检查代码质量"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        issues = []
        
        # 检查文件长度
        if len(lines) > 500:
            issues.append(f"文件过长 ({len(lines)} 行)，建议拆分")
        
        # 检查函数长度
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                func_start = i
                func_name = re.search(r'def\s+(\w+)', line).group(1)
                # 查找函数结束位置
                indent_level = len(line) - len(line.lstrip())
                for j in range(i + 1, min(i + 101, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith('#'):
                        if len(lines[j]) - len(lines[j].lstrip()) <= indent_level and not lines[j].strip().startswith(('"""', "'''")):
                            func_length = j - func_start
                            if func_length > 50:
                                issues.append(f"函数 {func_name} 过长 ({func_length} 行)")
                            break
        
        # 检查注释覆盖
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        docstring_lines = len(re.findall(r'"""[^"]*"""', content, re.DOTALL)) + len(re.findall(r"'''[^']*'''", content, re.DOTALL))
        total_lines = len([line for line in lines if line.strip()])
        
        if total_lines > 0:
            comment_ratio = (comment_lines + docstring_lines) / total_lines
            if comment_ratio < 0.1:
                issues.append(f"注释覆盖率低 ({comment_ratio*100:.1f}%)，建议添加更多注释")
        
        # 检查重复代码
        # 简单检查：检查是否有重复的 import 语句
        imports = re.findall(r'^from\s+\S+\s+import|^\s*import\s+\S+', content, re.MULTILINE)
        if len(imports) != len(set(imports)):
            issues.append("存在重复的 import 语句")
        
        return issues
    except Exception as e:
        return [f"检查代码质量时出错: {str(e)}"]


def check_database_operations(file_path):
    """检查数据库操作的规范性"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 检查是否使用了连接池
        if 'get_session' in content or 'get_engine' in content:
            # 检查是否正确关闭连接
            if 'get_session' in content:
                if 'finally:' not in content or 'close()' not in content:
                    issues.append("可能未正确关闭数据库连接")
        
        # 检查是否使用了事务
        if 'insert' in content.lower() or 'update' in content.lower() or 'delete' in content.lower():
            if 'commit()' not in content:
                issues.append("可能未使用事务，数据可能不一致")
        
        # 检查是否有参数化查询
        if re.search(r'execute\s*\(\s*f["\'].*SELECT.*FROM', content, re.IGNORECASE):
            issues.append("可能未使用参数化查询")
        
        return issues
    except Exception as e:
        return [f"检查数据库操作时出错: {str(e)}"]


def check_testing():
    """检查测试覆盖"""
    tests_dir = Path(__file__).parent.parent / "tests"
    src_dir = Path(__file__).parent.parent / "src"
    
    issues = []
    
    if not tests_dir.exists():
        issues.append("tests 目录不存在")
        return issues
    
    # 统计测试文件
    test_files = list(tests_dir.glob("**/test_*.py")) + list(tests_dir.glob("**/*_test.py"))
    src_files = list(src_dir.glob("**/*.py"))
    
    if len(src_files) > 0 and len(test_files) == 0:
        issues.append("没有测试文件")
    elif len(test_files) < len(src_files) * 0.5:
        issues.append(f"测试覆盖率低 ({len(test_files)}/{len(src_files)} 文件有测试)")
    
    return issues


def check_documentation():
    """检查文档完整性"""
    docs_dir = Path(__file__).parent.parent / "docs"
    src_dir = Path(__file__).parent.parent / "src"
    
    issues = []
    
    required_docs = [
        "README.md",
        "功能说明文档.md"
    ]
    
    for doc in required_docs:
        if not (docs_dir / doc).exists():
            issues.append(f"缺少文档: {doc}")
    
    # 检查 API 文档
    if not (docs_dir / "后端API完整文档-Figma设计用.md").exists():
        issues.append("缺少 API 文档")
    
    return issues


def run_technical_check():
    """执行技术架构检查"""
    print("=" * 80)
    print("策略二：技术架构检查")
    print("=" * 80)
    print()
    
    # 1. 检查工具文件的技术质量
    print("1️⃣ 工具文件技术质量检查")
    print("-" * 80)
    
    tools_dir = Path(__file__).parent.parent / "src" / "tools"
    tool_files = list(tools_dir.glob("*_tool.py")) if tools_dir.exists() else []
    
    total_issues = 0
    issues_by_type = {
        "error_handling": 0,
        "security": 0,
        "code_quality": 0,
        "database": 0
    }
    
    for tool_file in tool_files:
        if tool_file.name.startswith("_"):
            continue
        
        error_issues = check_error_handling(tool_file)
        security_issues = check_security(tool_file)
        quality_issues = check_code_quality(tool_file)
        db_issues = check_database_operations(tool_file)
        
        file_issues = error_issues + security_issues + quality_issues + db_issues
        
        if file_issues:
            print(f"\n{tool_file.name}:")
            for issue in file_issues:
                print(f"  ⚠️  {issue}")
                total_issues += 1
                
                # 分类统计
                if issue in error_issues:
                    issues_by_type["error_handling"] += 1
                elif issue in security_issues:
                    issues_by_type["security"] += 1
                elif issue in quality_issues:
                    issues_by_type["code_quality"] += 1
                elif issue in db_issues:
                    issues_by_type["database"] += 1
    
    if total_issues == 0:
        print("✅ 所有工具文件的技术质量良好")
    else:
        print(f"\n总计发现 {total_issues} 个问题")
    
    print()
    
    # 2. 检查测试覆盖
    print("2️⃣ 测试覆盖检查")
    print("-" * 80)
    test_issues = check_testing()
    if test_issues:
        for issue in test_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ 测试覆盖良好")
    print()
    
    # 3. 检查文档
    print("3️⃣ 文档完整性检查")
    print("-" * 80)
    doc_issues = check_documentation()
    if doc_issues:
        for issue in doc_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ 文档完整")
    print()
    
    # 4. 检查配置管理
    print("4️⃣ 配置管理检查")
    print("-" * 80)
    
    config_issues = []
    
    # 检查环境变量使用
    if (tools_dir / "file_storage_tool.py").exists():
        with open(tools_dir / "file_storage_tool.py", 'r', encoding='utf-8') as f:
            if 'os.getenv' not in f.read():
                config_issues.append("文件存储工具未使用环境变量管理配置")
    
    if config_issues:
        for issue in config_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ 配置管理良好")
    print()
    
    # 5. 检查依赖管理
    print("5️⃣ 依赖管理检查")
    print("-" * 80)
    
    req_file = Path(__file__).parent.parent / "requirements.txt"
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"✅ requirements.txt 存在，包含 {len(requirements)} 个依赖")
    else:
        print("  ⚠️  requirements.txt 不存在")
    print()
    
    # 6. 检查数据迁移系统
    print("6️⃣ 数据迁移系统检查")
    print("-" * 80)
    
    migration_manager = Path(__file__).parent.parent / "src" / "storage" / "database" / "migration_manager.py"
    migrations_dir = Path(__file__).parent.parent / "migrations"
    
    migration_issues = []
    
    if not migration_manager.exists():
        migration_issues.append("迁移管理器不存在")
    else:
        print("  ✅ 迁移管理器存在")
    
    if not migrations_dir.exists():
        migration_issues.append("migrations 目录不存在")
    else:
        migration_files = list(migrations_dir.glob("*.json"))
        print(f"  ✅ 发现 {len(migration_files)} 个迁移定义")
    
    if migration_issues:
        for issue in migration_issues:
            print(f"  ⚠️  {issue}")
    print()
    
    # 7. 统计结果
    print("7️⃣ 统计结果")
    print("-" * 80)
    print(f"检查的工具文件数量: {len(tool_files)}")
    print(f"发现的问题总数: {total_issues}")
    print(f"  - 错误处理问题: {issues_by_type['error_handling']}")
    print(f"  - 安全性问题: {issues_by_type['security']}")
    print(f"  - 代码质量问题: {issues_by_type['code_quality']}")
    print(f"  - 数据库操作问题: {issues_by_type['database']}")
    print()
    
    # 8. 评分
    print("8️⃣ 技术架构评分")
    print("-" * 80)
    
    # 简单评分算法
    scores = {
        "代码质量": max(0, 100 - issues_by_type["code_quality"] * 5),
        "安全性": max(0, 100 - issues_by_type["security"] * 10),
        "错误处理": max(0, 100 - issues_by_type["error_handling"] * 5),
        "数据库操作": max(0, 100 - issues_by_type["database"] * 10),
        "测试覆盖": 100 if not test_issues else 50,
        "文档完整": 100 if not doc_issues else 50,
        "迁移系统": 100 if not migration_issues else 50
    }
    
    for category, score in scores.items():
        status = "✅" if score >= 80 else ("⚠️" if score >= 60 else "❌")
        print(f"  {status} {category}: {score}/100")
    
    avg_score = sum(scores.values()) / len(scores)
    print(f"\n  📊 综合评分: {avg_score:.1f}/100")
    
    if avg_score >= 90:
        overall_status = "优秀"
    elif avg_score >= 80:
        overall_status = "良好"
    elif avg_score >= 70:
        overall_status = "中等"
    elif avg_score >= 60:
        overall_status = "及格"
    else:
        overall_status = "需要改进"
    
    print(f"  📈 整体评级: {overall_status}")
    
    print()
    print("=" * 80)
    
    return {
        "total_issues": total_issues,
        "issues_by_type": issues_by_type,
        "test_issues": test_issues,
        "doc_issues": doc_issues,
        "scores": scores,
        "avg_score": avg_score,
        "overall_status": overall_status
    }


if __name__ == "__main__":
    results = run_technical_check()
    
    # 保存结果
    output_file = Path(__file__).parent / "strategy2_technical_check.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n检查结果已保存到: {output_file}")
