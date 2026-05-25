@echo off
setlocal

set PYTHON=D:\miniconda3\envs\vibe-music\python.exe
set PYINSTALLER=D:\miniconda3\envs\vibe-music\Scripts\pyinstaller.exe
set PROJECT_DIR=%~dp0
set DIST_DIR=%PROJECT_DIR%dist\VibeMusic

echo ============================================
echo   VibeMusic - Windows Build Script
echo ============================================
echo.

echo [1/3] Cleaning previous build...
if exist "%PROJECT_DIR%dist" rmdir /s /q "%PROJECT_DIR%dist"
if exist "%PROJECT_DIR%build" rmdir /s /q "%PROJECT_DIR%build"

echo [2/3] Running PyInstaller...
cd /d "%PROJECT_DIR%"
"%PYINSTALLER%" VibeMusic.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller failed!
    pause
    exit /b 1
)

echo [3/3] Verifying output...
if not exist "%DIST_DIR%\VibeMusic.exe" (
    echo [ERROR] VibeMusic.exe not found!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build complete!
echo   Output: %DIST_DIR%
echo   Run: %DIST_DIR%\VibeMusic.exe
echo ============================================
echo.
echo NOTE: For QQ/Kuwo music source, Node.js is required.
echo       Download: https://nodejs.org/
echo.
pause
