# GitHub 关联和自动提交指南

## 📦 一次性设置（首次使用）

### 1. 在GitHub创建仓库

访问 https://github.com/new

```
Repository name: email_assistant
Description: AI邮件助手 - 智能分析和汇总
Privacy: Private (私有仓库，保护隐私)
❌ 不要勾选 "Initialize this repository with a README"
```

点击 **Create repository**

### 2. 关联本地仓库

GitHub会显示指令，复制运行：

```bash
# HTTPS方式（简单，但每次需要输入密码）
git remote add origin https://github.com/YOUR_USERNAME/email_assistant.git

# SSH方式（推荐，配置后不需要密码）
git remote add origin git@github.com:YOUR_USERNAME/email_assistant.git
```

替换 `YOUR_USERNAME` 为您的GitHub用户名。

### 3. 首次推送

```bash
git push -u origin master
```

或双击运行 `push_to_github.bat`

---

## 🔄 日常提交流程

### 方式1：手动提交（完全控制）

每次修改后：

```bash
# 1. 查看修改
git status

# 2. 添加文件
git add .

# 3. 提交
git commit -m "feat: 描述你的修改"

# 4. 推送到GitHub
git push
```

### 方式2：使用批处理脚本（推荐）

我为您创建了便捷脚本 `push_to_github.bat`，双击即可推送。

### 方式3：在Cursor中操作

1. **查看修改**：
   - 点击左侧的 `Source Control` 图标（或按 `Ctrl+Shift+G`）
   - 查看所有修改的文件

2. **提交修改**：
   - 在 `Message` 框中输入提交信息
   - 点击 `✓ Commit` 按钮

3. **推送到GitHub**：
   - 点击 `...` 菜单
   - 选择 `Push`

---

## 🤖 自动提交方案

### 方案1：定时自动提交（推荐）

创建自动提交脚本：

```batch
@echo off
:: auto_commit.bat - 自动提交脚本

cd /d C:\workspace\python\email_assistant

:: 检查是否有修改
git status --short > status.txt
set /p STATUS=<status.txt
del status.txt

if not "%STATUS%"=="" (
    echo 发现修改，自动提交...
    git add .
    git commit -m "auto: 自动备份 - %date% %time%"
    git push
    echo 自动提交完成
) else (
    echo 没有修改，跳过提交
)
```

### 方案2：每次运行后自动提交

修改 `run_v4.bat`，在最后添加：

```batch
echo.
echo 是否自动提交到GitHub？(y/n)
set /p choice=
if /i "%choice%"=="y" (
    git add .
    git commit -m "auto: 运行报告备份 - %date%"
    git push
)
```

### 方案3：Windows任务计划自动备份

设置每天定时备份：

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每天23:00
4. 操作：运行 `auto_commit.bat`

---

## 🔐 SSH密钥配置（推荐，免密码）

### 1. 生成SSH密钥

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

一路回车，使用默认设置。

### 2. 查看公钥

```bash
cat ~/.ssh/id_ed25519.pub
```

复制整个公钥内容。

### 3. 添加到GitHub

1. GitHub → Settings → SSH and GPG keys
2. 点击 `New SSH key`
3. 粘贴公钥
4. 保存

### 4. 测试连接

```bash
ssh -T git@github.com
```

看到 "Hi YOUR_USERNAME!" 就成功了。

---

## 📋 推荐的工作流程

### 每天工作结束

```batch
:: 快速备份脚本
git add .
git commit -m "update: %date%的工作内容"
git push
```

### 重大更新后

```bash
git add .
git commit -m "feat: 详细描述新功能"
git push
```

### 出现问题时

```bash
# 暂存当前工作
git stash

# 恢复之前版本
git checkout v3.0

# 恢复工作
git stash pop
```

---

## 🎯 Cursor + GitHub 最佳实践

### 在Cursor中使用Git

1. **Source Control面板** (`Ctrl+Shift+G`)
   - 实时看到所有修改
   - 点击文件对比差异

2. **提交**
   - 输入提交信息
   - 点击 ✓ 提交

3. **推送**
   - 点击 `...` → `Push`
   - 或点击底部状态栏的同步按钮

4. **查看历史**
   - `...` → `View History`
   - 查看所有提交记录

### 自动同步设置

在Cursor中设置自动保存后推送：
1. `File` → `Preferences` → `Settings`
2. 搜索 `git.autoStash`
3. 开启自动暂存

---

## ✅ 现在开始设置

### 立即执行的命令

```bash
# 1. 检查当前状态
git remote -v

# 2. 如果没有remote，添加GitHub仓库
git remote add origin https://github.com/YOUR_USERNAME/email_assistant.git

# 3. 推送所有代码和标签
git push -u origin master --tags

# 4. 确认推送成功
git log --oneline -3
```

## 🎉 完成后的好处

- ✅ 代码云端备份，永不丢失
- ✅ 版本历史完整保留
- ✅ 可以随时回退到任何版本
- ✅ 在任何设备访问和编辑
- ✅ Cursor无缝集成GitHub

请告诉我：
1. 您的GitHub用户名是什么？
2. 是否需要我帮您生成完整的设置命令？
3. 是否需要自动备份脚本？

我可以帮您配置一键推送！🚀
