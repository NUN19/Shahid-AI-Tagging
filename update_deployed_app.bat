@echo off
echo ========================================
echo Deploying Updates to GitHub
echo ========================================
echo.

cd /d "d:\AI Shahid project"

echo Step 1: Checking git status...
git status

echo.
echo Step 2: Adding all changes...
git add .

echo.
echo Step 3: Committing changes...
git commit -m "Fix Gemini API error handling and JSON response issues"

echo.
echo Step 4: Pushing to GitHub...
echo (This will trigger auto-deployment on Render/Railway)
git push origin main

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Changes pushed to GitHub.
    echo.
    echo Next steps:
    echo 1. Wait 2-5 minutes for auto-deployment
    echo 2. Check your Render/Railway dashboard
    echo 3. Test your deployed link once deployment completes
    echo.
    echo Your deployed URL should update automatically!
) else (
    echo There was an error. Check the messages above.
    echo.
    echo Common issues:
    echo - Git not configured (run complete_setup.bat first)
    echo - No changes to commit
    echo - Authentication failed (use Personal Access Token)
)
echo ========================================
pause

