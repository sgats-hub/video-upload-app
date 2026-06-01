@echo off
chcp 65001 >nul
echo ============================================
echo    Let's Encrypt SSL 证书安装脚本
echo ============================================
echo.

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: 请以管理员身份运行此脚本！
    pause
    exit /b 1
)

:: 步骤1: 安装 Chocolatey
echo [1/4] 检查并安装 Chocolatey...
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo       正在安装 Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if %errorlevel% neq 0 (
        echo ERROR: Chocolatey 安装失败！
        pause
        exit /b 1
    )
    echo       Chocolatey 安装成功
) else (
    echo       Chocolatey 已安装
)
echo.

:: 步骤2: 安装 Certbot
echo [2/4] 检查并安装 Certbot...
where certbot >nul 2>&1
if %errorlevel% neq 0 (
    echo       正在安装 Certbot...
    choco install certbot -y
    if %errorlevel% neq 0 (
        echo ERROR: Certbot 安装失败！
        pause
        exit /b 1
    )
    echo       Certbot 安装成功
) else (
    echo       Certbot 已安装
)
echo.

:: 步骤3: 创建验证目录
echo [3/4] 创建证书验证目录...
mkdir "E:\video-upload-app\dist\.well-known" >nul 2>&1
echo       验证目录已创建
echo.

:: 步骤4: 获取证书
echo [4/4] 获取 SSL 证书...
echo       请确保域名 2minutevideos.com 和 www.2minutevideos.com 已解析到本服务器
echo.
pause
certbot certonly --webroot -w "E:\video-upload-app\dist" -d 2minutevideos.com -d www.2minutevideos.com

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo              证书获取成功！
    echo ============================================
    echo.
    echo 证书路径: C:\Certbot\live\2minutevideos.com\
    echo   - fullchain.pem (完整证书链)
    echo   - privkey.pem   (私钥)
    echo.
    echo 请重启 Nginx 使配置生效：
    echo   cd C:\nginx
    echo   nginx -s reload
    echo.
    echo 证书有效期: 90天
    echo 自动续期命令: certbot renew
) else (
    echo.
    echo ERROR: 证书获取失败！
    echo 请检查：
    echo   1. 域名是否已正确解析到本服务器
    echo   2. 端口 80 是否开放
    echo   3. 验证目录是否可访问
)

pause