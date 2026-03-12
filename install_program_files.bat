@echo off
setlocal

set "APP_NAME=Surface Touch Shortcuts"
set "PUBLISHER=Surface Touch Shortcuts"
set "INSTALL_DIR=%ProgramFiles%\%APP_NAME%"
set "START_MENU_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "UNINSTALL_KEY=HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "SOURCE_DIR=%SCRIPT_DIR%"

REM First try: EXE in the same directory as this script
set "EXE_PATH="
for %%F in ("%SOURCE_DIR%\surface_touch_shortcuts_*.exe") do (
    set "EXE_PATH=%%~fF"
    goto found_exe
)

REM Second try: look in dist package folders (most recent first)
for /f "delims=" %%D in ('dir /b /ad /o-d "%SCRIPT_DIR%\dist\surface_touch_shortcuts_*_package" 2^>nul') do (
    for %%F in ("%SCRIPT_DIR%\dist\%%D\surface_touch_shortcuts_*.exe") do (
        set "SOURCE_DIR=%SCRIPT_DIR%\dist\%%D"
        set "EXE_PATH=%%~fF"
        goto found_exe
    )
)

:found_exe
if not defined EXE_PATH (
    echo Could not find surface_touch_shortcuts_*.exe
    echo.
    echo Searched in:
    echo   %SCRIPT_DIR%
    echo   %SCRIPT_DIR%\dist\surface_touch_shortcuts_*_package
    echo.
    echo Run build_exe.bat first.
    pause
    exit /b 1
)

for %%F in ("%EXE_PATH%") do (
    set "EXE_NAME=%%~nxF"
)

echo Found: %EXE_NAME%
echo Source: %SOURCE_DIR%
echo.

REM Check required files
if not exist "%SOURCE_DIR%\touch_shortcuts_config.json" (
    echo Missing touch_shortcuts_config.json
    pause
    exit /b 1
)
if not exist "%SOURCE_DIR%\surface_touch_shortcuts_help.html" (
    echo Missing surface_touch_shortcuts_help.html
    pause
    exit /b 1
)
if not exist "%SOURCE_DIR%\uninstall_surface_touch_shortcuts.bat" (
    echo Missing uninstall_surface_touch_shortcuts.bat
    pause
    exit /b 1
)
if not exist "%SOURCE_DIR%\run_as_admin_surface_touch_shortcuts.bat" (
    echo Missing run_as_admin_surface_touch_shortcuts.bat
    pause
    exit /b 1
)

REM Request admin if needed
net session >nul 2>nul
if errorlevel 1 (
    echo Requesting administrator permission...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b 0
)

REM Create directories
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%START_MENU_DIR%" mkdir "%START_MENU_DIR%"

REM Stop running instances
tasklist /FI "IMAGENAME eq %EXE_NAME%" 2>nul | find /I "%EXE_NAME%" >nul
if not errorlevel 1 (
    echo Stopping running %EXE_NAME%...
    taskkill /IM "%EXE_NAME%" /F >nul 2>nul
)

REM Copy files
echo Copying files to %INSTALL_DIR%...

copy "%EXE_PATH%" "%INSTALL_DIR%\" /Y >nul
if errorlevel 1 (
    echo Failed to copy %EXE_NAME%
    pause
    exit /b 1
)

copy "%SOURCE_DIR%\touch_shortcuts_config.json" "%INSTALL_DIR%\" /Y >nul
if errorlevel 1 (
    echo Failed to copy touch_shortcuts_config.json
    pause
    exit /b 1
)

copy "%SOURCE_DIR%\surface_touch_shortcuts_help.html" "%INSTALL_DIR%\" /Y >nul
if errorlevel 1 (
    echo Failed to copy surface_touch_shortcuts_help.html
    pause
    exit /b 1
)

if exist "%SOURCE_DIR%\images" (
    if not exist "%INSTALL_DIR%\images" mkdir "%INSTALL_DIR%\images"
    xcopy "%SOURCE_DIR%\images\*.*" "%INSTALL_DIR%\images\" /E /Y >nul
    if errorlevel 1 (
        echo Failed to copy images folder
        pause
        exit /b 1
    )
)

copy "%SOURCE_DIR%\uninstall_surface_touch_shortcuts.bat" "%INSTALL_DIR%\" /Y >nul
if errorlevel 1 (
    echo Failed to copy uninstall_surface_touch_shortcuts.bat
    pause
    exit /b 1
)

copy "%SOURCE_DIR%\run_as_admin_surface_touch_shortcuts.bat" "%INSTALL_DIR%\" /Y >nul
if errorlevel 1 (
    echo Failed to copy run_as_admin_surface_touch_shortcuts.bat
    pause
    exit /b 1
)

REM Create Start Menu shortcuts
echo Creating Start Menu shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut('%START_MENU_DIR%\%APP_NAME%.lnk'); " ^
  "$s.TargetPath = '%INSTALL_DIR%\%EXE_NAME%'; " ^
  "$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s.IconLocation = '%INSTALL_DIR%\%EXE_NAME%,0'; " ^
  "$s.Save(); " ^
  "$h = $ws.CreateShortcut('%START_MENU_DIR%\%APP_NAME% Help.lnk'); " ^
  "$h.TargetPath = '%INSTALL_DIR%\surface_touch_shortcuts_help.html'; " ^
  "$h.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$h.IconLocation = '%SystemRoot%\System32\SHELL32.dll,23'; " ^
  "$h.Save(); " ^
  "$a = $ws.CreateShortcut('%START_MENU_DIR%\%APP_NAME% (Admin).lnk'); " ^
  "$a.TargetPath = '%INSTALL_DIR%\run_as_admin_surface_touch_shortcuts.bat'; " ^
  "$a.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$a.IconLocation = '%SystemRoot%\System32\SHELL32.dll,77'; " ^
  "$a.Save(); " ^
  "$u = $ws.CreateShortcut('%START_MENU_DIR%\Uninstall %APP_NAME%.lnk'); " ^
  "$u.TargetPath = '%INSTALL_DIR%\uninstall_surface_touch_shortcuts.bat'; " ^
  "$u.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$u.IconLocation = '%SystemRoot%\System32\SHELL32.dll,131'; " ^
  "$u.Save()"

REM Add to Programs and Features
echo Adding to Programs and Features...
reg add "%UNINSTALL_KEY%" /v "DisplayName" /t REG_SZ /d "%APP_NAME%" /f >nul
reg add "%UNINSTALL_KEY%" /v "Publisher" /t REG_SZ /d "%PUBLISHER%" /f >nul
reg add "%UNINSTALL_KEY%" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "%UNINSTALL_KEY%" /v "DisplayIcon" /t REG_SZ /d "%INSTALL_DIR%\%EXE_NAME%" /f >nul
reg add "%UNINSTALL_KEY%" /v "UninstallString" /t REG_SZ /d "%INSTALL_DIR%\uninstall_surface_touch_shortcuts.bat" /f >nul
reg add "%UNINSTALL_KEY%" /v "DisplayVersion" /t REG_SZ /d "1.0" /f >nul
reg add "%UNINSTALL_KEY%" /v "NoModify" /t REG_DWORD /d 1 /f >nul
reg add "%UNINSTALL_KEY%" /v "NoRepair" /t REG_DWORD /d 1 /f >nul

echo.
echo Installation complete!
echo.
echo Installed to: %INSTALL_DIR%
echo Start Menu:   %START_MENU_DIR%
echo.
pause
