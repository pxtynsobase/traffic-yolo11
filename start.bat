@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_CMD=py -3"
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 goto found
set "BUNDLED=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%BUNDLED%" goto error
set PYTHON_CMD="%BUNDLED%"
:found
if not exist .runtime-tmp mkdir .runtime-tmp
set "TEMP=%CD%\.runtime-tmp"
set "TMP=%TEMP%"
set "PYTHONPATH=%CD%\.packages;%PYTHONPATH%"
if exist .packages\setup.ok goto run
%PYTHON_CMD% -m pip install --target .packages -r requirements-lock.txt
if errorlevel 1 goto error
echo installed>.packages\setup.ok
:run
echo Open http://127.0.0.1:8050 in your browser
%PYTHON_CMD% app.py
pause
exit /b
:error
echo Setup failed. Install Python 3.11 or 3.12 and try again.
pause
