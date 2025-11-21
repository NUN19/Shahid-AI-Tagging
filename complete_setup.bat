@echo off
echo ========================================
echo Complete GitHub Setup
echo ========================================
echo.

cd /d "d:\AI Shahid project"

echo Step 1: Configuring Git user...
echo (Using your GitHub email - you can change this later)
git config user.email "NUN19@users.noreply.github.com"
git config user.name "NUN19"

echo.
echo Step 2: Initializing git repository...
git init

echo.
echo Step 3: Adding all files...
git add .

echo.
echo Step 4: Creating first commit...
git commit -m "Initial commit - AI Tagging App"

echo.
echo Step 5: Setting branch to main...
git branch -M main

echo.
echo Step 6: Adding GitHub remote...
git remote remove origin 2>nul
git remote add origin https://github.com/NUN19/Shahid-AI-Tagging.git

echo.
echo Step 7: Pushing to GitHub...
echo (You may be prompted for GitHub credentials)
echo (Use Personal Access Token as password)
git push -u origin main

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Your code is on GitHub!
    echo Check: https://github.com/NUN19/Shahid-AI-Tagging
) else (
    echo There was an error. Check the messages above.
    echo.
    echo Common fixes:
    echo - If authentication failed, use Personal Access Token
    echo - If branch error, the commit might not have been created
)
echo ========================================
pause

