@echo off
echo ========================================
echo 修复Git中文编码问题
echo ========================================
echo.

echo 正在配置Git编码设置...

git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8

echo.
echo ✅ Git编码配置完成
echo.
echo 注意：
echo 1. 建议使用英文提交信息（更通用）
echo 2. 如果必须用中文，可以在CMD中提交
echo 3. 或者在Cursor的Source Control面板中提交
echo.
echo ========================================
pause

