@echo off
echo 正在重启Nginx...
taskkill /f /im nginx.exe >nul 2>&1
cd C:\nginx
start nginx
echo Nginx已重启
timeout /t 2 /nobreak >nul
echo 测试API连接...
curl -X POST http://localhost:8088/api/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\",\"role\":\"admin\"}"
pause