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

set "PACKAGE_DIR=dist\surface_touch_shortcuts_%ARCH%_package"
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

copy "dist\surface_touch_shortcuts_%ARCH%.exe" "%PACKAGE_DIR%\" >nul
copy "touch_shortcuts_config.json" "%PACKAGE_DIR%\" >nul
copy "surface_touch_shortcuts_help.html" "%PACKAGE_DIR%\" >nul
copy "install_program_files.bat" "%PACKAGE_DIR%\" >nul
copy "run_as_admin_surface_touch_shortcuts.bat" "%PACKAGE_DIR%\" >nul
copy "uninstall_surface_touch_shortcuts.bat" "%PACKAGE_DIR%\" >nul

echo.
echo Build complete.
echo EXE location:
echo   dist\surface_touch_shortcuts_%ARCH%.exe
echo.
echo Installable package folder:
echo   %PACKAGE_DIR%
echo.
echo Run install_program_files.bat from that package folder to copy the EXE,
echo default config, and help file into Program Files.
pause
