@echo off
setlocal
cd /d "%~dp0"
title Storyteller - one-time setup
echo.
echo  Storyteller: one-time setup for this computer
echo  =============================================
echo  This installs the AI tools (about 6 GB including the models). It takes 10-20 minutes.
echo.

rem ---- Python 3.12
py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo  Python 3.12 is not installed yet.
  echo   1. Open https://www.python.org/downloads/release/python-3128/
  echo   2. Download "Windows installer (64-bit)" and run it. Tick "Add python.exe to PATH".
  echo   3. Then double-click this Setup file again.
  echo.
  pause
  exit /b 1
)

rem ---- keep the models next to these files, not on drive C:
set "U2NET_HOME=%~dp0models"
set "TORCH_HOME=%~dp0models"
set "HF_HOME=%~dp0models"

if not exist ".venv\Scripts\python.exe" (
  echo  Making a private Python folder for the tools ...
  py -3.12 -m venv .venv || goto failed
)
set "PY=.venv\Scripts\python.exe"
"%PY%" -m pip install --upgrade pip --quiet || goto failed

echo  Installing PyTorch for NVIDIA RTX 50-series cards (about 3 GB) ...
"%PY%" -m pip install torch --index-url https://download.pytorch.org/whl/cu128 || goto failed
echo  Installing the cutout and background tools ...
"%PY%" -m pip install "rembg[gpu]" opencv-python-headless scipy || goto failed
"%PY%" -m pip install --no-deps simple-lama-inpainting==0.1.2 || goto failed

echo.
echo  Downloading the AI models (about 2.3 GB) and checking the graphics card ...
"%PY%" gpu_check.py
if errorlevel 3 (
  echo.
  echo  Trying the version of the cutout runtime built for CUDA 12 ...
  "%PY%" -m pip install "onnxruntime-gpu==1.22.0" || goto failed
  "%PY%" gpu_check.py
)
if errorlevel 3 (
  echo.
  echo  Trying DirectML, which works with any graphics card on Windows ...
  "%PY%" -m pip uninstall -y onnxruntime-gpu onnxruntime
  "%PY%" -m pip install onnxruntime-directml || goto failed
  "%PY%" gpu_check.py
)
if errorlevel 1 (
  echo.
  echo  The tools are installed, but the cutouts will run on the processor ^(slow^).
  echo  Send Claude a screenshot of this window.
) else (
  echo.
  echo  All set. Double-click "Make Chapters" to make chapters.
)
echo.
pause
exit /b 0

:failed
echo.
echo  Something went wrong above. Send Claude a screenshot of this window.
echo.
pause
exit /b 1
