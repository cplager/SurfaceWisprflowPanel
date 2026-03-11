@echo off
setlocal

set "INSTALL_DIR=%~dp0"
set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"
set "EXE_PATH="

for %%F in ("%INSTALL_DIR%\surface_touch_shortcuts_*.exe") do (
    set "EXE_PATH=%%~fF"
    goto found_exe
)

:found_exe
if not defined EXE_PATH (
    echo Could not find surface_touch_shortcuts_*.exe in:
    echo   %INSTALL_DIR%
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%EXE_PATH%' -WorkingDirectory '%INSTALL_DIR%' -Verb RunAs"
