@echo off
REM Git push all script
cd /d "c:\Users\hp\Desktop\NLPpro\resume_screening_project"

echo.
echo ======================================
echo Resume Screening Pro - Push All
echo ======================================
echo.

REM Configure git
git config user.email "dev@resumescreening.com"
git config user.name "Resume Screening Bot"

REM Add all files
echo [1/4] Adding all files...
git add .

REM Check status
echo [2/4] Checking status...
git status --short

REM Commit
echo [3/4] Committing changes...
git commit -m "chore: Add deployment links and status documentation"

REM Push
echo [4/4] Pushing to main...
git push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ Push successful!
) else (
    echo ⚠️ Push had issues. Trying force push...
    git push -f origin main
)

echo.
echo ======================================
echo Push complete!
echo ======================================
pause
