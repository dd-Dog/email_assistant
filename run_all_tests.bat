@echo off
chcp 65001 >nul
echo.
echo ========================================
echo V5.2 完整测试
echo ========================================
echo.

echo [测试1] 人员信息加载测试
echo ----------------------------------------
python test_person_loader.py
if %errorlevel% neq 0 (
    echo [失败] 人员加载测试失败
    pause
    exit /b 1
)
echo.

echo [测试2] 项目文档加载测试
echo ----------------------------------------
python test_doc_loader.py
if %errorlevel% neq 0 (
    echo [失败] 项目文档加载测试失败
    pause
    exit /b 1
)
echo.

echo [测试3] 配置迁移工具测试
echo ----------------------------------------
echo 检查迁移文件是否存在...
if exist "persons\人员信息表_迁移.xlsx" (
    echo [OK] 迁移文件已存在: persons\人员信息表_迁移.xlsx
) else (
    echo [提示] 迁移文件不存在，可运行 migrate_to_excel.py 创建
)
echo.

echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 下一步：
echo 1. 查看 persons\人员信息表_迁移.xlsx
echo 2. 补充详细信息（可选）
echo 3. 重命名为 人员信息表.xlsx
echo 4. 运行主程序: python main_v4.py
echo.
pause

