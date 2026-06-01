@echo off
chcp 65001 >nul
echo ========================================
echo    视频上传系统 - 停止所有服务
echo ========================================
echo.

echo 停止前端服务...
taskkill /FI "WINDOWTITLE eq Video Upload Frontend*" /F >nul 2>&1
echo       √ 前端服务已停止
echo.

echo 停止后端服务...
taskkill /FI "WINDOWTITLE eq Video Upload Backend*" /F >nul 2>&1
echo       √ 后端服务已停止
echo.

echo ========================================
echo           所有服务已停止
echo ========================================
echo.
pause
