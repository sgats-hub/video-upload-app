<#
.SYNOPSIS
设置Flask后端服务开机自动启动

.DESCRIPTION
此脚本用于创建Windows任务计划程序任务，使Flask后端服务在系统启动时自动运行
#>

# 任务名称
$taskName = "VideoApp Backend Service"

# 检查是否以管理员身份运行
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "请以管理员身份运行此脚本！"
    exit 1
}

# 创建启动脚本
$startScriptPath = "E:\video-upload-app\backend\start_backend_silent.bat"
$startScriptContent = @"
@echo off
cd /d E:\video-upload-app\backend
python app.py
"@

Write-Host "创建启动脚本: $startScriptPath"
Set-Content -Path $startScriptPath -Value $startScriptContent -Encoding UTF8

# 创建任务计划
Write-Host "创建任务计划: $taskName"

# 删除已存在的任务
schtasks /delete /tn $taskName /f 2>&1 | Out-Null

# 创建新任务
$taskResult = schtasks /create `
    /tn $taskName `
    /tr "`"$startScriptPath`"" `
    /sc onstart `
    /ru SYSTEM `
    /rl highest `
    /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "任务计划创建成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "任务名称: $taskName"
    Write-Host "触发条件: 系统启动时"
    Write-Host "运行用户: SYSTEM"
    Write-Host "启动脚本: $startScriptPath"
    Write-Host ""
    Write-Host "测试启动任务..."
    
    # 立即运行一次任务以测试
    schtasks /run /tn $taskName
    
    Start-Sleep -Seconds 3
    
    # 检查服务是否启动
    $pythonProcess = Get-Process python* -ErrorAction SilentlyContinue
    if ($pythonProcess) {
        Write-Host "服务启动成功！" -ForegroundColor Green
        Write-Host "进程ID: $($pythonProcess.Id)"
    } else {
        Write-Host "服务启动失败，请检查日志" -ForegroundColor Red
    }
} else {
    Write-Host "任务计划创建失败: $taskResult" -ForegroundColor Red
}
