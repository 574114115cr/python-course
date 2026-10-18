@echo off
chcp 65001 >nul
title Python course site
cd /d "%~dp0"
set PY=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe
if not exist "%PY%" set PY=python
echo.
echo   Python course site
echo   ------------------
echo   URL:   http://127.0.0.1:8090/index.html
echo   Stop:  press Ctrl+C in this window
echo.
start "" http://127.0.0.1:8090/index.html
"%PY%" "tools\serve.py" 8090
pause
