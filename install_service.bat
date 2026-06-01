@echo off
setlocal enabledelayedexpansion

echo ============================
echo Video Upload App Service Installer
echo ============================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    pause
    exit /b 1
)

:: Check NSSM
set "NSSM_PATH=C:\Windows\System32\nssm.exe"
if not exist "%NSSM_PATH%" (
    echo ERROR: NSSM not found at %NSSM_PATH%
    pause
    exit /b 1
)
echo OK: NSSM found at %NSSM_PATH%

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH!
    pause
    exit /b 1
)
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo OK: Python %PYTHON_VERSION% found

:: Set paths
set "PROJECT_PATH=E:\video-upload-app"
set "BACKEND_PATH=%PROJECT_PATH%\backend"

:: Check project directory
if not exist "%BACKEND_PATH%" (
    echo ERROR: Backend directory not found: %BACKEND_PATH%
    pause
    exit /b 1
)
echo OK: Backend directory exists: %BACKEND_PATH%

:: Check app.py
if not exist "%BACKEND_PATH%\app.py" (
    echo ERROR: app.py not found in backend directory!
    pause
    exit /b 1
)
echo OK: app.py exists

:: Remove existing service
echo.
echo Checking for existing service...
sc query VideoUploadApp >nul 2>&1
if %errorlevel% equ 0 (
    echo Stopping existing service...
    "%NSSM_PATH%" stop VideoUploadApp >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo Removing existing service...
    "%NSSM_PATH%" remove VideoUploadApp confirm >nul 2>&1
    timeout /t 2 /nobreak >nul
)

:: Create logs directory
if not exist "%BACKEND_PATH%\logs" mkdir "%BACKEND_PATH%\logs"

:: Install service
echo.
echo Installing service...
"%NSSM_PATH%" install VideoUploadApp python app.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to install service!
    pause
    exit /b 1
)

:: Configure service
echo Configuring service...
"%NSSM_PATH%" set VideoUploadApp AppDirectory "%BACKEND_PATH%"
"%NSSM_PATH%" set VideoUploadApp DisplayName "Video Upload Application"
"%NSSM_PATH%" set VideoUploadApp Description "Video Upload System Backend"
"%NSSM_PATH%" set VideoUploadApp Start SERVICE_AUTO_START
"%NSSM_PATH%" set VideoUploadApp AppStdout "%BACKEND_PATH%\logs\stdout.log"
"%NSSM_PATH%" set VideoUploadApp AppStderr "%BACKEND_PATH%\logs\stderr.log"
"%NSSM_PATH%" set VideoUploadApp AppNoConsole 1

:: Start service
echo.
echo Starting service...
"%NSSM_PATH%" start VideoUploadApp

:: Check status
timeout /t 3 /nobreak >nul
sc query VideoUploadApp | findstr /i "STATE"

if %errorlevel% equ 0 (
    echo.
    echo ============================
    echo SERVICE INSTALLATION SUCCESS!
    echo ============================
    echo.
    echo Service Name: VideoUploadApp
    echo Backend URL: http://localhost:5000
    echo Log Directory: %BACKEND_PATH%\logs
    echo.
    echo Management Commands:
    echo   Start:     nssm start VideoUploadApp
    echo   Stop:      nssm stop VideoUploadApp
    echo   Restart:   nssm restart VideoUploadApp
    echo   Remove:    nssm remove VideoUploadApp confirm
    echo.
) else (
    echo.
    echo ERROR: Service failed to start!
    echo.
    echo Please check the log files:
    echo   %BACKEND_PATH%\logs\stdout.log
    echo   %BACKEND_PATH%\logs\stderr.log
    echo.
    echo Or try running manually:
    echo   cd %BACKEND_PATH%
    echo   python app.py
    echo.
)

pause