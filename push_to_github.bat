@echo off
chcp 65001
echo ========================================
echo 推送代码到GitHub
echo ========================================
echo.

echo 提示：首次推送需要先关联远程仓库
echo.
echo 如果还没关联，请先运行：
echo git remote add origin https://github.com/YOUR_USERNAME/email_assistant.git
echo.

echo 开始推送...
git push -u origin master

echo.
if %errorlevel% == 0 (
    echo ========================================
    echo ✅ 推送成功！
    echo ========================================
) else (
    echo ========================================
    echo ❌ 推送失败
    echo 请检查：
    echo 1. 是否已关联远程仓库
    echo 2. 是否有推送权限
    echo 3. 网络连接是否正常
    echo ========================================
)

echo.
pause

