@echo off
echo ============================================
echo   氛围音乐 // 像素终端 - 启动中...
echo ============================================
echo.

echo [1/2] 启动 NCM 音乐API...
start /b "" D:\nodejs\node.exe "%~dp0ncm-api\server.js"
timeout /t 5 /nobreak >nul

echo [2/2] 启动主应用...
D:\miniconda3\envs\vibe-music\python.exe "%~dp0app.py"
