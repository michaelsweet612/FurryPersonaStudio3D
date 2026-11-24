@echo off
setlocal enabledelayedexpansion
title Required Programs Checker & Auto-Installer — Furry Persona Studio 3D v3.0
echo ========================================================================
echo   FURRY PERSONA STUDIO 3D v3.0 — AUTOMATIC REQUIRED PROGRAMS CHECKER
echo ========================================================================
echo.

:: Step 1: Check Python 3
echo [1/4] Checking for Python 3...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python 3 was NOT found on this PC.
    echo [*] Attempting automatic installation via Windows Package Manager ^(winget^)...
    winget --version >nul 2>&1
    if not errorlevel 1 (
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        echo [*] Please close and re-run this script after Python finishes installing so PATH refreshes.
        pause
        exit /b 0
    ) else (
        echo [!] winget is unavailable. Opening the official Python download page...
        start "" "https://www.python.org/downloads/"
        echo [*] Install Python 3 ^(check "Add Python to PATH"^), then re-run this script.
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%v in ('python --version') do echo [OK] Found %%v
)

:: Step 2: Check pip & install PyInstaller + Pillow
echo.
echo [2/4] Checking required Python packages ^(pyinstaller, pillow^)...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [*] Bootstrapping pip...
    python -m ensurepip --upgrade
)
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing PyInstaller...
    python -m pip install --upgrade pyinstaller
) else (
    echo [OK] PyInstaller is installed.
)
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing Pillow...
    python -m pip install --upgrade pillow
) else (
    echo [OK] Pillow is installed.
)

:: Step 3: Build the standalone Windows EXE automatically if missing
echo.
echo [3/4] Checking for compiled FurryPersonaStudio3D.exe...
cd /d "%~dp0.."
if not exist "dist\FurryPersonaStudio3D.exe" (
    echo [*] Building standalone FurryPersonaStudio3D.exe automatically...
    python -m PyInstaller --noconfirm build_exe.spec
) else (
    echo [OK] FurryPersonaStudio3D.exe is already built!
)

:: Step 4: Launch!
echo.
echo [4/4] All required programs verified! Launching Furry Persona Studio 3D...
if exist "dist\FurryPersonaStudio3D.exe" (
    start "" "dist\FurryPersonaStudio3D.exe"
) else (
    python "src\furry_persona_studio.py"
)
echo Done!
timeout /t 3 >nul
exit /b 0
