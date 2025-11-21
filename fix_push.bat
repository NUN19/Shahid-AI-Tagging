@echo off
echo ========================================
echo Fixing GitHub Push Error
echo ========================================
echo.
echo This will pull remote files first, then push.
echo.

cd /d "d:\AI Shahid project"

echo Step 1: Pulling remote repository...
echo (This merges any files from GitHub with your local files)
git pull origin main --allow-unrelated-histories

echo.
echo Step 2: Adding any new files...
git add .

echo.
echo Step 3: Committing merge...
git commit -m "Merge remote repository with local files"

echo.
echo Step 4: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done! Check GitHub to see your code.
echo ========================================
pause

