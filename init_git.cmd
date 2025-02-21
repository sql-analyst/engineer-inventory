@echo off

REM Change to the project directory
cd /d C:\Users\sross\OneDrive\Documents\Consulting\Engineer_marketplace_flask

REM Set Git user configuration (should be done before git init)
git config --global user.name "sql-analyst"
git config --global user.email "s.ross_@hotmail.com"
git config --global core.autocrlf true

REM Initialize Git repository
git init

REM Add all files to the staging area
git add .

REM Commit the changes
git commit -m "Initial commit for Engineer Marketplace Flask project"

REM Add the remote GitHub repository (replace with your actual GitHub repository URL)
git remote add origin https://github.com/sql-analyst/engineer-inventory.git

REM If the main branch does not exist, create it locally
git branch -M main

REM Push to the GitHub repository (push to 'main' branch)
git push -u origin main

REM Pause to view the result
pause
