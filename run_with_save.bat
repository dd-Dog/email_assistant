@echo off
chcp 65001
echo ========================================
echo 邮箱助手 - 保存本地版
echo ========================================
echo.
echo 报告会保存到 reports 文件夹
echo 同时尝试发送邮件
echo.

python main_with_save.py

echo.
echo ========================================
echo 运行完成
echo 请查看 reports 文件夹中的报告文件
echo ========================================
pause

