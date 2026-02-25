# 🚀 推送代码到 GitHub

> 将魔法课桌学习助手项目推送到 GitHub 远程仓库

---

## 📊 当前状态

✅ **本地提交已完成**
- 本地分支领先远程分支 5 个提交
- 工作区干净，无待提交的更改
- 所有更改已提交到本地仓库

⚠️ **需要推送到远程仓库**
- 远程仓库：`https://github.com/Panb-KG/magic-school-agent.git`
- 分支：`main`

---

## 🔑 推送方式

### 方式 1：使用 GitHub Personal Access Token（推荐）

#### 步骤 1：创建 Personal Access Token

1. 登录 GitHub
2. 点击头像 → Settings
3. 左侧菜单 → Developer settings
4. Personal access tokens → Tokens (classic)
5. Generate new token → Generate new token (classic)
6. 填写信息：
   - **Note**: Magic School Agent
   - **Expiration**: 选择过期时间（推荐 90 天）
   - **Select scopes**: 勾选 `repo`（完整的仓库访问权限）
7. 点击 Generate token
8. **复制 Token**（注意：只显示一次，请妥善保存！）

#### 步骤 2：使用 Token 推送

```bash
# 方式 A：在 URL 中直接包含 Token
git push https://YOUR_TOKEN@github.com/Panb-KG/magic-school-agent.git main

# 方式 B：使用 git credential helper
git config --global credential.helper store
git push origin main
# 提示输入用户名和密码时：
# 用户名：YOUR_GITHUB_USERNAME
# 密码：YOUR_PERSONAL_ACCESS_TOKEN
```

#### 示例

```bash
# 替换 YOUR_TOKEN 为您的实际 Token
git push https://ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/Panb-KG/magic-school-agent.git main
```

---

### 方式 2：使用 SSH 密钥（推荐长期使用）

#### 步骤 1：生成 SSH 密钥

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 或者使用 RSA（较旧系统）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

#### 步骤 2：添加 SSH 密钥到 GitHub

1. 复制公钥
```bash
cat ~/.ssh/id_ed25519.pub
# 或
cat ~/.ssh/id_rsa.pub
```

2. 添加到 GitHub
   - 登录 GitHub
   - 点击头像 → Settings
   - 左侧菜单 → SSH and GPG keys
   - New SSH key
   - **Title**: Magic School Agent
   - **Key**: 粘贴刚才复制的公钥
   - Add SSH key

#### 步骤 3：修改远程仓库 URL

```bash
# 将远程仓库 URL 改为 SSH
git remote set-url origin git@github.com:Panb-KG/magic-school-agent.git

# 推送
git push origin main
```

---

### 方式 3：使用 GitHub CLI（推荐 GitHub 用户）

#### 步骤 1：安装 GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
# 从 https://cli.github.com/ 下载安装
```

#### 步骤 2：认证

```bash
gh auth login
# 按照提示完成认证
```

#### 步骤 3：推送

```bash
git push origin main
```

---

## 📝 推送命令汇总

### 快速推送（推荐方式 1）

```bash
# 1. 创建 Personal Access Token（见上方步骤）
# 2. 使用以下命令推送（替换 YOUR_TOKEN）

git push https://YOUR_TOKEN@github.com/Panb-KG/magic-school-agent.git main
```

### 使用 SSH（推荐方式 2）

```bash
# 1. 配置 SSH 密钥（见上方步骤）
# 2. 修改远程 URL
git remote set-url origin git@github.com:Panb-KG/magic-school-agent.git

# 3. 推送
git push origin main
```

---

## 🔍 验证推送

推送完成后，验证是否成功：

```bash
# 检查状态
git status

# 应该显示：
# Your branch is up to date with 'origin/main'.
```

或在浏览器中访问：
```
https://github.com/Panb-KG/magic-school-agent
```

查看最新的提交记录。

---

## 📋 本次推送的内容

本次推送包含 5 个提交：

1. **清理前端相关代码和文档**
   - 删除 27 个前端相关文件
   - 更新 README.md
   - 创建清理总结文档

2. **添加 API 部署说明文档**
   - 澄清部署架构
   - 对比 Coze 和独立服务模式
   - 提供完整的 API 调用示例

3. **添加 Coze API 集成指南**
   - 完整的 API 使用文档
   - 多语言调用示例
   - 错误处理和最佳实践

4. **创建 Coze API 集成示例**
   - HTML 演示页面
   - React 集成示例
   - Python SDK
   - 示例目录说明

5. **更新 README.md**
   - 添加部署方式选择说明
   - 添加快速集成指南
   - 更新文档链接

---

## ⚠️ 常见问题

### Q1: 推送时提示 "Authentication failed"

**A**：
- 检查 Personal Access Token 是否正确
- 确认 Token 有 `repo` 权限
- 确认 Token 未过期

### Q2: 推送时提示 "Permission denied"

**A**：
- 确认您有仓库的写入权限
- 检查仓库地址是否正确
- 确认 GitHub 账户名正确

### Q3: 推送时提示 "remote: Repository not found"

**A**：
- 确认仓库地址正确
- 确认仓库已创建
- 检查是否有访问权限

### Q4: 如何查看推送历史？

**A**：
```bash
# 查看本地提交历史
git log --oneline

# 查看远程提交历史
git log origin/main --oneline
```

---

## 📚 相关文档

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub SSH Keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitHub CLI](https://cli.github.com/)

---

## 🚀 下一步

推送成功后，您可以：

1. **在 GitHub 上创建 Release**
   ```bash
   gh release create v1.0.0
   ```

2. **创建 GitHub Pages**
   - 在仓库设置中启用 GitHub Pages
   - 部署文档网站

3. **配置 GitHub Actions**
   - 自动化测试
   - 自动化部署

---

**推送完成后，请验证 GitHub 仓库已更新！**

如有问题，请参考上方常见问题部分。
