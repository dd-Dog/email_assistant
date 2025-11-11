@echo off
chcp 65001
echo ========================================
echo 邮箱助手 - 安装依赖
echo ========================================
echo.

python --version
echo.

echo 正在安装依赖包...
pip install -r requirements.txt

echo.
echo ========================================
echo 安装完成！
echo.
echo 下一步：
echo 1. 复制 config.example.json 为 config.json
echo 2. 编辑 config.json 填入您的邮箱信息
echo 3. 运行 run_once.bat 测试
echo ========================================
pause

