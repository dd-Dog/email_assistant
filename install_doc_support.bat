@echo off
chcp 65001 >nul
echo ========================================
echo 安装文档读取支持（Word和Excel）
echo ========================================
echo.

echo 正在安装 python-docx（Word文档支持）...
pip install python-docx==1.1.0
if %errorlevel% neq 0 (
    echo 错误：python-docx 安装失败
    pause
    exit /b 1
)
echo ✓ python-docx 安装成功
echo.

echo 正在安装 openpyxl（Excel文档支持）...
pip install openpyxl==3.1.2
if %errorlevel% neq 0 (
    echo 错误：openpyxl 安装失败
    pause
    exit /b 1
)
echo ✓ openpyxl 安装成功
echo.

echo ========================================
echo ✓ 文档读取支持安装完成！
echo ========================================
echo.
echo 现在可以读取以下格式的文档：
echo   - Word文档（.docx）
echo   - Excel文档（.xlsx, .xls）
echo   - 文本文档（.txt）
echo   - Markdown文档（.md）
echo.
pause

