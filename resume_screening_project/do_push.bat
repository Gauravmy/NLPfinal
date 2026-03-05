@echo off
setlocal enabledelayedexpansion

cd /d C:\Users\hp\Desktop\NLPpro\resume_screening_project

git config user.email "dev@resumescreening.com"
git config user.name "Bot"
git add .
git commit -m "docs: Add deployment documentation and links"
git push origin main
echo.
echo Push completed - check GitHub for updates
