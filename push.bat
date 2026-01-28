@echo off
REM Check if a commit message argument is provided
IF "%~1"=="" (
    ECHO Error: Please provide a commit message as an argument.
    ECHO Usage: git_push.bat "Your commit message"
    EXIT /B 1
)

ECHO Staging all changes...
git add .

ECHO Committing changes with message: %1
git commit -m "%1"

ECHO Pushing changes to remote...
git push

REM Optional: Keep the window open to see the result
PAUSE
