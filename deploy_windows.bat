@echo off
setlocal enabledelayedexpansion

:: Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    pause
    exit /b 1
)

:: Set project path
set "PROJECT_PATH=E:\video-upload-app"
echo Project Path: %PROJECT_PATH%
echo.

:: 1. Check Python
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo      OK: Python installed
echo.

:: 2. Install Python dependencies
echo [2/5] Installing Python dependencies...
cd /d "%PROJECT_PATH%\backend"
pip install flask flask-sqlalchemy flask-cors werkzeug ffmpeg-python -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo      OK: Python dependencies installed
echo.

:: 3. Check ffmpeg
echo [3/5] Checking ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: ffmpeg not installed - video compression will be disabled
    echo Download from: https://ffmpeg.org/download.html
) else (
    echo      OK: ffmpeg installed
)
echo.

:: 4. Create directories
echo [4/5] Creating directories...
if not exist "%PROJECT_PATH%\backend\uploads" mkdir "%PROJECT_PATH%\backend\uploads"
if not exist "%PROJECT_PATH%\backend\instance" mkdir "%PROJECT_PATH%\backend\instance"
if not exist "%PROJECT_PATH%\backend\logs" mkdir "%PROJECT_PATH%\backend\logs"
echo      OK: Directories created
echo.

:: 5. Configure firewall
echo [5/5] Configuring firewall rules...
netsh advfirewall firewall show rule name="VideoUploadApp-5000" >nul 2>&1
if %errorlevel% neq 0 (
    netsh advfirewall firewall add rule name="VideoUploadApp-5000" dir=in action=allow protocol=tcp localport=5000
    netsh advfirewall firewall add rule name="VideoUploadApp-80" dir=in action=allow protocol=tcp localport=80
    netsh advfirewall firewall add rule name="VideoUploadApp-443" dir=in action=allow protocol=tcp localport=443
    echo      OK: Firewall rules added
) else (
    echo      OK: Firewall rules exist
)
echo.

echo ============================
echo DEPLOYMENT PREPARATION DONE!
echo ============================
echo.
echo Next Steps:
echo 1. Install NSSM from https://nssm.cc/download
echo    Copy nssm.exe to C:\Windows\System32\
echo.
echo 2. Run: install_service.bat
echo.
echo 3. Configure Nginx:
echo    - Copy nginx_windows.conf to C:\nginx\conf\nginx.conf
echo    - Start Nginx: cd C:\nginx ^& start nginx
echo.
echo 4. Configure DNS: Point 2mintuevideos.com to your server IP
echo.
pause