@echo off
title Furry Persona Studio v2.4 Launcher
echo ====================================================
echo   FURRY PERSONA STUDIO v2.4 (Windows Launcher)
echo ====================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed or not in PATH.
    echo Opening the zero-install Web Edition in your browser instead...
    start "" "%~dp0web_edition\FurryPersonaStudio.html"
    pause
    exit /b 1
)
python "%~dp0src\furry_persona_studio.py"
pause
