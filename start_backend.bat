@echo off
chcp 65001 >nul
echo 正在启动Flask后端服务...

:: 设置Python路径，确保能找到用户安装的包
set PYTHONPATH=C:\Users\yanyu\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages;%PYTHONPATH%

:: 启动Flask服务
cd /d E:\video-upload-app\backend
python app.py

pause