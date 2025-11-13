@echo off
chcp 65001 >nul
echo.
echo ========================================
echo V5.3 Quick Test
echo ========================================
echo.

echo Step 1: Check Excel file
echo ----------------------------------------
if exist "persons\人员信息表_V5.3.xlsx" (
    echo [OK] Found V5.3 Excel file
    goto test
)

echo [Notice] V5.3 Excel not found
echo.
echo Please choose:
echo   A - Migrate from config.json (Recommended)
echo   B - Create new template
echo.
choice /C AB /M "Choose (A/B)"

if errorlevel 2 (
    echo.
    echo Creating V5.3 template...
    python create_person_excel_v5.3.py
) else (
    echo.
    echo Migrating from config.json...
    python migrate_to_excel.py
    echo.
    echo Renaming file...
    move persons\人员信息表_迁移.xlsx persons\人员信息表_V5.3.xlsx
)
echo.

:test
echo Step 2: Test person loading
echo ----------------------------------------
python test_person_loader.py
echo.

echo Step 3: Test org relationships
echo ----------------------------------------
python test_org_relationship.py
echo.

echo ========================================
echo Test Completed!
echo ========================================
echo.
echo Next steps:
echo 1. Edit Excel to add org relationships (optional):
echo    start persons\人员信息表_V5.3.xlsx
echo.
echo 2. Run main program:
echo    python main_v4.py
echo.
pause

