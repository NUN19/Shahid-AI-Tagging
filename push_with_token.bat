@echo off
echo ========================================
echo Push to GitHub with Personal Access Token
echo ========================================
echo.
echo IMPORTANT: GitHub no longer accepts passwords!
echo You need a Personal Access Token.
echo.
echo If you don't have one:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Generate new token (classic)
echo 3. Check 'repo' scope
echo 4. Copy the token
echo.
echo Press any key when you have your token ready...
pause

cd /d "d:\AI Shahid project"

echo.
echo Pushing to GitHub...
echo.
echo When prompted:
echo - Username: NUN19
echo - Password: PASTE YOUR PERSONAL ACCESS TOKEN (not your GitHub password!)
echo.

git push -u origin main

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Your code is on GitHub!
    echo Check: https://github.com/NUN19/Shahid-AI-Tagging
    echo.
    echo Next step: Deploy to Render!
) else (
    echo There was an error.
    echo.
    echo Common issues:
    echo - Used password instead of token
    echo - Token doesn't have 'repo' scope
    echo - Token expired
    echo.
    echo Solution: Create a new token at https://github.com/settings/tokens
)
echo ========================================
pause

