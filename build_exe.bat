@echo off
setlocal

set "PY_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PY_CMD=py"

if not defined PY_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo Python not found. Install Python, then rerun this script.
    pause
    exit /b 1
)

set "ARCH=unknown"

if /I "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ARCH=arm64"
if /I "%PROCESSOR_ARCHITECTURE%"=="AMD64" set "ARCH=x64"

if /I "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "ARCH=arm64"
if /I "%PROCESSOR_ARCHITEW6432%"=="AMD64" set "ARCH=x64"

echo Detected build architecture: %ARCH%
echo Using Python command: %PY_CMD%

echo Installing/upgrading build dependencies...
%PY_CMD% -m pip --version >nul 2>nul
if errorlevel 1 (
    echo WARNING: pip is not available in this environment. Skipping dependency installation.
) else (
    %PY_CMD% -m pip install --upgrade pip
    if errorlevel 1 (
        echo Failed to upgrade pip.
        pause
        exit /b 1
    )
    %PY_CMD% -m pip install pyinstaller keyboard pystray pillow
    if errorlevel 1 (
        echo Failed to install build dependencies.
        pause
        exit /b 1
    )
)

echo Building standalone EXE...
%PY_CMD% -m PyInstaller --noconsole --onefile --name surface_touch_shortcuts_%ARCH% surface_shortcuts_panel.py
if errorlevel 1 (
    echo PyInstaller build failed.
    pause
    exit /b 1
)

set "PACKAGE_DIR=dist\surface_touch_shortcuts_%ARCH%_package"

REM Archive existing package if present
if exist "%PACKAGE_DIR%" (
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value ^| find "="') do set "DT=%%I"
    set "TIMESTAMP=%DT:~0,8%_%DT:~8,6%"
    set "ARCHIVE_DIR=%PACKAGE_DIR%_%TIMESTAMP%"
    echo Archiving existing package to %ARCHIVE_DIR%...
    move "%PACKAGE_DIR%" "%ARCHIVE_DIR%" >nul
    if errorlevel 1 (
        echo Failed to archive existing package.
        pause
        exit /b 1
    )
)

mkdir "%PACKAGE_DIR%"
if errorlevel 1 (
    echo Failed to create package directory: %PACKAGE_DIR%
    pause
    exit /b 1
)

copy "dist\surface_touch_shortcuts_%ARCH%.exe" "%PACKAGE_DIR%\" >nul
if errorlevel 1 (
    echo Failed to copy EXE into package directory.
    pause
    exit /b 1
)
copy "touch_shortcuts_config.json" "%PACKAGE_DIR%\" >nul
if errorlevel 1 (
    echo Failed to copy touch_shortcuts_config.json.
    pause
    exit /b 1
)
copy "surface_touch_shortcuts_help.html" "%PACKAGE_DIR%\" >nul
if errorlevel 1 (
    echo Failed to copy surface_touch_shortcuts_help.html.
    pause
    exit /b 1
)
if exist "images" (
    mkdir "%PACKAGE_DIR%\images" >nul 2>nul
    xcopy "images\*.*" "%PACKAGE_DIR%\images\" /E /Y >nul
    if errorlevel 1 (
        echo Failed to copy images folder.
        pause
        exit /b 1
    )
)
copy "install_program_files.bat" "%PACKAGE_DIR%\" >nul
if errorlevel 1 (
    echo Failed to copy install_program_files.bat.
    pause
    exit /b 1
)
copy "run_as_admin_surface_touch_shortcuts.bat" "%PACKAGE_DIR%\" >nul
if errorlevel 1 (
    echo Failed to copy run_as_admin_surface_touch_shortcuts.bat.
    pause
    exit /b 1
)
copy "uninstall_surface_touch_shortcuts.bat" "%PACKAGE_DIR%\" >nul
if errorlevel 1 (
    echo Failed to copy uninstall_surface_touch_shortcuts.bat.
    pause
    exit /b 1
)

echo.
echo Build complete.
echo EXE location:
echo   dist\surface_touch_shortcuts_%ARCH%.exe
echo.
echo Installable package folder:
echo   %PACKAGE_DIR%
echo.
echo Run install_program_files.bat from that package folder to install.
pause