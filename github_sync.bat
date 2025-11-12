@echo off
chcp 65001
echo ========================================
echo 一键同步到GitHub
echo ========================================
echo.

echo 正在添加所有修改...
git add .

echo.
echo 请输入提交信息（或直接回车使用默认信息）：
set /p commit_msg=

if "%commit_msg%"=="" (
    set commit_msg=update: 代码更新 %date% %time%
)

echo.
echo 提交信息: %commit_msg%
git commit -m "%commit_msg%"

echo.
echo 正在推送到GitHub...
git push

echo.
if %errorlevel% == 0 (
    echo ========================================
    echo ✅ 同步成功！
    echo 代码已安全备份到GitHub
    echo ========================================
) else (
    echo ========================================
    echo ❌ 同步失败
    echo 请检查网络连接
    echo ========================================
)

echo.
echo 查看仓库: https://github.com/dd-Dog/email_assistant
echo.
pause

