@echo off
setlocal

set "APP_NAME=Surface Touch Shortcuts"
set "PUBLISHER=Surface Touch Shortcuts"
set "INSTALL_DIR=%ProgramFiles%\%APP_NAME%"
set "START_MENU_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "UNINSTALL_KEY=HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "EXE_PATH="
for %%F in ("%SCRIPT_DIR%\surface_touch_shortcuts_*.exe") do (
    set "EXE_PATH=%%~fF"
    goto found_exe
)

:found_exe
if not defined EXE_PATH (
    echo Could not find surface_touch_shortcuts_*.exe next to this installer.
    echo Build first with build_exe.bat, then run this installer from the package folder.
    pause
    exit /b 1
)

for %%F in ("%EXE_PATH%") do (
    set "EXE_NAME=%%~nxF"
    set "EXE_BASE=%%~nF"
)

if not exist "%SCRIPT_DIR%\touch_shortcuts_config.json" (
    echo Missing touch_shortcuts_config.json next to this installer.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%\surface_touch_shortcuts_help.html" (
    echo Missing surface_touch_shortcuts_help.html next to this installer.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%\uninstall_surface_touch_shortcuts.bat" (
    echo Missing uninstall_surface_touch_shortcuts.bat next to this installer.
    pause
    exit /b 1
)

net session >nul 2>nul
if errorlevel 1 (
    echo Requesting administrator permission to install into Program Files...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b 0
)

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%START_MENU_DIR%" mkdir "%START_MENU_DIR%"

copy "%EXE_PATH%" "%INSTALL_DIR%\" /Y >nul
copy "%SCRIPT_DIR%\touch_shortcuts_config.json" "%INSTALL_DIR%\" /Y >nul
copy "%SCRIPT_DIR%\surface_touch_shortcuts_help.html" "%INSTALL_DIR%\" /Y >nul
copy "%SCRIPT_DIR%\uninstall_surface_touch_shortcuts.bat" "%INSTALL_DIR%\" /Y >nul

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
  "$u = $ws.CreateShortcut('%START_MENU_DIR%\Uninstall %APP_NAME%.lnk'); " ^
  "$u.TargetPath = '%INSTALL_DIR%\uninstall_surface_touch_shortcuts.bat'; " ^
  "$u.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$u.IconLocation = '%SystemRoot%\System32\SHELL32.dll,131'; " ^
  "$u.Save()"

reg add "%UNINSTALL_KEY%" /v "DisplayName" /t REG_SZ /d "%APP_NAME%" /f >nul
reg add "%UNINSTALL_KEY%" /v "Publisher" /t REG_SZ /d "%PUBLISHER%" /f >nul
reg add "%UNINSTALL_KEY%" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "%UNINSTALL_KEY%" /v "DisplayIcon" /t REG_SZ /d "%INSTALL_DIR%\%EXE_NAME%" /f >nul
reg add "%UNINSTALL_KEY%" /v "UninstallString" /t REG_SZ /d "%INSTALL_DIR%\uninstall_surface_touch_shortcuts.bat" /f >nul
reg add "%UNINSTALL_KEY%" /v "DisplayVersion" /t REG_SZ /d "1.0" /f >nul
reg add "%UNINSTALL_KEY%" /v "NoModify" /t REG_DWORD /d 1 /f >nul
reg add "%UNINSTALL_KEY%" /v "NoRepair" /t REG_DWORD /d 1 /f >nul

echo.
echo Installed to:
echo   %INSTALL_DIR%
echo.
echo Start Menu folder:
echo   %START_MENU_DIR%
echo.
echo Files:
echo   %EXE_NAME%
echo   touch_shortcuts_config.json
echo   surface_touch_shortcuts_help.html
echo   uninstall_surface_touch_shortcuts.bat
echo.
echo Installed Apps entry created for:
echo   %APP_NAME%
pause
