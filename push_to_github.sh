#!/bin/bash
# 推送代码到 GitHub 脚本

echo "=========================================="
echo "  魔法课桌学习助手 - 推送到 GitHub"
echo "=========================================="
echo ""

# 检查 Git 状态
echo "📊 检查 Git 状态..."
git status

echo ""
echo "⚠️  注意：您需要提供 GitHub 认证信息"
echo ""

# 选项 1：使用 Personal Access Token
echo "=========================================="
echo "方式 1：使用 Personal Access Token"
echo "=========================================="
echo ""
echo "请按以下步骤操作："
echo "1. 访问：https://github.com/settings/tokens"
echo "2. 点击 'Generate new token' → 'Generate new token (classic)'"
echo "3. 创建一个具有 'repo' 权限的 Token"
echo "4. 复制生成的 Token"
echo ""
read -p "请输入您的 GitHub Personal Access Token: " GITHUB_TOKEN

if [ -n "$GITHUB_TOKEN" ]; then
    echo ""
    echo "🚀 正在推送到 GitHub..."
    git push https://${GITHUB_TOKEN}@github.com/Panb-KG/magic-school-agent.git main

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 推送成功！"
        echo ""
        echo "📌 访问您的仓库："
        echo "https://github.com/Panb-KG/magic-school-agent"
    else
        echo ""
        echo "❌ 推送失败，请检查 Token 是否正确"
    fi
else
    echo ""
    echo "❌ 未输入 Token，已取消推送"
fi

echo ""
echo "=========================================="
echo "如需其他推送方式，请参考 PUSH_TO_GITHUB.md"
echo "=========================================="
