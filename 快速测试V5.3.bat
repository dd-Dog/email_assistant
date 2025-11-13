@echo off
chcp 65001 >nul
echo.
echo ========================================
echo V5.3 快速测试向导
echo ========================================
echo.

echo 步骤1: 检查Excel文件
echo ----------------------------------------
if exist "persons\人员信息表_V5.3.xlsx" (
    echo [OK] 找到V5.3 Excel文件
) else (
    echo [提示] 未找到V5.3 Excel文件
    echo.
    echo 您有两个选择：
    echo.
    echo 【选择A - 从config.json迁移（推荐）】
    echo   1. 运行: python migrate_to_excel.py
    echo   2. 然后: move persons\人员信息表_迁移.xlsx persons\人员信息表_V5.3.xlsx
    echo.
    echo 【选择B - 创建新模板】
    echo   1. 运行: python create_person_excel_v5.3.py
    echo.
    choice /C AB /M "请选择（A=迁移/B=新建）"
    
    if errorlevel 2 (
        echo.
        echo 正在创建V5.3模板...
        python create_person_excel_v5.3.py
        if errorlevel 1 (
            echo [失败] 创建失败
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo 正在迁移config.json...
        python migrate_to_excel.py
        if errorlevel 1 (
            echo [失败] 迁移失败
            pause
            exit /b 1
        )
        echo.
        echo 正在重命名文件...
        move persons\人员信息表_迁移.xlsx persons\人员信息表_V5.3.xlsx
    )
)
echo.

echo 步骤2: 测试人员加载
echo ----------------------------------------
python test_person_loader.py
if errorlevel 1 (
    echo [失败] 人员加载测试失败
    pause
    exit /b 1
)
echo.

echo 步骤3: 测试组织关系
echo ----------------------------------------
python test_org_relationship.py
if errorlevel 1 (
    echo [失败] 组织关系测试失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 测试结果：
echo [OK] 人员信息加载成功
echo [OK] 组织关系功能正常
echo.
echo 下一步：
echo 1. 打开Excel补充详细信息（可选）
echo    start persons\人员信息表_V5.3.xlsx
echo.
echo 2. 运行主程序
echo    python main_v4.py
echo.
pause

