@echo off
echo ========================================
echo Fix Railway Python Installation Error
echo ========================================
echo.

cd /d "d:\AI Shahid project"

echo Option 1: Update runtime.txt (already done)
echo Option 2: Remove runtime.txt (let Railway auto-detect)
echo.
echo Which do you prefer?
echo [1] Keep updated runtime.txt (python-3.11)
echo [2] Remove runtime.txt (auto-detect)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Using updated runtime.txt...
    git add runtime.txt
    git commit -m "Fix Python version for Railway - use python-3.11"
) else if "%choice%"=="2" (
    echo.
    echo Removing runtime.txt...
    git rm runtime.txt
    git commit -m "Remove runtime.txt - let Railway auto-detect Python"
) else (
    echo Invalid choice. Using option 1 (updated runtime.txt)...
    git add runtime.txt
    git commit -m "Fix Python version for Railway - use python-3.11"
)

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done! Railway will auto-redeploy.
echo Wait 2-3 minutes and check Railway dashboard.
echo ========================================
pause

