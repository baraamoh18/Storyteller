@echo off
setlocal
cd /d "%~dp0"
title Storyteller reader

rem ---- any Python 3 will do (the reader only uses what comes with Python)
py -3 --version >nul 2>nul
if not errorlevel 1 (set "PY=py -3" & goto run)
python --version >nul 2>nul
if not errorlevel 1 (set "PY=python" & goto run)
echo.
echo  Python is not installed yet.
echo   1. Open https://www.python.org/downloads/release/python-3128/
echo   2. Download "Windows installer (64-bit)" and run it. Tick "Add python.exe to PATH".
echo   3. Then double-click "Read Storyteller" again.
echo.
pause
exit /b 1

:run
%PY% "%~dp0reader.py"
if errorlevel 1 pause
