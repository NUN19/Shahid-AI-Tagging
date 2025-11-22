@echo off
echo ========================================
echo Removing Excel File from GitHub
echo ========================================
echo.
echo This will:
echo 1. Add Excel files to .gitignore
echo 2. Remove Excel file from git tracking
echo 3. Keep the local file (won't delete it)
echo.

cd /d "d:\AI Shahid project"

echo Step 1: Removing Excel file from git tracking...
echo (This keeps the file locally, just removes it from git)
git rm --cached "Updated Mind Map.xlsx" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo File not tracked in git, or already removed.
)

echo.
echo Step 2: Adding all Excel files to .gitignore...
echo (Already done in .gitignore file)

echo.
echo Step 3: Committing the removal...
git add .gitignore
git commit -m "Remove Excel file from repository - users upload their own"

echo.
echo Step 4: Pushing to GitHub...
git push origin main

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Excel file removed from GitHub.
    echo.
    echo The file is still on your computer, but:
    echo - It's no longer tracked by git
    echo - It won't be pushed to GitHub
    echo - Users will upload their own Excel files
    echo.
    echo Your deployed app will update in 2-5 minutes.
) else (
    echo There was an error. Check the messages above.
    echo.
    echo If git is not found, use Git Bash instead:
    echo 1. Open Git Bash
    echo 2. cd "/d/AI Shahid project"
    echo 3. git rm --cached "Updated Mind Map.xlsx"
    echo 4. git add .gitignore
    echo 5. git commit -m "Remove Excel file from repository"
    echo 6. git push origin main
)
echo ========================================
pause

