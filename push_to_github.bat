@echo off
echo ========================================
echo Pushing code to GitHub
echo ========================================
echo.

cd /d "d:\AI Shahid project"

echo Step 1: Initializing git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Creating commit...
git commit -m "Initial commit - AI Tagging App"

echo.
echo Step 4: Setting branch to main...
git branch -M main

echo.
echo Step 5: Adding GitHub remote...
git remote add origin https://github.com/NUN19/Shahid-AI-Tagging.git

echo.
echo Step 6: Pushing to GitHub...
echo (You may be prompted for GitHub credentials)
git push -u origin main

echo.
echo ========================================
echo Done! Check GitHub to see your code.
echo ========================================
pause

