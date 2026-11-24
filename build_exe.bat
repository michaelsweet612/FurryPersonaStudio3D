@echo off
title Build FurryPersonaStudio.exe
echo ============================================================
echo   Building Standalone FurryPersonaStudio.exe via PyInstaller
echo ============================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.9+ is required to compile the Windows .exe.
    echo Download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing PyInstaller (if not already installed)...
python -m pip install --upgrade pyinstaller

echo [2/3] Compiling FurryPersonaStudio.exe with all 15 audio clips, icons, and presets...
python -m PyInstaller --noconfirm build_exe.spec

echo [3/3] Done! Look inside dist\FurryPersonaStudio.exe
if exist "dist\FurryPersonaStudio.exe" (
    echo SUCCESS: dist\FurryPersonaStudio.exe is ready to run!
) else (
    echo Build finished with warnings. Check output above.
)
pause
