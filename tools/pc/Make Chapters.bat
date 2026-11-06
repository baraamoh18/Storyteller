@echo off
setlocal
cd /d "%~dp0"
title Storyteller - make chapters
set "U2NET_HOME=%~dp0models"
set "TORCH_HOME=%~dp0models"
set "HF_HOME=%~dp0models"
if not exist ".venv\Scripts\python.exe" (
  echo  Run "Setup" first ^(double-click it once^).
  pause
  exit /b 1
)

rem ---- where the CBZ files are (remembered from last time)
set "CBZ=D:\Work\StoryTelling website\chapters"
if exist "cbz-folder.txt" set /p CBZ=<"cbz-folder.txt"
echo.
echo  Folder with your CBZ files:
echo    %CBZ%
set "NEW="
set /p NEW=  Press Enter to use it, or type another folder: 
if defined NEW set "NEW=%NEW:"=%"
if defined NEW set "CBZ=%NEW%"
>"cbz-folder.txt" echo %CBZ%

echo.
set "CH="
set /p CH=  Which chapters? For example 94, or 1-20, or 1-5,94: 
if "%CH%"=="" (
  echo  No chapters given.
  pause
  exit /b 1
)

echo.
echo  Making chapters %CH%. You can leave this running overnight:
echo   - keep the computer plugged in and set Windows to never sleep while it runs
echo     ^(Settings - System - Power - Screen and sleep^);
echo   - closing this window stops it; running it again carries on where it stopped.
echo.
".venv\Scripts\python.exe" make_chapter.py --cbz-dir "%CBZ%" --out "%~dp0finished" --chapters "%CH%" --work "%~dp0work"
echo.
echo  Finished chapters are in the "finished" folder:
echo    %~dp0finished
echo  Send the chapter_XXX.zip files to Claude.
if exist "%~dp0finished" explorer "%~dp0finished"
echo.
pause
