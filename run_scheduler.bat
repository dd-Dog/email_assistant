@echo off
chcp 65001
echo ========================================
echo 邮箱助手 - 定时任务模式
echo ========================================
echo.
echo 程序将在每天配置的时间自动运行
echo 按 Ctrl+C 可以停止
echo.

python scheduler.py

pause

