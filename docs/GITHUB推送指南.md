# GitHub 仓库连接与推送指南

## 前置条件

1. 确保已安装 Git
2. 拥有 GitHub 账号
3. 已在 GitHub 上创建新仓库

## 方式一：命令行推送（推荐）

### 1. 在 GitHub 创建新仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库名称：`magic-school-agent`
4. 选择 Public 或 Private
5. **不要**勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

### 2. 连接本地仓库到 GitHub

执行以下命令（替换 YOUR_USERNAME）：

```bash
cd /workspace/projects

# 添加远程仓库（替换 YOUR_USERNAME 为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/magic-school-agent.git

# 或者使用 SSH（如果配置了SSH密钥）
git remote add origin git@github.com:YOUR_USERNAME/magic-school-agent.git

# 查看远程仓库
git remote -v
```

### 3. 推送代码到 GitHub

```bash
# 首次推送（设置上游分支）
git push -u origin main

# 或如果本地分支是 master
git push -u origin master
```

### 4. 验证推送成功

访问你的 GitHub 仓库页面，应该能看到所有文件已上传。

## 方式二：使用 GitHub CLI（gh）

### 安装 GitHub CLI

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Windows
winget install --id GitHub.cli
```

### 登录并创建仓库

```bash
cd /workspace/projects

# 登录 GitHub
gh auth login

# 创建仓库并推送
gh repo create magic-school-agent --public --source=. --remote=origin --push
```

## 方式三：使用 GitHub Desktop（图形界面）

1. 下载并安装 [GitHub Desktop](https://desktop.github.com/)
2. 打开 GitHub Desktop
3. File → Add Local Repository → 选择 `/workspace/projects`
4. Repository → Repository Settings → 将远程仓库设置为你的 GitHub 仓库
5. 点击 "Publish repository"

## 常见问题

### Q1: 提示 "Authentication failed"

**解决方案**：

```bash
# 方法1：使用 Personal Access Token
# 1. GitHub 设置 → Developer settings → Personal access tokens → Tokens (classic)
# 2. 生成新 token，勾选 "repo" 权限
# 3. 推送时使用 token 作为密码

git push
Username: YOUR_GITHUB_USERNAME
Password: YOUR_PERSONAL_ACCESS_TOKEN
```

### Q2: 提示 "remote: Permission denied"

**原因**：
- 仓库地址写错了（检查用户名）
- 没有仓库的写入权限

**解决方案**：
```bash
# 更新远程仓库地址
git remote set-url origin https://github.com/CORRECT_USERNAME/magic-school-agent.git
```

### Q3: 提示 "Updates were rejected because the remote contains work you do not have locally"

**原因**：GitHub 仓库中有文件（如 README），本地没有

**解决方案**：
```bash
# 方案1：拉取远程变更后推送（推荐）
git pull origin main --allow-unrelated-histories
git push origin main

# 方案2：强制推送（会覆盖远程内容，慎用！）
git push origin main --force
```

### Q4: 大文件推送失败

**原因**：GitHub 单个文件限制为 100MB，仓库总大小建议小于 1GB

**解决方案**：
```bash
# 检查大文件
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print substr($0,6)}' | sort -nk2 | tail -10

# 如果有超过 100MB 的文件，需要从历史中移除
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch large_file.tar.gz' --prune-empty --tag-name-filter cat -- --all

# 然后再推送
git push origin main --force
```

## 推送后的后续操作

### 1. 设置仓库描述和标签

访问 GitHub 仓库页面 → Settings → General：
- Description: `基于LangGraph的魔法学校主题学习管理智能体`
- Topics: `langgraph`, `agent`, `education`, `python`, `fastapi`

### 2. 添加 README 和 LICENSE

- GitHub 已自动创建 README
- 在 Settings → General 中选择开源协议（MIT License）

### 3. 启用 GitHub Pages（可选）

Settings → Pages → Source: `main` → Save

### 4. 设置保护规则（推荐）

Settings → Branches → Add rule → Branch: `main`
勾选：
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

### 5. 添加贡献指南

创建 `.github/CONTRIBUTING.md` 文件

### 6. 添加 Issue 模板

创建 `.github/ISSUE_TEMPLATE/bug_report.md`

## 自动化部署到 GitHub Actions（可选）

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Server

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/
```

## 验证清单

推送完成后，确认以下内容：

- [ ] 所有代码文件都已上传
- [ ] README.md 显示正常
- [ ] LICENSE 文件存在
- [ ] .gitignore 配置正确
- [ ] 没有敏感信息（API密钥、密码等）被上传
- [ ] 大文件已排除
- [ ] 仓库描述和标签已设置

## 安全提醒

⚠️ **重要**：确认 `.env` 文件不会被提交到 Git

检查 `.gitignore` 中是否包含：
```
.env
*.key
*.pem
credentials.json
config/secrets/
```

如果已提交敏感信息，需要：
```bash
# 从历史中移除（不会删除本地文件）
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all
git push origin main --force
```

## 下一步

推送成功后，你可以：

1. **设置 Webhook**：自动触发部署
2. **配置 CI/CD**：自动化测试和部署
3. **邀请协作者**：团队协作开发
4. **发布 Releases**：版本管理

---

如有问题，请访问 [GitHub 官方文档](https://docs.github.com/) 查看详细说明。
