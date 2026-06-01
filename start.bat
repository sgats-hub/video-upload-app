@echo off

:: 1. 尝试静默清理可能残留的旧 Python 后端进程（隐藏找不到进程时的报错）
taskkill /f /im python.exe >nul 2>&1

:: 2. 切进后端绝对路径并静默启动 Python 服务
cd /d "E:\video-upload-app\backend"
start /b python app.py

echo ========================================
echo PYTHON BACKEND DAEMON STARTED (PORT 5000)
echo ========================================
timeout /t 3