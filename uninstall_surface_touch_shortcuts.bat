@echo off
setlocal

set "APP_NAME=Surface Touch Shortcuts"
set "INSTALL_DIR=%~dp0"
set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"
set "START_MENU_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "UNINSTALL_KEY=HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%"

net session >nul 2>nul
if errorlevel 1 (
    echo Requesting administrator permission to uninstall from Program Files...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b 0
)

echo This will remove %APP_NAME% from:
echo   %INSTALL_DIR%
echo.
choice /M "Continue"
if errorlevel 2 exit /b 0

if exist "%START_MENU_DIR%" rmdir /s /q "%START_MENU_DIR%"
reg delete "%UNINSTALL_KEY%" /f >nul 2>nul

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Start-Sleep -Milliseconds 300; " ^
  "$path = '%INSTALL_DIR%'; " ^
  "Get-Process | Where-Object { $_.Path -like ($path + '\*') } | Stop-Process -Force -ErrorAction SilentlyContinue"

ping 127.0.0.1 -n 2 >nul

set "CLEANUP_CMD=ping 127.0.0.1 -n 3 ^>nul ^& attrib -r \"%INSTALL_DIR%\*\" /s /d ^>nul 2^>nul ^& del /f /q \"%INSTALL_DIR%\*\" ^>nul 2^>nul ^& for /d %%%%D in (\"%INSTALL_DIR%\*\") do rmdir /s /q \"%%%%~fD\" ^& rmdir /s /q \"%INSTALL_DIR%\""
start "" cmd /c "%CLEANUP_CMD%"

echo.
echo Uninstall started. The install folder will be removed in a moment.
pause
