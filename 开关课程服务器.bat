@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Python Course Server

set "PORT=8090"
set "PYW=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\pythonw.exe"
if not exist "%PYW%" set "PYW=pythonw"

rem ---- 端口是否已在监听 ----
set "PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT% " ^| findstr LISTENING') do set "PID=%%a"

if defined PID goto STOP
goto START

:START
echo.
start "" "%PYW%" "tools\serve.py" %PORT%
set "N=0"
:WAIT
set /a N+=1
ping -n 2 127.0.0.1 >nul
netstat -ano | findstr ":%PORT% " | findstr LISTENING >nul
if not errorlevel 1 goto OK
if %N% LSS 8 goto WAIT
echo   [FAILED]  server did not start after 8s
goto END

:OK
echo   [SERVER ON ]  http://127.0.0.1:%PORT%/index.html
echo                 (双击桌面「课程首页」打开；再运行本快捷方式即可关闭)
goto END

:STOP
taskkill /F /PID %PID% >nul 2>&1
echo.
echo   [SERVER OFF]  port %PORT% released

:END
ping -n 3 127.0.0.1 >nul
endlocal
