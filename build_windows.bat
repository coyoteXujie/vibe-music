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

echo [1/4] Cleaning previous build...
if exist "%PROJECT_DIR%dist" rmdir /s /q "%PROJECT_DIR%dist"
if exist "%PROJECT_DIR%build" rmdir /s /q "%PROJECT_DIR%build"

echo [2/4] Running PyInstaller...
cd /d "%PROJECT_DIR%"
"%PYINSTALLER%" VibeMusic.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller failed!
    pause
    exit /b 1
)

echo [3/4] Copying ncm-api...
xcopy "%PROJECT_DIR%ncm-api" "%DIST_DIR%\ncm-api\" /e /i /y /q

echo [4/4] Installing ncm-api dependencies...
cd /d "%DIST_DIR%\ncm-api"
call npm install --production 2>nul
if errorlevel 1 (
    echo [WARN] npm install failed. NCM API may not work.
    echo        You can manually run: cd ncm-api ^&^& npm install
)
cd /d "%PROJECT_DIR%"

echo.
echo ============================================
echo   Build complete!
echo   Output: %DIST_DIR%
echo   Run: %DIST_DIR%\VibeMusic.exe
echo ============================================
echo.
echo NOTE: This application requires Node.js
echo       to be installed for music search to work.
echo       Download: https://nodejs.org/
echo.
pause
