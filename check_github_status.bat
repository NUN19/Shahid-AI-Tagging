@echo off
echo ========================================
echo Checking GitHub Status
echo ========================================
echo.

cd /d "d:\AI Shahid project"

echo Checking if code is on GitHub...
echo.
echo Opening GitHub repository in browser...
start https://github.com/NUN19/Shahid-AI-Tagging

echo.
echo ========================================
echo Check your browser - do you see your files?
echo ========================================
echo.
echo If YES - Great! Proceed to Render deployment.
echo If NO - You need to use Personal Access Token.
echo.
pause

