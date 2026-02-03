# 在 Mac 上访问服务器前端界面的完整指南

## 📋 前提条件

- Mac 电脑
- 服务器 IP 地址：`101.126.128.57`
- 服务器用户名：需要提供（通常是 root 或其他用户）
- 服务器密码或 SSH 密钥

---

## 🚀 方法 1: SSH 端口转发（推荐）

### 步骤 1: 打开终端

在 Mac 上，按 `Command + 空格`，输入「终端」或「Terminal」，然后按回车。

### 步骤 2: 建立 SSH 隧道

```bash
ssh -L 5173:localhost:5173 username@101.126.128.57
```

将 `username` 替换为你的服务器用户名，例如：
```bash
ssh -L 5173:localhost:5173 root@101.126.128.57
```

**参数说明**：
- `-L 5173:localhost:5173`: 将本地 5173 端口转发到服务器的 localhost:5173
- `username@101.126.128.57`: 你的服务器地址

### 步骤 3: 输入密码

如果使用密码认证，输入密码（输入时不会显示）。

### 步骤 4: 访问应用

保持终端窗口打开，然后在浏览器中访问：
```
http://localhost:5173/
```

### 步骤 5: 使用完成后关闭

在终端窗口按 `Ctrl + C` 关闭 SSH 连接。

---

## 🔑 方法 2: 使用 SSH 密钥（更安全）

### 步骤 1: 生成 SSH 密钥

在 Mac 终端运行：
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

按回车使用默认路径，可以设置密码（可选）。

### 步骤 2: 复制公钥到服务器

```bash
ssh-copy-id username@101.126.128.57
```

如果 `ssh-copy-id` 不可用，手动复制：
```bash
cat ~/.ssh/id_rsa.pub | ssh username@101.126.128.57 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 步骤 3: 使用密钥连接

```bash
ssh -i ~/.ssh/id_rsa -L 5173:localhost:5173 username@101.126.128.57
```

### 步骤 4: 访问应用

在浏览器访问：
```
http://localhost:5173/
```

---

## 🌐 方法 3: 通过 VPN 或内网访问

如果你的 Mac 和服务器在同一网络：

```bash
ping 101.126.128.57
```

如果能 ping 通，直接在浏览器访问：
```
http://101.126.128.57:5173/
```

或者使用内网 IP：
```
http://9.128.44.145:5173/
```

---

## 🔧 方法 4: 使用第三方工具

### 使用 iTerm2（推荐终端）

1. 下载安装 iTerm2: https://iterm2.com/
2. 打开 iTerm2
3. 使用 SSH 命令：
```bash
ssh -L 5173:localhost:5173 username@101.126.128.57
```

### 使用 Royal TSX（SSH 客户端）

1. 下载安装 Royal TSX
2. 创建新的 SSH 连接
3. 配置端口转发：本地 5173 → 远程 localhost:5173
4. 连接后访问：http://localhost:5173/

### 使用 VS Code

1. 安装 VS Code
2. 安装 "Remote - SSH" 扩展
3. 配置 SSH 连接
4. 使用端口转发功能

---

## 📱 方法 5: 使用浏览器扩展

### 使用 "Allow CORS" 扩展

如果遇到 CORS 问题：

1. 在 Chrome 浏览器中安装 "Allow CORS: Access-Control-Allow-Origin" 扩展
2. 启用扩展
3. 重新访问应用

---

## 🔐 访问后登录

成功访问后，使用测试账号登录：

### 学生账号
- 用户名: `student`
- 密码: `password123`

### 家长账号
- 用户名: `parent`
- 密码: `password123`

---

## 🛠️ 常见问题

### Q1: 连接被拒绝

**错误**: `ssh: connect to host 101.126.128.57 port 22: Connection refused`

**解决**:
1. 检查 SSH 服务是否运行：在服务器上运行 `systemctl status sshd`
2. 检查防火墙：确认 22 端口开放
3. 检查云服务商安全组：开放 SSH 端口 22

### Q2: 权限被拒绝

**错误**: `Permission denied (publickey)`

**解决**:
1. 使用密码登录：`ssh -o PreferredAuthentications=password username@101.126.128.57`
2. 或配置 SSH 密钥（见方法 2）

### Q3: 端口已被占用

**错误**: `bind: Address already in use`

**解决**: 使用其他端口：
```bash
ssh -L 8080:localhost:5173 username@101.126.128.57
```
然后访问：http://localhost:8080/

### Q4: 连接超时

**解决**:
1. 检查网络连接
2. 确认服务器 IP 正确
3. 检查防火墙设置

---

## 💡 最佳实践

### 1. 保存 SSH 配置

编辑 `~/.ssh/config`:
```
Host magic-school
    HostName 101.126.128.57
    User username
    Port 22
    IdentityFile ~/.ssh/id_rsa
    LocalForward 5173 localhost:5173
```

然后只需运行：
```bash
ssh magic-school
```

### 2. 后台运行 SSH 隧道

```bash
ssh -N -f -L 5173:localhost:5173 username@101.126.128.57
```

- `-N`: 不执行远程命令
- `-f`: 后台运行

查看后台隧道：
```bash
ps aux | grep ssh
```

关闭后台隧道：
```bash
killall ssh
```

### 3. 使用 SSH 配置文件

创建多个端口转发：
```bash
ssh -L 5173:localhost:5173 -L 3000:localhost:3000 -L 5000:localhost:5000 username@101.126.128.57
```

### 4. 自动重连

使用 autossh 自动重连：
```bash
# 安装 autossh
brew install autossh

# 使用 autossh
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -L 5173:localhost:5173 username@101.126.128.57
```

---

## 🎯 快速开始（最简单的方法）

1. 打开 Mac 终端
2. 运行：
```bash
ssh -L 5173:localhost:5173 root@101.126.128.57
```
3. 输入密码
4. 在浏览器访问：http://localhost:5173/
5. 使用账号登录：student / password123

---

## 📚 相关资源

- SSH 官方文档: https://www.openssh.com/manual.html
- iTerm2: https://iterm2.com/
- VS Code Remote: https://code.visualstudio.com/docs/remote/ssh

---

## 🎉 完成！

现在你可以在 Mac 上通过 SSH 隧道访问服务器上的前端界面了！

**记住**: SSH 终端窗口必须保持打开状态才能访问应用。
