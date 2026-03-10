@echo off
setlocal

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher not found. Install Python, then rerun this script.
    pause
    exit /b 1
)

set "ARCH=unknown"

if /I "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ARCH=arm64"
if /I "%PROCESSOR_ARCHITECTURE%"=="AMD64" set "ARCH=x64"

if /I "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "ARCH=arm64"
if /I "%PROCESSOR_ARCHITEW6432%"=="AMD64" set "ARCH=x64"

echo Detected build architecture: %ARCH%

echo Installing/upgrading build dependencies...
py -m pip install --upgrade pip
py -m pip install pyinstaller keyboard pystray pillow

echo Building standalone EXE...
py -m PyInstaller --noconsole --onefile --name surface_touch_shortcuts_%ARCH% surface_shortcuts_panel.py

echo.
echo Build complete.
echo EXE location:
echo   dist\surface_touch_shortcuts_%ARCH%.exe
echo.
echo Copy touch_shortcuts_config.json into the same folder as the EXE.
pause
